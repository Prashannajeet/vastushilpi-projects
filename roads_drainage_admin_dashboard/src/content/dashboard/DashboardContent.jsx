import React from "react";
import {
  DataComponent,
  DataTable,
  EvidenceChart,
  MetricCard,
  Section,
  SectionHeader,
  useDataApp,
  useDashboardTabs,
} from "../../data-app-public.jsx";
import "./example.css";

const STORAGE_KEY = "roadsDrainageSurveyRecordsV1";
const QUERY_ID = "field_records";
const RECORDS_API = "/api/field-survey/roads-drainage/records";
const CONDITIONS = ["Good", "Fair", "Poor", "Critical"];
const CATEGORY_COLORS = { Road: "#ffb020", "Stormwater Drainage": "#00bfa6" };
const VECTOR_BASE = window.location.pathname.startsWith("/admin/")
  ? "/workspace/field-survey/roads-drainage/data/"
  : "/roads_drainage_geotagging/data/";

function readDeviceRecords() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return { rows: Array.isArray(parsed) ? parsed : [], error: "" };
  } catch (error) {
    return { rows: [], error: error instanceof Error ? error.message : "The device records could not be read." };
  }
}

function countPhotos(record) {
  const storedCount = Number(record.photoCount);
  if (Number.isFinite(storedCount)) return storedCount;
  return Array.isArray(record.photos) ? record.photos.filter(Boolean).length : 0;
}

function recordDate(record) {
  return record.surveyDate || String(record.deviceTimestamp || record.createdAt || "").slice(0, 10);
}

function groupCount(rows, field, emptyLabel = "Not specified") {
  const counts = new Map();
  rows.forEach((row) => {
    const value = String(row[field] || emptyLabel);
    counts.set(value, (counts.get(value) || 0) + 1);
  });
  return [...counts].map(([label, count]) => ({ label, count })).sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
}

function csvCell(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function downloadCsv(rows) {
  const fields = ["assetCode", "project", "zone", "surveyor", "surveyDate", "surveyTime", "category", "assetType", "assetName", "condition", "issue", "latitude", "longitude", "gpsAccuracy", "gpsSampleCount", "photoCount", "deviceTimestamp"];
  const body = rows.map((row) => fields.map((field) => csvCell(field === "photoCount" ? countPhotos(row) : row[field])).join(","));
  const blob = new Blob([[fields.join(","), ...body].join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "nita-geoai-filtered-field-records.csv";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function qualityFlags(record) {
  const flags = [];
  const accuracy = Number(record.gpsAccuracy);
  if (!Number.isFinite(accuracy)) flags.push("GPS accuracy missing");
  else if (accuracy > 25) flags.push(`Low GPS accuracy (${Math.round(accuracy)} m)`);
  if (countPhotos(record) < 1) flags.push("Photo 1 missing");
  if (!Number.isFinite(Number(record.latitude)) || !Number.isFinite(Number(record.longitude))) flags.push("Coordinates missing");
  if (!record.deviceTimestamp) flags.push("Device timestamp missing");
  return flags;
}

function uniqueValues(rows, field) {
  return [...new Set(rows.map((row) => String(row[field] || "")).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function FilterSelect({ label, value, options, onChange }) {
  return <label className="admin-filter">
    <span>{label}</span>
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      <option value="all">All</option>
      {options.map((option) => <option value={option} key={option}>{option}</option>)}
    </select>
  </label>;
}

function geometryLines(geometry) {
  if (!geometry) return [];
  if (geometry.type === "LineString") return [geometry.coordinates];
  if (geometry.type === "MultiLineString" || geometry.type === "Polygon") return geometry.coordinates;
  if (geometry.type === "MultiPolygon") return geometry.coordinates.flat();
  return [];
}

function MandideepSpatialView({ rows }) {
  const [vectors, setVectors] = React.useState(/** @type {any[]} */ ([]));
  const [status, setStatus] = React.useState("Loading Mandideep reference layers…");

  React.useEffect(() => {
    let cancelled = false;
    const sources = [
      ["aoi", "mandideep_aoi_wgs84.geojson"],
      ["roads", "mandideep_osm_roads_buffer100m_wgs84.geojson"],
      ["waterways", "mandideep_osm_waterways_wgs84.geojson"],
    ];
    Promise.all(sources.map(async ([key, file]) => {
      const response = await fetch(VECTOR_BASE + file);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return { key, data: await response.json() };
    })).then((loaded) => {
      if (!cancelled) { setVectors(loaded); setStatus("Mandideep AOI, roads and waterways"); }
    }).catch(() => {
      if (!cancelled) setStatus("Reference layers unavailable; field points remain visible.");
    });
    return () => { cancelled = true; };
  }, []);

  const lines = React.useMemo(() => vectors.flatMap(({ key, data }) => (data.features || []).flatMap((feature, featureIndex) =>
    geometryLines(feature.geometry).map((coordinates, lineIndex) => ({ key, id: `${key}-${featureIndex}-${lineIndex}`, coordinates })))), [vectors]);
  const referenceCoordinates = lines.flatMap((line) => line.coordinates);
  const pointCoordinates = rows.map((row) => [Number(row.longitude), Number(row.latitude)]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  const coordinates = referenceCoordinates.length ? referenceCoordinates : pointCoordinates;
  if (!coordinates.length) return <div className="spatial-empty">No mapped field records yet.<small>{status}</small></div>;
  const xs = coordinates.map(([x]) => Number(x)), ys = coordinates.map(([, y]) => Number(y));
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const padX = Math.max((maxX - minX) * .03, .001), padY = Math.max((maxY - minY) * .03, .001);
  const bounds = { minX:minX - padX, maxX:maxX + padX, minY:minY - padY, maxY:maxY + padY };
  const project = ([longitude, latitude]) => [
    ((Number(longitude) - bounds.minX) / (bounds.maxX - bounds.minX)) * 1000,
    520 - ((Number(latitude) - bounds.minY) / (bounds.maxY - bounds.minY)) * 520,
  ];
  const points = rows.map((record) => ({ record, point:project([record.longitude, record.latitude]) }))
    .filter(({ point }) => point.every(Number.isFinite));

  return <div className="spatial-view">
    <svg viewBox="0 0 1000 520" role="img" aria-label="Filtered survey records across the Mandideep reference network">
      <rect width="1000" height="520" className="spatial-background" />
      {lines.map((line) => {
        const projected = line.coordinates.map(project).filter((point) => point.every(Number.isFinite));
        if (projected.length < 2) return null;
        const pointsValue = projected.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
        return line.key === "aoi" ? <polygon key={line.id} points={pointsValue} className="spatial-aoi" />
          : <polyline key={line.id} points={pointsValue} className={`spatial-${line.key}`} />;
      })}
      {points.map(({ record, point }, index) => <circle key={record.id || index} cx={point[0]} cy={point[1]} r="7"
        className={`asset-point condition-${String(record.condition || "unknown").toLowerCase()}`}
        style={{ "--asset-color": CATEGORY_COLORS[record.category] || "#00d4ff" }}>
        <title>{`${record.assetCode || "Asset"} · ${record.assetType || record.category || "Unclassified"} · ${record.condition || "Unknown"}`}</title>
      </circle>)}
    </svg>
    <div className="spatial-caption"><span>{status}</span><span>{points.length} filtered assets</span></div>
  </div>;
}

export function DashboardContent() {
  useDashboardTabs([{ id: "administration", label: "Administration" }]);
  const { appTitle, setAppTitle } = useDataApp();
  const initial = React.useMemo(readDeviceRecords, []);
  const [records, setRecords] = React.useState(initial.rows);
  const [readError, setReadError] = React.useState(initial.error);
  const [recordSource, setRecordSource] = React.useState("Device cache");
  const [refreshedAt, setRefreshedAt] = React.useState(new Date());
  const [filters, setFilters] = React.useState({ category:"all", assetType:"all", condition:"all", zone:"all", surveyor:"all", from:"", to:"" });

  React.useEffect(() => { if (appTitle !== "Roads & Drainage Administration") setAppTitle("Roads & Drainage Administration"); }, [appTitle, setAppTitle]);

  async function refresh() {
    try {
      const response = await fetch(RECORDS_API, { credentials:"same-origin", cache:"no-store" });
      const body = await response.json().catch(() => ({}));
      if (!response.ok || !Array.isArray(body.records)) throw new Error(body.error || `Central records unavailable (${response.status}).`);
      setRecords(body.records);
      setReadError("");
      setRecordSource("Central NITA GeoAI database");
    } catch (error) {
      const fallback = readDeviceRecords();
      setRecords(fallback.rows);
      setReadError(fallback.error || "Central database unavailable; showing records stored in this browser.");
      setRecordSource("Device cache");
    } finally {
      setRefreshedAt(new Date());
    }
  }

  React.useEffect(() => { void refresh(); }, []);

  React.useEffect(() => {
    const handleStorage = (event) => { if (event.key === STORAGE_KEY) void refresh(); };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const filtered = React.useMemo(() => records.filter((record) => {
    const date = recordDate(record);
    return (filters.category === "all" || record.category === filters.category)
      && (filters.assetType === "all" || record.assetType === filters.assetType)
      && (filters.condition === "all" || record.condition === filters.condition)
      && (filters.zone === "all" || String(record.zone || "Not specified") === filters.zone)
      && (filters.surveyor === "all" || String(record.surveyor || "Not specified") === filters.surveyor)
      && (!filters.from || date >= filters.from) && (!filters.to || date <= filters.to);
  }), [records, filters]);

  const conditionRows = CONDITIONS.map((condition) => ({ condition, count:filtered.filter((row) => row.condition === condition).length }));
  const categoryRows = groupCount(filtered, "category").map((row) => ({ category:row.label, count:row.count }));
  const assetTypeRows = groupCount(filtered, "assetType").slice(0, 10).map((row) => ({ assetType:row.label, count:row.count }));
  const dailyRows = groupCount(filtered.map((row) => ({ surveyDate:recordDate(row) })), "surveyDate")
    .map((row) => ({ surveyDate:row.label, count:row.count })).sort((a, b) => a.surveyDate.localeCompare(b.surveyDate));
  const accuracyValues = filtered.map((row) => Number(row.gpsAccuracy)).filter(Number.isFinite);
  const averageAccuracy = accuracyValues.length ? accuracyValues.reduce((sum, value) => sum + value, 0) / accuracyValues.length : null;
  const attention = filtered.filter((row) => ["Poor", "Critical"].includes(row.condition));
  const critical = filtered.filter((row) => row.condition === "Critical");
  const completePhotos = filtered.filter((row) => countPhotos(row) === 3);
  const qualityRows = filtered.map((row) => ({ ...row, qualityIssue:qualityFlags(row).join("; ") })).filter((row) => row.qualityIssue);
  const registerRows = filtered.map((row) => ({ ...row, photoCount:countPhotos(row), gpsAccuracyDisplay:Number.isFinite(Number(row.gpsAccuracy)) ? `${Math.round(Number(row.gpsAccuracy))} m` : "Missing", surveyDate:recordDate(row) }));
  const selectedPeriod = filters.from || filters.to ? `${filters.from || "Start"}–${filters.to || "Latest"}` : "All dates";
  const setFilter = (field, value) => setFilters((current) => ({ ...current, [field]:value }));
  const resetFilters = () => setFilters({ category:"all", assetType:"all", condition:"all", zone:"all", surveyor:"all", from:"", to:"" });

  return <article className="admin-dashboard">
    <SectionHeader id="admin-title" title="Field asset operations" />
    <p className="admin-intro">Category analysis, inspection priorities and data-quality control for roads and stormwater drainage.</p>

    <div className="admin-filterbar" aria-label="Dashboard filters">
      <FilterSelect label="Infrastructure" value={filters.category} options={uniqueValues(records, "category")} onChange={(value) => setFilter("category", value)} />
      <FilterSelect label="Asset type" value={filters.assetType} options={uniqueValues(records, "assetType")} onChange={(value) => setFilter("assetType", value)} />
      <FilterSelect label="Condition" value={filters.condition} options={CONDITIONS} onChange={(value) => setFilter("condition", value)} />
      <FilterSelect label="Zone" value={filters.zone} options={uniqueValues(records.map((row) => ({ ...row, zone:row.zone || "Not specified" })), "zone")} onChange={(value) => setFilter("zone", value)} />
      <FilterSelect label="Surveyor" value={filters.surveyor} options={uniqueValues(records.map((row) => ({ ...row, surveyor:row.surveyor || "Not specified" })), "surveyor")} onChange={(value) => setFilter("surveyor", value)} />
      <label className="admin-filter"><span>From</span><input type="date" value={filters.from} onChange={(event) => setFilter("from", event.target.value)} /></label>
      <label className="admin-filter"><span>To</span><input type="date" value={filters.to} onChange={(event) => setFilter("to", event.target.value)} /></label>
      <div className="admin-filter-actions"><button type="button" onClick={resetFilters}>Reset</button><button type="button" className="accent" onClick={() => void refresh()}>Refresh records</button></div>
    </div>
    <div className="admin-scope"><span>{filtered.length} of {records.length} records · {selectedPeriod} · {recordSource}</span><span>Refreshed {refreshedAt.toLocaleTimeString()}</span></div>
    {readError && <div className="admin-error">{readError}</div>}

    <Section id="headline-metrics" kind="metrics" columns={3} spacing="none">
      <MetricCard id="total-records" queryId={QUERY_ID} title="Filtered assets" value={filtered.length} description="All survey records matching the current filters." periodLabel={selectedPeriod} sourceRows={filtered} />
      <MetricCard id="attention-records" queryId={QUERY_ID} title="Needs attention" value={attention.length} description="Assets assessed as Poor or Critical." periodLabel={selectedPeriod} sourceRows={filtered} />
      <MetricCard id="critical-records" queryId={QUERY_ID} title="Critical assets" value={critical.length} description="Assets assessed as Critical and requiring priority review." periodLabel={selectedPeriod} sourceRows={filtered} />
      <MetricCard id="gps-accuracy" queryId={QUERY_ID} title="Average GPS accuracy" value={averageAccuracy == null ? "—" : `${averageAccuracy.toFixed(1)} m`} description="Mean device-reported horizontal accuracy for filtered records; lower is better." periodLabel={selectedPeriod} sourceRows={filtered} />
      <MetricCard id="photo-completeness" queryId={QUERY_ID} title="Three-photo coverage" value={filtered.length ? `${Math.round(completePhotos.length / filtered.length * 100)}%` : "—"} description="Share of filtered records containing all three photograph slots." periodLabel={selectedPeriod} sourceRows={filtered} />
      <MetricCard id="quality-exceptions" queryId={QUERY_ID} title="Data-quality exceptions" value={qualityRows.length} description="Records with low or missing GPS accuracy, missing Photo 1, coordinates or device timestamp." periodLabel={selectedPeriod} sourceRows={filtered} />
    </Section>

    <Section id="spatial-analysis" title="Spatial coverage" spacing="after-metrics">
      <DataComponent id="mandideep-spatial-view" queryId={QUERY_ID} kind="chart" title="Filtered assets across Mandideep" description="Geographic plot using the Mandideep AOI, road and waterway reference vectors." sourceRows={filtered} displayRows={filtered} variant="card">
        <MandideepSpatialView rows={filtered} />
      </DataComponent>
    </Section>

    <Section id="category-analysis" title="Category and condition analysis" columns={2}>
      <EvidenceChart id="condition-analysis" queryId={QUERY_ID} title="Condition profile" description="Asset count by recorded condition." spec={{ type:"horizontalBar", x:"count", y:"condition", startAtZero:true }} rows={conditionRows} sourceRows={filtered} height={260} />
      <EvidenceChart id="category-composition" queryId={QUERY_ID} title="Infrastructure mix" description="Road and stormwater drainage records in the selected scope." spec={{ type:"bar", x:"category", y:"count", startAtZero:true }} rows={categoryRows} sourceRows={filtered} height={260} />
      <EvidenceChart id="asset-type-analysis" queryId={QUERY_ID} title="Leading asset types" description="Top ten asset types by record count." spec={{ type:"horizontalBar", x:"count", y:"assetType", startAtZero:true }} rows={assetTypeRows} sourceRows={filtered} height={320} />
      <EvidenceChart id="survey-trend" queryId={QUERY_ID} title="Survey activity by date" description="Number of field records logged on each device date." spec={{ type:"line", x:"surveyDate", y:"count", startAtZero:true }} rows={dailyRows} sourceRows={filtered} height={320} />
    </Section>

    <Section id="quality-control" title="Quality and action queue" columns={1}>
      <DataComponent id="quality-queue" queryId={QUERY_ID} kind="table" title="Records requiring data correction" description="Exceptions are evaluated from the same filtered population." sourceRows={filtered} displayRows={qualityRows} variant="card">
        <DataTable rows={qualityRows} rowKey="id" searchable columns={[
          { key:"assetCode", label:"Asset ID" }, { key:"category", label:"Category" }, { key:"assetType", label:"Asset type" },
          { key:"condition", label:"Condition", presentation:"status" }, { key:"surveyor", label:"Surveyor" }, { key:"qualityIssue", label:"Quality issue" },
        ]} />
      </DataComponent>
      <DataComponent id="record-register" queryId={QUERY_ID} kind="table" title="Filtered asset register" description="Exact operational records behind the dashboard. Export uses this same filtered scope." sourceRows={filtered} displayRows={registerRows} variant="card">
        <div className="register-actions"><button type="button" onClick={() => downloadCsv(filtered)} disabled={!filtered.length}>Export filtered CSV</button></div>
        <DataTable rows={registerRows} rowKey="id" searchable columns={[
          { key:"assetCode", label:"Asset ID" }, { key:"surveyDate", label:"Date" }, { key:"category", label:"Category" },
          { key:"assetType", label:"Asset type" }, { key:"assetName", label:"Location" }, { key:"zone", label:"Zone" },
          { key:"condition", label:"Condition", presentation:"status" }, { key:"gpsAccuracyDisplay", label:"GPS accuracy" },
          { key:"photoCount", label:"Photos" }, { key:"surveyor", label:"Surveyor" },
        ]} />
      </DataComponent>
    </Section>
  </article>;
}
