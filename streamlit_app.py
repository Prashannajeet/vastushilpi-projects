from pathlib import Path
import json
import os
import streamlit as st
import folium
from branca.element import MacroElement, Template
from folium.plugins import Draw, Fullscreen, MeasureControl
from streamlit_folium import st_folium
import plotly.graph_objects as go
from terrain import elevation_profile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'Interactive_Maps/assets'
DATA = Path(os.environ.get('VASTUSHILPI_DATA_DIR', ROOT / 'outputs'))
CONFIG = json.loads((ASSETS / 'config.json').read_text())

st.set_page_config(page_title='Vastushilpi Projects', page_icon='🗺️', layout='wide')
st.markdown('''<style>
[data-testid="stAppViewContainer"]{background:linear-gradient(145deg,#edf6ff,#f4fbf3 55%,#fff3f6)}
[data-testid="stHeader"]{display:none}
.block-container{padding:.6rem .8rem .6rem;max-width:none}
[data-testid="stVerticalBlock"]{gap:.5rem}
h3{font-size:1rem!important;padding:.1rem 0!important;color:#223b42}
[data-testid="stMetric"]{background:#f7fbfc;border:1px solid #dce6e9;border-radius:8px;padding:7px 10px}
[data-testid="stMetricValue"]{font-size:1.15rem!important;white-space:normal;overflow:visible}
[data-testid="stMetricValue"]>div{white-space:normal;overflow:visible;text-overflow:clip}
.st-key-layer_panel,.st-key-profile_panel{background:#fffdfb;border:1px solid #dce6e9;border-radius:9px;padding:12px}
.st-key-layer_panel [data-testid="stCheckbox"]{background:#f8fbfc;border:1px solid #e1e8ea;border-radius:6px;padding:1px 8px}
.st-key-layer_panel p{font-size:.8rem}
.st-key-layer_panel hr{margin:.6rem 0}
.st-key-layer_panel [data-testid="stCheckbox"] label{width:100%}
.st-key-map_panel iframe{border-radius:9px}
.st-key-profile_panel [data-testid="stMetricLabel"] p{font-size:.72rem}
.st-key-profile_panel [data-testid="stDownloadButton"] button{width:100%}
.st-key-workspace_header{background:linear-gradient(110deg,#e1efff,#e8f7eb 60%,#fff2d7);border:1px solid #dce6e9;border-radius:9px;padding:14px 18px;box-shadow:0 8px 22px #243f4810}
.brand{display:flex;align-items:center;gap:9px;font-size:11px;font-weight:700;letter-spacing:1.5px;color:#33717e;margin-bottom:6px}
.brand-mark{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;background:linear-gradient(135deg,#245c75,#4096a3);color:white;border-radius:7px;font-size:12px;letter-spacing:0;box-shadow:0 3px 8px #245c7520}
.developer-credit{font-size:10px;color:#476a75;line-height:1.5;margin-top:10px}
.workspace-title{font-size:23px;font-weight:750;color:#20383e;line-height:1.25}
.workspace-subtitle{font-size:12px;color:#64767c;margin-top:5px}
@media(min-width:1200px){
[data-testid="stMain"]{overflow:hidden}
.st-key-layer_panel,.st-key-profile_panel{min-height:calc(100dvh - 180px)}
.st-key-layer_panel{max-height:calc(100dvh - 180px);overflow-y:auto}
.st-key-map_panel iframe{height:calc(100dvh - 210px)!important;min-height:260px}
}
/* Pastel surfaces keep dark text and geographic imagery legible. */
.st-key-layer_panel{background:#eef7ff;border-color:#d3e4f5}
.st-key-profile_panel{background:#fff4f7;border-color:#ecdce3}
[data-testid="stMetric"]{background:#fff4d9;border-color:#e7dfc7}
.st-key-workspace_header [data-testid="stColumn"]:nth-child(2) [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"]{background:#e4efff}
.st-key-workspace_header [data-testid="stColumn"]:nth-child(2) [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{background:#e5f4e7}
.st-key-workspace_header [data-testid="stColumn"]:nth-child(2) [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{background:#fbe7ed}
.st-key-layer_panel [data-testid="stCheckbox"]{background:#e5f4e7;border-color:#d4e5d5}
.st-key-layer_panel [data-testid="stCheckbox"]:nth-of-type(2n){background:#fff0d9}
button[data-baseweb="tab"]{color:#735d50}
button[data-baseweb="tab"][aria-selected="true"]{background:#e3eefb;border-radius:7px;color:#28576f}
[data-testid="stDownloadButton"] button{background:#e7f4e5;border-color:#c8dfc6;color:#355b42}
@media(max-width:1199px){
[data-testid="stMain"]{overflow:auto}
.st-key-layer_panel,.st-key-profile_panel{min-height:0}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel){flex-wrap:wrap}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel)>[data-testid="stColumn"]:nth-child(1){flex:1 1 26%;min-width:240px}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel)>[data-testid="stColumn"]:nth-child(2){flex:2 1 65%;min-width:0}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel)>[data-testid="stColumn"]:nth-child(3){flex:1 1 100%;width:100%}
.st-key-map_panel iframe{height:540px!important}
.st-key-workspace_header>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"]{flex-wrap:wrap}
.st-key-workspace_header>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{flex:1 1 100%;width:100%}
}
@media(max-width:640px){
.st-key-workspace_header [data-testid="stColumn"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:8px!important}
.st-key-workspace_header [data-testid="stColumn"] [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{flex:1 1 45%!important;width:45%!important;min-width:0!important}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel)>[data-testid="stColumn"]:nth-child(2){order:-1}

.block-container{padding:.5rem}
.workspace-title{font-size:19px}
.brand{font-size:9px;letter-spacing:.7px}
.st-key-workspace_header{padding:12px}
[data-testid="stHorizontalBlock"]:has(.st-key-layer_panel)>[data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important;min-width:0!important}
.st-key-map_panel iframe{height:420px!important}
[data-testid="stMetricValue"]{font-size:1rem!important}
[data-testid="stMetricLabel"] p{font-size:.7rem}
[data-testid="stTabs"] button{min-height:44px}
.st-key-map_panel [data-testid="stMarkdownContainer"]>div{flex-wrap:wrap}
}
</style>''',unsafe_allow_html=True)
header = st.container(key='workspace_header')
layer_column, map_column, profile_column = st.columns([1.05,3.35,1.35],gap='small')
with layer_column, st.container(key='layer_panel'):
    st.subheader('Survey workspace')
    location = st.selectbox('Location', list(CONFIG), format_func=lambda n: CONFIG[n]['title'])
    cfg = CONFIG[location]
    st.divider()
    st.subheader('Layer stack')
    basemap = st.selectbox('Basemap', ['Satellite imagery', 'Topography', 'ArcGIS terrain + topography · Labels'])
    show_dem = st.checkbox('Smooth DEM', True)
    show_hillshade = st.checkbox('Smooth hillshade', True)
    show_contours = st.checkbox('Contours · 1 m', False)
    show_coverage = st.checkbox('Survey coverage', True)
    opacity = st.slider('Terrain opacity', 0, 100, 65) / 100
    with st.expander('Layer comparison · Swipe'):
        compare = st.checkbox('Enable swipe comparison')
        compare_left = st.selectbox('Left layer', ['Smooth DEM', 'Smooth hillshade', 'Basemap'])
        compare_right = st.selectbox('Right layer', ['Basemap', 'Smooth DEM', 'Smooth hillshade'])
        st.caption('Drag the divider across the map. The basemap remains visible beneath transparent terrain.')
    st.divider()
    st.subheader('Drawing tools')
    st.caption('Line → elevation profile. Polygon, rectangle or marker → annotation. Finish a line by clicking its last vertex.')
    st.caption('Use the map toolbar to edit, delete, measure or enter fullscreen.')
    st.divider()
    st.caption(f"Projected reference · EPSG:{cfg['epsg']}")
    st.markdown("<div class='developer-credit'><strong>NITA AI &amp; GEOANALYTICS</strong><br>Developed by Nita AI &amp; Geoanalytics (OPC) Pvt Ltd</div>",unsafe_allow_html=True)
with header:
    heading, counters = st.columns([2,3])
    with heading:
        st.markdown(f"<div class='brand'><span class='brand-mark'>NA</span><span>NITA AI &amp; GEOANALYTICS · TERRAIN &amp; GIS</span></div><div class='workspace-title'>Vastushilpi Projects · {cfg['title']}</div><div class='workspace-subtitle'>Developed by Nita AI &amp; Geoanalytics (OPC) Pvt Ltd</div>",unsafe_allow_html=True)
    with counters:
        a,b,c,d = st.columns(4)
        a.metric('Survey points', f"{cfg['points']:,}")
        b.metric('Coverage', f"{cfg['area']:.2f} ha")
        c.metric('Elevation', f"{cfg['range'][0]:.1f}–{cfg['range'][1]:.1f} m")
        d.metric('Grid spacing', f"{cfg['spacing']} m")

bounds = cfg['bounds']; centre = [(bounds[0][i]+bounds[1][i])/2 for i in (0,1)]
m = folium.Map(location=centre, tiles=None, control_scale=True, prefer_canvas=False)
if basemap == 'Satellite imagery':
    folium.TileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Imagery © Esri, Maxar, Earthstar Geographics and GIS User Community', name='Satellite imagery', max_native_zoom=19, max_zoom=22).add_to(m)
elif basemap == 'Topography':
    folium.TileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Map data © OpenStreetMap contributors, SRTM | © OpenTopoMap (CC-BY-SA)', name='Topography', max_native_zoom=17, max_zoom=22).add_to(m)
else:
    folium.TileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',attr='Topography © Esri, HERE, Garmin, FAO, USGS, NGA and GIS User Community',name='ArcGIS topography with labels',max_native_zoom=19,max_zoom=22).add_to(m)
    folium.map.CustomPane('basemap_relief',z_index=250,pointer_events=False).add_to(m)
    folium.TileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',attr='World Hillshade © Esri, USGS, GEBCO and GIS User Community',name='ArcGIS shaded relief',pane='basemap_relief',opacity=.35,max_native_zoom=16,max_zoom=22,overlay=True).add_to(m)
    relief_style = MacroElement()
    relief_style._template = Template('''{% macro script(this, kwargs) %}
    {{this._parent.get_name()}}.getPane('basemap_relief').style.mixBlendMode='multiply';
    {% endmacro %}''')
    relief_style.add_to(m)
if show_dem and not compare:
    folium.raster_layers.ImageOverlay(str(ASSETS / f'{location}_dem.png'), bounds=bounds, opacity=opacity, name='Smooth DEM').add_to(m)
if show_hillshade and not compare:
    folium.raster_layers.ImageOverlay(str(ASSETS / f'{location}_hillshade.png'), bounds=bounds, opacity=1, name='Smooth hillshade').add_to(m)
if compare:
    for side, label in [('left', compare_left), ('right', compare_right)]:
        pane = f'comparison_{side}'
        folium.map.CustomPane(pane, z_index=410, pointer_events=False).add_to(m)
        if label != 'Basemap':
            suffix = 'dem' if label == 'Smooth DEM' else 'hillshade'
            folium.raster_layers.ImageOverlay(str(ASSETS / f'{location}_{suffix}.png'),bounds=bounds,opacity=1,pane=pane,name=f'{side} · {label}').add_to(m)
    swipe = MacroElement()
    swipe._template = Template('''{% macro script(this, kwargs) %}
    (function(){
        const map = {{this._parent.get_name()}};
        const left = map.getPane('comparison_left'), right = map.getPane('comparison_right');
        const control = L.control({position:'bottomleft'});
        control.onAdd = function(){
            const box = L.DomUtil.create('div','swipe-control');
            box.style.cssText='background:#fff4d9;padding:8px 12px;border-radius:8px;color:#344e59;box-shadow:0 2px 8px #0002;max-width:calc(100vw - 100px)';
            const title = document.createElement('div');title.textContent='Swipe layer comparison';title.style.fontSize='12px';box.appendChild(title);
            const slider = document.createElement('input');slider.type='range';slider.min=0;slider.max=100;slider.value=50;slider.setAttribute('aria-label','Layer comparison divider');slider.style.cssText='width:220px;max-width:100%;height:30px;touch-action:none';box.appendChild(slider);
            L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);
            const divider = L.DomUtil.create('div','swipe-divider',map.getContainer());
            divider.style.cssText='position:absolute;top:0;bottom:0;width:3px;background:#fff4d9;z-index:450;pointer-events:none;box-shadow:0 0 5px #0007';
            function update(){
                const size=map.getSize(),origin=map.containerPointToLayerPoint([0,0]);
                const cut=size.x*Number(slider.value)/100;
                // Leaflet panes move during pan; clip in layer coordinates.
                left.style.clipPath=`polygon(${origin.x}px ${origin.y}px,${origin.x+cut}px ${origin.y}px,${origin.x+cut}px ${origin.y+size.y}px,${origin.x}px ${origin.y+size.y}px)`;
                right.style.clipPath=`polygon(${origin.x+cut}px ${origin.y}px,${origin.x+size.x}px ${origin.y}px,${origin.x+size.x}px ${origin.y+size.y}px,${origin.x+cut}px ${origin.y+size.y}px)`;
                divider.style.left=cut+'px';
            }
            divider.style.width='12px';divider.style.background='linear-gradient(90deg,transparent 4px,#fff4d9 4px,#fff4d9 7px,transparent 7px)';divider.style.pointerEvents='auto';divider.style.touchAction='none';divider.style.cursor='ew-resize';
            L.DomEvent.disableClickPropagation(divider);
            divider.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();divider.setPointerCapture(e.pointerId);map.dragging.disable();});
            divider.addEventListener('pointermove',e=>{if(divider.hasPointerCapture(e.pointerId)){const rect=map.getContainer().getBoundingClientRect();slider.value=Math.max(0,Math.min(100,(e.clientX-rect.left)/rect.width*100));update();}});
            function finish(e){if(divider.hasPointerCapture(e.pointerId))divider.releasePointerCapture(e.pointerId);map.dragging.enable();}
            divider.addEventListener('pointerup',finish);divider.addEventListener('pointercancel',finish);
            slider.addEventListener('input',update);map.on('move zoom resize',update);requestAnimationFrame(update);
            return box;
        };control.addTo(map);
    })();
    {% endmacro %}''')
    swipe.add_to(m)
if show_coverage:
    folium.GeoJson(json.loads((ASSETS / f'{location}_coverage.geojson').read_text()), name='Survey coverage', style_function=lambda _: {'color':'#ffe7a0','weight':2,'fillOpacity':0,'dashArray':'5 4'}).add_to(m)
if show_contours:
    contours = json.loads((ASSETS / f'{location}_contours.geojson').read_text())
    folium.GeoJson(contours, name='Contours 1 m', style_function=lambda _: {'color':'#473b27','weight':1,'opacity':.7}).add_to(m)
editable = folium.FeatureGroup(name='User drawings').add_to(m)
for feature in st.session_state.get(f'drawings_{location}', []):
    geometry = feature.get('geometry', {})
    coords = geometry.get('coordinates', [])
    if geometry.get('type') == 'LineString':
        folium.PolyLine([[lat, lon] for lon, lat in coords], color='#e7c578', weight=4).add_to(editable)
    elif geometry.get('type') == 'Polygon':
        folium.Polygon([[[lat, lon] for lon, lat in ring] for ring in coords], color='#e7c578', fill_opacity=.15).add_to(editable)
    elif geometry.get('type') == 'Point':
        folium.Marker([coords[1], coords[0]]).add_to(editable)
Draw(export=False, feature_group=editable, position='topleft', draw_options={'polyline':{'shapeOptions':{'color':'#e7c578','weight':4}},'polygon':{'allowIntersection':False,'showArea':True,'shapeOptions':{'color':'#e7c578'}},'rectangle':True,'marker':True,'circle':False,'circlemarker':False}, edit_options={'edit':True,'remove':True}).add_to(m)
Fullscreen(position='topright').add_to(m); MeasureControl(position='topright',primary_length_unit='meters',primary_area_unit='sqmeters').add_to(m)
m.fit_bounds(bounds, padding=(25,25))
m.get_root().header.add_child(folium.Element('<style>html,body{height:100%;overflow:hidden}#map_div{height:100vh!important}</style>'))
with map_column, st.container(key='map_panel'):
    result = st_folium(m, key=f'map_{location}', height=610, use_container_width=True, returned_objects=['all_drawings'])
    
    if compare:
        st.caption(f'← {compare_left} | {compare_right} → · Drag the comparison slider')
    st.markdown(f"<div style='display:flex;align-items:center;gap:10px;font-size:11px;color:#526b73'><span>{cfg['range'][0]:.1f} m</span><div style='height:10px;width:140px;background:linear-gradient(90deg,#1e6678,#429995,#a3c391,#e1d197,#b28b69,#f2ebe1)'></div><span>{cfg['range'][1]:.1f} m</span><span>Smoothed elevation · geographic north is up</span></div>", unsafe_allow_html=True)
state_key = f'drawings_{location}'
if result and result.get('all_drawings') is not None:
    st.session_state[state_key] = result['all_drawings']
drawings = st.session_state.get(state_key, [])
with profile_column, st.container(key='profile_panel'):
    st.subheader('Survey intelligence')
    profile_tab, data_tab, reference_tab = st.tabs(['Profile','Data','Reference'])
    with data_tab:
        st.write(f"**{cfg['title']}**")
        st.caption(f"{cfg['points']:,} XYZ survey points · {cfg['spacing']} m point spacing")
        st.caption(f"DEM coverage {cfg['area']:.2f} ha · original cell size 0.5 m")
        st.caption(f"User annotations: {len(drawings)}")
        if drawings:
            st.download_button('Export drawings · GeoJSON',json.dumps({'type':'FeatureCollection','features':drawings},indent=2),file_name=f'{location}_drawings_wgs84.geojson',mime='application/geo+json')
    with reference_tab:
        st.write(f"**EPSG:{cfg['epsg']}**")
        st.caption(cfg['datumNote'])
        st.caption('Profiles use the original 0.5 m DEM with bilinear sampling. Gaps indicate NoData.')
        st.caption('Smooth terrain uses a 1 m Gaussian filter for display. Coverage is an interpolation mask, not a legal boundary. Cell size does not represent survey accuracy.')
    with profile_tab:
        st.caption('DRAW A ROUTE TO EXPLORE ELEVATION')
        lines = [f for f in drawings if f.get('geometry',{}).get('type') == 'LineString']
        if not lines:
            st.caption('Draw a line on the map. Click its final vertex again to finish.')
        else:
            selected = st.selectbox('Profile route',range(len(lines)),format_func=lambda i: f'Line {i+1}',key=f'route_{location}')
            path = DATA / f'{location}_dem_0p5m.tif'
            if not path.exists():
                st.warning('The original DEM is not installed on this server. Provide the DEM file to enable profiles.')
                upload = st.file_uploader('Original projected 0.5 m DEM GeoTIFF',type=['tif','tiff'],key=f'dem_{location}')
                if upload:
                    from rasterio.io import MemoryFile
                    with MemoryFile(upload.getvalue()) as mem:
                        # /vsimem/ is used only within the current upload lifetime.
                        path = mem.name
                        try:
                            df, stats = elevation_profile(path,lines[selected]['geometry']['coordinates'])
                        except Exception as error:
                            st.error(str(error));st.stop()
                else:
                    st.stop()
            else:
                try:
                    with st.spinner('Sampling original DEM…'):
                        df, stats = elevation_profile(path,lines[selected]['geometry']['coordinates'])
                except Exception as error:
                    st.error(f'Profile could not be sampled: {error}');st.stop()
            if stats['epsg'] != cfg['epsg']:
                st.error(f"DEM must use EPSG:{cfg['epsg']} for this survey.");st.stop()
            ca, cb, cc = st.columns(3)
            ca.metric('Route distance',f"{stats['length_m']:.1f} m");cb.metric('DEM support',f"{stats['supported_percent']:.1f}%");cc.metric('Sample interval',f"{stats['sample_interval_m']:.2f} m")
            if df['elevation_m'].notna().any():
                fig = go.Figure(go.Scatter(x=df.distance_m,y=df.elevation_m,mode='lines',connectgaps=False,line={'color':'#147c86','width':2},hovertemplate='%{x:.1f} m distance<br>%{y:.2f} m elevation<extra></extra>'))
                fig.update_layout(height=240,autosize=True,margin={'l':20,'r':20,'t':15,'b':20},xaxis_title='Distance (m)',yaxis_title='Elevation (m)',paper_bgcolor='white',plot_bgcolor='white',font={'color':'#102f39'},xaxis={'gridcolor':'#e2eaed'},yaxis={'gridcolor':'#e2eaed'})
                st.plotly_chart(fig,width="stretch")
            else:
                st.warning('No supported DEM elevations along this route. Draw inside the marked survey coverage.')
            st.caption('Original TIN DEM · bilinear sampling · gaps indicate NoData · vertical datum unconfirmed')
            st.download_button('Export profile CSV',df.to_csv(index=False),file_name=f'{location}_elevation_profile.csv',mime='text/csv')
