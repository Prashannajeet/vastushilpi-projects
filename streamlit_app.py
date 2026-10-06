from pathlib import Path
import json
import os
import streamlit as st
import folium
from folium.plugins import Draw, Fullscreen, MeasureControl
from streamlit_folium import st_folium
import plotly.graph_objects as go
from terrain import elevation_profile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'Interactive_Maps/assets'
DATA = Path(os.environ.get('VASTUSHILPI_DATA_DIR', ROOT / 'outputs'))
CONFIG = json.loads((ASSETS / 'config.json').read_text())

st.set_page_config(page_title='Vastushilpi Projects', page_icon='🗺️', layout='wide', initial_sidebar_state='auto')
st.markdown('''<style>
.block-container{padding-top:1.8rem;padding-bottom:1.5rem;max-width:1800px}
h1{letter-spacing:-.035em!important}div[data-testid="stMetric"]{background:#eef4f6;border-top:3px solid #147c86;padding:12px 18px;border-radius:5px}
[data-testid="stMetricValue"]{font-size:1.5rem!important}
[data-testid="stSidebar"]{border-right:1px solid #dbe4e7}
</style>''', unsafe_allow_html=True)

with st.sidebar:
    st.title('Vastushilpi Projects')
    location = st.radio('Survey location', list(CONFIG), format_func=lambda n: CONFIG[n]['title'])
    cfg = CONFIG[location]
    st.subheader('Map layers')
    basemap = st.radio('Basemap', ['Satellite imagery', 'Topography'], horizontal=True)
    show_dem = st.checkbox('Smooth DEM', True)
    show_hillshade = st.checkbox('Smooth hillshade', True)
    show_contours = st.checkbox('Contours · 1 m', False)
    show_coverage = st.checkbox('Survey coverage', True)
    opacity = st.slider('DEM opacity', 0, 100, 65) / 100
    st.subheader('Reference')
    st.write(f"**EPSG:{cfg['epsg']}**")
    st.caption(cfg['datumNote'])
    st.caption('Profiles use the original 0.5 m DEM. Smooth layers use a 1 m Gaussian filter for display. Coverage is an interpolation mask, not a legal boundary.')
    st.caption('0.5 m cell size does not represent survey accuracy.')

st.title(cfg['title'])
st.caption('Vastushilpi Projects · Survey GIS')
a, b, c, d = st.columns(4)
a.metric('Survey points', f"{cfg['points']:,}"); b.metric('DEM coverage', f"{cfg['area']:.2f} ha")
c.metric('Elevation range', f"{cfg['range'][0]:.1f}–{cfg['range'][1]:.1f} m"); d.metric('Point spacing', f"{cfg['spacing']} m")
st.info('Draw a line with the map toolbar to create an elevation profile. Draw polygons, rectangles or markers to annotate; use Edit or Delete to change them.')

bounds = cfg['bounds']; centre = [(bounds[0][i]+bounds[1][i])/2 for i in (0,1)]
m = folium.Map(location=centre, tiles=None, control_scale=True, prefer_canvas=False)
if basemap == 'Satellite imagery':
    folium.TileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Imagery © Esri, Maxar, Earthstar Geographics and GIS User Community', name='Satellite imagery', max_native_zoom=19, max_zoom=22).add_to(m)
else:
    folium.TileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Map data © OpenStreetMap contributors, SRTM | © OpenTopoMap (CC-BY-SA)', name='Topography', max_native_zoom=17, max_zoom=22).add_to(m)
if show_dem:
    folium.raster_layers.ImageOverlay(str(ASSETS / f'{location}_dem.png'), bounds=bounds, opacity=opacity, name='Smooth DEM').add_to(m)
if show_hillshade:
    folium.raster_layers.ImageOverlay(str(ASSETS / f'{location}_hillshade.png'), bounds=bounds, opacity=1, name='Smooth hillshade').add_to(m)
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
result = st_folium(m, key=f'map_{location}', height=610, use_container_width=True, returned_objects=['all_drawings'])

st.markdown(f"<div style='display:flex;align-items:center;gap:12px;font-size:14px'><span>{cfg['range'][0]:.1f} m</span><div style='height:10px;width:260px;background:linear-gradient(90deg,#1e6678,#429995,#a3c391,#e1d197,#b28b69,#f2ebe1)'></div><span>{cfg['range'][1]:.1f} m</span><span>Smoothed elevation · geographic north is up</span></div>", unsafe_allow_html=True)

state_key = f'drawings_{location}'
if result and result.get('all_drawings') is not None:
    st.session_state[state_key] = result['all_drawings']
drawings = st.session_state.get(state_key, [])
left, right = st.columns([3,1])
with left:
    st.subheader('Elevation profile')
with right:
    if drawings:
        st.download_button('Export drawings · GeoJSON', json.dumps({'type':'FeatureCollection','features':drawings},indent=2), file_name=f'{location}_drawings_wgs84.geojson',mime='application/geo+json')
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
        fig.update_layout(height=300,margin={'l':20,'r':20,'t':15,'b':20},xaxis_title='Distance (m)',yaxis_title='Elevation (m)',paper_bgcolor='white',plot_bgcolor='white',font={'color':'#102f39'},xaxis={'gridcolor':'#e2eaed'},yaxis={'gridcolor':'#e2eaed'})
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.warning('No supported DEM elevations along this route. Draw inside the marked survey coverage.')
    st.caption('Original TIN DEM · bilinear sampling · gaps indicate NoData · vertical datum unconfirmed')
    st.download_button('Export profile CSV',df.to_csv(index=False),file_name=f'{location}_elevation_profile.csv',mime='text/csv')
