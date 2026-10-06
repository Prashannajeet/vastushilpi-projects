from pathlib import Path
from qgis.core import *
import json
app=QgsApplication([],False);app.setPrefixPath('/Applications/QGIS-LTR.app/Contents/MacOS',True);app.initQgis();root=Path(__file__).resolve().parent.parent;results=[]
for n in ('grid','geolocation'):
 p=QgsProject.instance();p.clear();assert p.read(str(root/'outputs/GIS_Map_Package'/f'{n}_interactive_gis.qgz'))
 invalid=[l.name() for l in p.mapLayers().values() if not l.isValid()];assert not invalid,invalid
 original=next(l for l in p.mapLayers().values() if l.name().startswith('Original DEM'));assert original.elevationProperties().isEnabled()
 layouts=[l.name() for l in p.layoutManager().layouts()];assert 'Satellite | Professional GIS layout' in layouts and 'Topography | Professional GIS layout' in layouts
 sat=next(l for l in p.mapLayers().values() if l.name().startswith('Satellite imagery'));assert p.layerTreeRoot().findLayer(sat.id()).isVisible()
 results.append({'location':n,'valid_layers':len(p.mapLayers()),'epsg':p.crs().authid(),'satellite_default':True,'profile_surface_enabled':True,'layouts':layouts})
(root/'Interactive_Maps/qgis_validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));app.exitQgis()
