"use strict";
const AOI_BOUNDS={west:77.5030283,south:23.0624953,east:77.5799250,north:23.1164963};
const status=document.querySelector("#status");
const viewer=new Cesium.Viewer("cesiumContainer",{animation:false,timeline:false,baseLayerPicker:false,geocoder:false,homeButton:false,sceneModePicker:false,selectionIndicator:true,infoBox:true,baseLayer:false,terrainProvider:new Cesium.EllipsoidTerrainProvider(),shouldAnimate:false});
viewer.scene.globe.enableLighting=true;viewer.scene.globe.depthTestAgainstTerrain=false;viewer.scene.fog.enabled=true;viewer.scene.fog.density=0.00008;viewer.scene.sun.show=true;
const aoi=Cesium.Rectangle.fromDegrees(AOI_BOUNDS.west,AOI_BOUNDS.south,AOI_BOUNDS.east,AOI_BOUNDS.north);
const cameraDestination=Cesium.Cartesian3.fromDegrees(77.5415,23.0895,100000);
const cameraOrientation={heading:0,pitch:Cesium.Math.toRadians(-90),roll:0};
viewer.scene.mode=Cesium.SceneMode.SCENE3D;
viewer.scene.globe.show=true;
viewer.scene.globe.baseColor=Cesium.Color.fromCssColorString("#9cae88");
// Keep this instance intentionally lightweight until a validated Cesium 3D Tiles
// endpoint is available. The previous GeoJSON fallback loaded tens of thousands
// of polygons and could stop Cesium rendering with an invalid typed-array length.
status.textContent="Cesium scene ready · waiting for validated 3D Tiles endpoint";
async function addSatelliteImagery(){try{const provider=await Cesium.ArcGisMapServerImageryProvider.fromUrl("https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer");viewer.imageryLayers.addImageryProvider(provider);status.textContent="Satellite imagery loaded · ArcGIS World Imagery"}catch(error){status.textContent="Scene ready · satellite imagery unavailable";console.error(error)}}
viewer.imageryLayers.addImageryProvider(new Cesium.OpenStreetMapImageryProvider({url:"https://tile.openstreetmap.org/"}));
addSatelliteImagery();
document.querySelector("#fit").addEventListener("click",()=>viewer.camera.flyTo({destination:cameraDestination,orientation:cameraOrientation,duration:1.2}));
document.querySelector("#toggle-terrain").addEventListener("click",event=>{const enabled=viewer.terrainProvider instanceof Cesium.EllipsoidTerrainProvider;event.currentTarget.textContent=`Terrain: ${enabled?"on":"off"}`;status.textContent=enabled?"Terrain requires a configured Cesium ion or terrain endpoint":"Ellipsoid terrain active"});
