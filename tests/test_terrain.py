import tempfile
import unittest
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
from terrain import elevation_profile

class TerrainTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'plane.tif'
        self.transform=from_origin(500000,2500010,.5,.5)
        rows,cols=np.mgrid[:20,:20];self.values=(100+3*(cols+.5)*.5+2*(10-(rows+.5)*.5)).astype('float32')
        self.write(self.values)
        self.to_wgs=Transformer.from_crs(32643,4326,always_xy=True)
    def tearDown(self): self.temp.cleanup()
    def write(self,values):
        with rasterio.open(self.path,'w',driver='GTiff',height=20,width=20,count=1,dtype='float32',crs='EPSG:32643',transform=self.transform,nodata=float('nan')) as out:out.write(values,1)
    def route(self,a,b):return [list(self.to_wgs.transform(*p)) for p in (a,b)]
    def test_plane_bilinear_and_native_distance(self):
        df,stats=elevation_profile(self.path,self.route((500001.3,2500008.6),(500008.1,2500002.2)))
        expected=100+3*(df.easting_m-500000)+2*(df.northing_m-2500000)
        np.testing.assert_allclose(df.elevation_m,expected,atol=1e-5)
        self.assertAlmostEqual(stats['length_m'],np.hypot(6.8,6.4),places=6)
        self.assertEqual(stats['epsg'],32643)
    def test_nodata_not_bridged(self):
        self.values[:,9:11]=np.nan;self.write(self.values)
        df,stats=elevation_profile(self.path,self.route((500001,2500005),(500009,2500005)))
        self.assertTrue(df.elevation_m.isna().any());self.assertTrue(df.elevation_m.notna().any());self.assertLess(stats['supported_percent'],100)
    def test_outside_extent(self):
        df,stats=elevation_profile(self.path,self.route((500020,2500020),(500030,2500020)))
        self.assertEqual(stats['supported_percent'],0)
    def test_zero_route_rejected(self):
        with self.assertRaises(ValueError):elevation_profile(self.path,self.route((500001,2500005),(500001,2500005)))

if __name__=='__main__':unittest.main()
