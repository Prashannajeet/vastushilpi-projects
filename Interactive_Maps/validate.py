import json,importlib.util,sys,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gis_server',p/'server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
report=[]
for name in ('grid','geolocation'):
 a,gt,to_native,to_wgs=m.dataset(name)
 finite=np.argwhere(np.isfinite(a));row,col=finite[len(finite)//2];x=gt[0]+(int(col)+.5)*gt[1];y=gt[3]+(int(row)+.5)*gt[5]
 assert abs(m.sample(a,gt,x,y)-float(a[row,col]))<1e-5
 assert m.sample(a,gt,gt[0]-20,gt[3]+20) is None
 # A native projected segment through a supported patch; transforms must roundtrip.
 start=to_wgs.TransformPoint(x-5,y);end=to_wgs.TransformPoint(x+5,y)
 back=to_native.TransformPoint(start[0],start[1]);assert np.linalg.norm(np.array(back[:2])-[x-5,y])<.1
 data=m.profile(name,[list(start[:2]),list(end[:2])]);assert abs(data['length']-10)<.1;assert data['valid']>0
 source=m.PROJECT/'outputs'/f'{name}_dem_0p5m.tif'
 smooth=m.gdal.Open(str(m.PROJECT/'outputs'/f'{name}_dem_smooth_0p5m.tif'));v=smooth.ReadAsArray();assert np.array_equal(np.isfinite(a),np.isfinite(v));assert smooth.GetGeoTransform()==gt
 report.append({'location':name,'sample_matches_original_cell':True,'outside_extent_nodata':True,'native_transform_roundtrip_under_0p1m':True,'profile_length':data['length'],'profile_valid_samples':data['valid'],'smoothing_preserves_original_mask':True,'dem_source':str(source)})
(p/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
