"""Local GIS viewer. Original native 0.5 m DEMs are sampled, never display images."""
from http.server import HTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from osgeo import gdal,osr
import numpy as np,json,math,argparse
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
CACHE={};gdal.UseExceptions()
def reference(epsg):
 s=osr.SpatialReference();s.ImportFromEPSG(epsg);s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);return s
def dataset(name):
 if name not in ('grid','geolocation'):raise ValueError('Unknown location')
 if name not in CACHE:
  d=gdal.Open(str(PROJECT/'outputs'/f'{name}_dem_0p5m.tif'));s=d.GetSpatialRef();s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
  CACHE[name]=(d.ReadAsArray(),d.GetGeoTransform(),osr.CoordinateTransformation(reference(4326),s),osr.CoordinateTransformation(s,reference(4326)))
 return CACHE[name]
def sample(a,gt,x,y):
 c=(x-gt[0])/gt[1]-.5;r=(y-gt[3])/gt[5]-.5
 # Clamp only within the raster's cell footprint; never extrapolate outside.
 if c<-.5 or r<-.5 or c>a.shape[1]-.5 or r>a.shape[0]-.5:return None
 c=max(0,min(a.shape[1]-1,c));r=max(0,min(a.shape[0]-1,r));i=int(c);j=int(r);i1=min(i+1,a.shape[1]-1);j1=min(j+1,a.shape[0]-1)
 vals=np.array([a[j,i],a[j,i1],a[j1,i],a[j1,i1]],dtype=float);weights=np.array([(1-(c-i))*(1-(r-j)),(c-i)*(1-(r-j)),(1-(c-i))*(r-j),(c-i)*(r-j)])
 if np.any(~np.isfinite(vals[weights>1e-10])):return None
 return float(np.sum(np.nan_to_num(vals)*weights))
def profile(name,coords):
 if not isinstance(coords,list) or not 2<=len(coords)<=1000:raise ValueError('Draw a line with 2–1,000 vertices')
 if any(len(p)!=2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in p) or abs(p[0])>180 or abs(p[1])>90 for p in coords):raise ValueError('Invalid longitude/latitude')
 a,gt,to_native,to_wgs=dataset(name);xy=np.array([to_native.TransformPoint(*p)[:2] for p in coords]);lengths=np.linalg.norm(np.diff(xy,axis=0),axis=1);total=float(sum(lengths))
 if total<=0 or total>100000:raise ValueError('Profile length must be between 0 and 100 km')
 cum=np.r_[0,np.cumsum(lengths)];count=min(20001,max(2,int(math.ceil(total/.5))+1));distances=np.linspace(0,total,count);rows=[]
 for d in distances:
  k=min(len(lengths)-1,int(np.searchsorted(cum,d,side='right')-1));f=(d-cum[k])/lengths[k] if lengths[k]>0 else 0;p=xy[k]+f*(xy[k+1]-xy[k]);ll=to_wgs.TransformPoint(*p)
  rows.append({'distance':float(d),'z':sample(a,gt,*p),'x':float(p[0]),'y':float(p[1]),'lon':ll[0],'lat':ll[1]})
 zs=[p['z'] for p in rows if p['z'] is not None]
 return {'samples':rows,'length':total,'spacing':total/(count-1),'valid':len(zs),'min':min(zs) if zs else None,'max':max(zs) if zs else None,'epsg':32643 if name=='grid' else 24379,'source':'Original 0.5 m TIN DEM; bilinear cell-centre sampling; unknown vertical datum'}
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT),**kw)
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
 def do_GET(self):
  p=urlparse(self.path).path
  if p in ('/','/grid','/hiraundi'):self.path='/index.html'
  return super().do_GET()
 def do_POST(self):
  if self.path not in ('/api/profile','/api/export'):self.send_error(404);return
  try:
   size=int(self.headers.get('Content-Length',0))
   if size<=0 or size>5000000:raise ValueError('Request too large')
   req=json.loads(self.rfile.read(size))
   if self.path=='/api/export':
    name=req['filename'];allowed={n+suffix for n in ('grid','geolocation') for suffix in ('_drawings_wgs84.geojson','_elevation_profile.csv')}
    if name not in allowed or not isinstance(req['content'],str):raise ValueError('Invalid export')
    if name.endswith('.geojson'):json.loads(req['content'])
    elif not req['content'].startswith('distance_m,elevation_m,'):raise ValueError('Invalid profile CSV')
    dest=ROOT/'exports';dest.mkdir(exist_ok=True);(dest/name).write_text(req['content'])
    response={'saved':'Interactive_Maps/exports/'+name,'url':'exports/'+name}
   else:response=profile(req['location'],req['coordinates'])
   status=200
  except (ValueError,KeyError,TypeError) as e:response={'error':str(e)};status=400
  except Exception:response={'error':'DEM sampling failed. Check that the original project rasters are available.'};status=500
  payload=json.dumps(response,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
 print(f'GIS maps: http://127.0.0.1:{args.port}/grid and /hiraundi',flush=True)
 HTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
