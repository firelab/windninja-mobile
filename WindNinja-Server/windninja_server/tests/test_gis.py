import windninjawrapper.gis as wngis


BBOX_INSIDE_AK = [
    -147.9105926641097,
    64.79848287245939,
    -147.54226039805448,
    64.87942609584164,
]
BBOX_INSIDE_CONUS = [
    -114.0235465406869,
    46.99526210560205,
    -113.97925790543299,
    47.038565315467025,
]
BBOX_OUTSIDE = [
    92.60344875583002,
    55.89740919625363,
    93.26630525449141,
    56.124209568573185,
]


def test_within_forecast():
    forecast = wngis.withinForecast(BBOX_INSIDE_AK)
    assert (
        forecast == "NOMADS-HIRES-ARW-ALASKA-5-KM"
    ), "Invalid forecast for AK bounding box"

    forecast = wngis.withinForecast(BBOX_INSIDE_CONUS)
    assert forecast == "NOMADS-HRRR-CONUS-3-KM", "Invalid forecast for AK bounding box"

    forecast = wngis.withinForecast(BBOX_OUTSIDE)
    assert forecast is None, "Invalid forecast returned for bounding box outside"
