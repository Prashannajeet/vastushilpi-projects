from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QPainter
app=QgsApplication([],False);app.setPrefixPath('/Applications/QGIS-LTR.app/Contents/MacOS',True);app.initQgis()
ROOT=Path(__file__).resolve().parent.parent
for n in ('grid','geolocation'):
 p=QgsProject.instance();p.clear();assert p.read(str(ROOT/'outputs/GIS_Map_Package'/f'{n}_terrain.qgz'))
 original=list(p.mapLayers().values());origdem=next(l for l in original if isinstance(l,QgsRasterLayer) and l.name()=='Elevation (m)');orighs=next(l for l in original if isinstance(l,QgsRasterLayer) and l.name()=='Hillshade')
 origdem.setName('Original DEM | 0.5 m | elevation profile source');origdem.elevationProperties().setEnabled(True)
 smooth=QgsRasterLayer(str(ROOT/'outputs'/f'{n}_dem_smooth_0p5m.tif'),'Smooth DEM | display only');assert smooth.isValid();smooth.setRenderer(origdem.renderer().clone());smooth.setOpacity(.65)
 hs=QgsRasterLayer(str(ROOT/'outputs'/f'{n}_hillshade_smooth.tif'),'Smooth multidirectional hillshade');assert hs.isValid();hs.setRenderer(orighs.renderer().clone());hs.setOpacity(.5);hs.setBlendMode(QPainter.CompositionMode_Multiply)
 p.addMapLayer(smooth);p.addMapLayer(hs)
 root=p.layerTreeRoot();root.findLayer(origdem.id()).setItemVisibilityChecked(False);root.findLayer(orighs.id()).setItemVisibilityChecked(False)
 basemaps=root.addGroup('Online basemaps')
 satellite=QgsRasterLayer('type=xyz&url=https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}&zmin=0&zmax=19','Satellite imagery | Esri World Imagery','wms')
 topo=QgsRasterLayer('type=xyz&url=https://a.tile.opentopomap.org/{z}/{x}/{y}.png&zmin=0&zmax=17','Topography | OpenTopoMap','wms')
 for layer in (satellite,topo):
  assert layer.isValid(),layer.name();p.addMapLayer(layer,False);basemaps.addLayer(layer)
 root.findLayer(topo.id()).setItemVisibilityChecked(False)
 satellite.setAbstract('Sources: Esri, Maxar, Earthstar Geographics and GIS User Community. Online service; imagery date and resolution vary.')
 topo.setAbstract('Map data © OpenStreetMap contributors, SRTM; style © OpenTopoMap (CC-BY-SA). Online service.')
 manager=p.layoutManager();templates=list(manager.layouts())
 for old in templates:
  for kind,base,attribution in [('Satellite',satellite,'IMAGERY  © Esri, Maxar, Earthstar Geographics and GIS User Community'),('Topography',topo,'BASEMAP  © OpenStreetMap contributors, SRTM | © OpenTopoMap (CC-BY-SA)')]:
   new=manager.duplicateLayout(old,kind+' | Professional GIS layout')
   for item in new.items():
    if isinstance(item,QgsLayoutItemMap):
     layers=item.layers()
     # Keep the existing slope inset; change the main terrain map only.
     if any(l.id()==origdem.id() for l in layers):
      stack=[smooth if l.id()==origdem.id() else hs if l.id()==orighs.id() else l for l in layers];item.setLayers(stack+[base]);item.setKeepLayerSet(True)
    elif isinstance(item,QgsLayoutItemLabel):
     if item.text().startswith('METHOD  '):item.setText('METHOD  0.5 m TIN DEM | Gaussian display smoothing: sigma 1 m | multidirectional hillshade')
     elif item.text().startswith('SOURCE '):item.setText(item.text()+'\n'+attribution)
   # Attribution stays inside the page bottom margin, away from the existing footer.
   lab=QgsLayoutItemLabel(new);lab.setText(attribution);new.addLayoutItem(lab);lab.attemptMove(QgsLayoutPoint(15,286));lab.attemptResize(QgsLayoutSize(390,7));f=lab.font();f.setPointSize(7);lab.setFont(f)
 dest=ROOT/'outputs/GIS_Map_Package'/f'{n}_interactive_gis.qgz';p.setFileName(str(dest));p.setFilePathStorage(Qgis.FilePathType.Relative);assert p.write();print(dest,flush=True)
app.exitQgis()
