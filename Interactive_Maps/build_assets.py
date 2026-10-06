from pathlib import Path
from osgeo import gdal,ogr,osr
import numpy as np,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'Interactive_Maps/assets';OUT.mkdir(exist_ok=True)
gdal.UseExceptions()
def srs(e):
 s=osr.SpatialReference();s.ImportFromEPSG(e);s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);return s
config={}
for n,epsg,title,points,area,spacing in [('grid',32643,'Grid survey · 2009',20071,52.65,5),('geolocation',24379,'Hiraundi · I–A',15055,174.93,10)]:
 src=gdal.Open(str(ROOT/'outputs'/f'{n}_dem_smooth_0p5m.tif'));gt=src.GetGeoTransform()
 warp=gdal.Warp('',src,format='MEM',dstSRS='EPSG:3857',width=3000,resampleAlg='bilinear',dstNodata=float('nan'))
 a=warp.ReadAsArray();mask=np.isfinite(a);lo,hi=(393,424) if n=='grid' else (391.39,447.01)
 stops=np.array([[30,102,120],[66,153,149],[163,195,145],[225,209,151],[178,139,105],[242,235,225]])
 t=np.clip((np.nan_to_num(a,nan=lo)-lo)/(hi-lo),0,1)*5;idx=np.minimum(t.astype(int),4);f=(t-idx)[...,None];rgb=(stops[idx]*(1-f)+stops[idx+1]*f).astype('uint8')
 Image.fromarray(np.dstack([rgb,(mask*255).astype('uint8')])).save(OUT/f'{n}_dem.png')
 hg=gdal.Warp('',str(ROOT/'outputs'/f'{n}_hillshade_smooth.tif'),format='MEM',dstSRS='EPSG:3857',outputBounds=[warp.GetGeoTransform()[0],warp.GetGeoTransform()[3]+warp.RasterYSize*warp.GetGeoTransform()[5],warp.GetGeoTransform()[0]+warp.RasterXSize*warp.GetGeoTransform()[1],warp.GetGeoTransform()[3]],width=warp.RasterXSize,height=warp.RasterYSize,resampleAlg='bilinear',dstNodata=float('nan')).ReadAsArray()
 # Use dark transparent ink: bright flat ground remains unobscured.
 alpha=(np.clip((1-np.nan_to_num(hg,nan=1))*.9,0,.65)*255).astype('uint8');alpha[~mask]=0
 Image.fromarray(np.dstack([np.zeros((*a.shape,3),dtype='uint8'),alpha])).save(OUT/f'{n}_hillshade.png')
 wg=warp.GetGeoTransform(); tr=osr.CoordinateTransformation(srs(3857),srs(4326));sw=tr.TransformPoint(wg[0],wg[3]+warp.RasterYSize*wg[5]);ne=tr.TransformPoint(wg[0]+warp.RasterXSize*wg[1],wg[3])
 for layername,filekey in [('DEM_coverage_polygon','coverage'),('DEM_contours_1m_arc','contours')]:
  ds=ogr.Open(str(ROOT/'outputs/Shapefiles'/n/f'{layername}.shp'))
  if not ds:
   matches=list((ROOT/'outputs/Shapefiles'/n).rglob(f'{layername}.shp'));ds=ogr.Open(str(matches[0]))
  lyr=ds.GetLayer();native=lyr.GetSpatialRef();native.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);ct=osr.CoordinateTransformation(native,srs(4326));features=[]
  for feat in lyr:
   geom=feat.GetGeometryRef().SimplifyPreserveTopology(.5);geom.Transform(ct)
   features.append({'type':'Feature','geometry':json.loads(geom.ExportToJson()),'properties':dict(feat.items())})
  (OUT/f'{n}_{filekey}.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}))
 config[n]={'title':title,'epsg':epsg,'points':points,'area':area,'spacing':spacing,'range':[lo,hi],'bounds':[[sw[1],sw[0]],[ne[1],ne[0]]],'datumNote':'Vertical datum unconfirmed.' if n=='grid' else 'CAD GEODATA placement; Kalianpur → WGS84 transformation accuracy stated as 22 m. Vertical datum unconfirmed.'}
 print(n,'assets complete',flush=True)
(OUT/'config.json').write_text(json.dumps(config))
