import unittest
import os
import windninjawrapper.gis as wngis


class TestGIS(unittest.TestCase):
    bbox_inside_ak = [
        -147.9105926641097,
        64.79848287245939,
        -147.54226039805448,
        64.87942609584164,
    ]
    bbox_inside_conus = [
        -114.0235465406869,
        46.99526210560205,
        -113.97925790543299,
        47.038565315467025,
    ]
    bbox_outside = [
        92.60344875583002,
        55.89740919625363,
        93.26630525449141,
        56.124209568573185,
    ]

    @classmethod
    def setUpClass(cls):
        pass

    def test_withinForecast(self):
        forecast = wngis.withinForecast(TestGIS.bbox_inside_ak)
        self.assertEqual(
            forecast,
            "NOMADS-HIRES-ARW-ALASKA-5-KM",
            msg="Invalid forecast for AK bounding box",
        )

        forecast = wngis.withinForecast(TestGIS.bbox_inside_conus)
        self.assertEqual(
            forecast,
            "NOMADS-HRRR-CONUS-3-KM",
            msg="Invalid forecast for AK bounding box",
        )

        forecast = wngis.withinForecast(TestGIS.bbox_outside)
        self.assertIsNone(
            forecast, msg="Invalid forecast returned for bounding box outside"
        )

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == "__main__":
    unittest.main()
