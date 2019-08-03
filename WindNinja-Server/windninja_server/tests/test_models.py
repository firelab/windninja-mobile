import re
import pytest

import windninjaweb.models as wnmodels
import unittest
import datetime
import dateutil

_id_regex = (
    "\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)


def validate_job(actual):
    assert actual is not None, "Job is None"
    assert actual.account == "test@yourdatasmarter.com", "Incorrect job account"

    assert actual.name == "Point Six (test)", "Incorrect job name"
    assert actual.status == wnmodels.JobStatus.succeeded, "Incorrect job status"
    assert actual.id == "11111111-1111-1111-1111-111111111111", "Incorrect job id"
    assert actual.email == "5555555555@vtext.com", "Incorrect job email"

    assert actual.messages is not None, "Job messages is None"
    assert len(actual.messages) == 9, "Incorrect job messages length"
    # TODO: test some messages or split each to verify format

    assert actual.input is not None, "Job input is None"
    assert (
        actual.input.products
        == "vector:true;raster:true;topofire:true;geopdf:false;clustered:true;weather:true"
    ), "Incorrect job input products"
    assert (
        actual.input.parameters
        == "forecast_duration:6;vegetation:trees;mesh_choice:fine"
    ), "Incorrect job input parameters"
    assert actual.input.forecast == "NOMADS-NAM-CONUS-12-KM", "Incorrect job forecast"

    assert actual.input.domain is not None, "Job input domain is None"
    assert (
        actual.input.domain.xmax == -113.97925790543299
    ), "Incorrect job input domain xmax"
    assert (
        actual.input.domain.ymax == 47.038565315467025
    ), "Incorrect job input domain ymax"
    assert (
        actual.input.domain.xmin == -114.0235465406869
    ), "Incorrect job input domain xmin"
    assert (
        actual.input.domain.ymin == 46.99526210560205
    ), "Incorrect job input domain ymin"

    assert actual.output is not None, "Job output is None"
    # assert actual.output.products is not None, "Job output products is None"
    # assert len(actual.output.products) == 4, "Incorrect job output products length"

    assert actual.output.simulations is not None, "Job output simulation is None"
    assert actual.output.products is not None, "Job output products is None"
    assert (
        len(actual.output.products.keys()) == 5
    ), "Incorrect job output products length"

    assert (
        actual.output.products["vector"] is not None
    ), "Job output product vector is None"
    assert (
        actual.output.products["topofire"] is not None
    ), "Job output product topofire is None"
    assert (
        actual.output.products["clustered"] is not None
    ), "Job output product clustered is None"
    assert (
        actual.output.products["weather"] is not None
    ), "Job output product weather is None"
    assert (
        actual.output.products["raster"] is not None
    ), "Job output product raster is None"

    # actual_product = actual.output.products[0]
    # context.assertIsNotNone(actual_product, msg="Job output product[0] is None")
    # TODO: test others are not None
    # context.assertEqual(actual_product.name, "WindNinja Raster Tiles", msg="Incorrect job output product[0] name")
    # context.assertEqual(actual_product.package, "tiles.zip", msg="Incorrect job output product[0] package")
    # context.assertEqual(actual_product.type, "raster", msg="Incorrect job output product[0] type")
    # context.assertEqual(actual_product.format, "tiles", msg="Incorrect job output product[0] format")

    # context.assertEqual(len(actual_product.files), 4, "Incorrect job output product[0] files length")
    # context.assertEqual(actual_product.files[0], "dem_12-15-2015_1700_29m", msg="Incorrect job output product[0] file[0]")

    # context.assertEqual(len(actual_product.data), 4, "Incorrect job output product[0] data length")
    # context.assertEqual(actual_product.data[0], "dem_12-15-2015_1700_29m:24.722978", msg="Incorrect job output product[0] data[0]")

    # TODO: test other products

    actual_product = actual.output.products["raster"]
    assert (
        actual_product.name == "WindNinja Raster Tiles"
    ), "Incorrect job output raster name"
    assert actual_product.package == "tiles.zip", "Incorrect job output raster package"
    assert actual_product.type == "raster", "Incorrect job output raster type"
    assert actual_product.format == "tiles", "Incorrect job output raster format"
    assert len(actual_product.files) == 7, "Incorrect job output raster files length"
    assert (
        actual_product.files[0] == "20171025T1200"
    ), "Incorrect job output raster file[0]"
    assert actual_product.data is not None, "Job output raster data is None"
    assert (
        actual_product.data["maxSpeed"] is not None
    ), "Job output raster data max speed is None"

    assert (
        len(actual_product.data["maxSpeed"].keys()) == 8
    ), "Incorrect job output raster max speed keys length"
    assert (
        actual_product.data["maxSpeed"]["overall"] == 32.541089
    ), "Incorrect job output raster max speed overall value"
    assert (
        actual_product.data["speedBreaks"] is not None
    ), "Job output raster data speed breaks is None"
    assert (
        len(actual_product.data["speedBreaks"]) == 5
    ), "Incorrect job output raster speed breaks keys"


def validate_account(actual):
    # TODO: finish validation
    assert actual is not None, "Account is None"
    assert wnmodels.AccountStatus.accepted == actual.status, "Status is not 'accepted'"
    assert len(actual.devices) == 1, "Device length is not 1"
    assert actual.devices[0] is not None, "Device[0] is None"


def validate_feedback(actual):
    assert actual is not None, "Feedback is None"
    assert actual.id == "5a46dfb6-70c1-400d-8361-f9b9c000ecbd", "Incorrect feedback id"
    assert actual.account == "nwagenbrenner@gmail.com", "Incorrect feedback account"
    assert actual.date_time_stamp == datetime.datetime(
        2015, 12, 16, 14, 10, 54, 455516, dateutil.tz.gettz("America/Denver")
    ), "Incorrect feedback account"
    assert (
        actual.comments == "Does this work? Where is this sent to?\n"
    ), "Incorrect feedback comments"


class MockModels:
    account_json = r'{"id":"nwagenbrenner@gmail.com","email":"nwagenbrenner@gmail.com","name":"Natalie","devices":[{"id":"34168dabe324072c","model":"SAMSUNG-SM-G850A","platform":"Android","version":"5.0.2"}],"createdOn":"2015-12-15T15:34:20.422737-07:00","status":"Accepted"}'
    account_id = "nwagenbrenner@gmail.com"
    account_hash = "bb8f07d34b662c5889bffd2684c647febdde7e092beb897f8d52abf23df21f07"
    device_id = "34168dabe324072c"

    feedback_json = r'{"id":"5a46dfb6-70c1-400d-8361-f9b9c000ecbd","account":"nwagenbrenner@gmail.com","dateTimeStamp":"2015-12-16T14:10:54.4555168-07:00","comments":"Does this work? Where is this sent to?\n"}'
    feedback_id = "5a46dfb6-70c1-400d-8361-f9b9c000ecbd"

    job_id = r"11111111-1111-1111-1111-111111111111"
    job_json = r'{"account": "test@yourdatasmarter.com", "email": "5555555555@vtext.com", "id": "11111111-1111-1111-1111-111111111111", "input": {"domain": {"xmax": -113.97925790543299, "xmin": -114.0235465406869, "ymax": 47.038565315467025, "ymin": 46.99526210560205}, "forecast": "NOMADS-NAM-CONUS-12-KM", "parameters": "forecast_duration:6;vegetation:trees;mesh_choice:fine", "products": "vector:true;raster:true;topofire:true;geopdf:false;clustered:true;weather:true"}, "messages": ["2015-02-27T16:48:45.2949952-07:00 | INFO | job created", "2017-10-25T10:43:02.508000 | INFO | Initializing WindNinja Run", "2017-10-25T10:43:02.579000 | INFO | DEM created", "2017-10-25T10:44:00.881000 | INFO | WindNinjaCLI executed", "2017-10-25T10:44:02.114000 | INFO | Weather converted to geojson", "2017-10-25T10:44:44.107000 | INFO | Output converted to geojson", "2017-10-25T10:44:47.937000 | INFO | TopoFire tiles compiled", "2017-10-25T10:45:03.387000 | INFO | Output converted to cluster", "2017-10-25T10:45:03.537000 | INFO | Complete - total processing: 0:02:01.055000"], "name": "Point Six (test)", "output": {"clustered": {"baseUrl": "", "data": {"maxSpeed": {"20171025T1000.shp": 10.287882, "20171025T1100.shp": 11.524338, "20171025T1200.shp": 17.897222, "20171025T1300.shp": 27.699691, "20171025T1400.shp": 32.205115, "20171025T1500.shp": 31.833992, "20171025T1600.shp": 32.541089, "overall": 32.541089}, "speedBreaks": [6.51, 13.02, 19.52, 26.03, 32.54]}, "files": ["clustered_total.csv"], "format": "csv", "name": "WindNinja Cluster Vectors", "package": "wx_clustered.zip", "type": "cluster"}, "raster": {"data": {"maxSpeed": {"20171025T1000": 10.287882, "20171025T1100": 11.524338, "20171025T1200": 17.897222, "20171025T1300": 27.699691, "20171025T1400": 32.205115, "20171025T1500": 31.833992, "20171025T1600": 32.541089, "overall": 32.541089}, "speedBreaks": [6.51, 13.02, 19.52, 26.03, 32.54]}, "files": ["20171025T1200", "20171025T1300", "20171025T1400", "20171025T1500", "20171025T1600", "20171025T1000", "20171025T1100"], "format": "tiles", "name": "WindNinja Raster Tiles", "package": "tiles.zip", "type": "raster"}, "simulations": {"times": ["20171025T1000", "20171025T1100", "20171025T1200", "20171025T1300", "20171025T1400", "20171025T1500", "20171025T1600"], "utcOffset": "-0600"}, "topofire": {"files": [], "format": "tiles", "name": "TopoFire Basemap", "package": "topofire.zip", "type": "basemap"}, "vector": {"data": {"maxSpeed":{"20171025T1000.json": 10.287882, "20171025T1100.json": 11.524338, "20171025T1200.json": 17.897222, "20171025T1300.json": 27.699691, "20171025T1400.json": 32.205115, "20171025T1500.json": 31.833992, "20171025T1600.json": 32.541089, "overall": 32.541089}}, "files": ["20171025T1200.json", "20171025T1300.json", "20171025T1400.json", "20171025T1500.json", "20171025T1600.json", "20171025T1000.json", "20171025T1100.json"], "format": "json", "name": "WindNinja Json Vectors", "package": "wn_geojson.zip", "type": "vector"}, "weather": {"data": {"maxSpeed": {"WX_20171025T1000.json": 24.730692, "WX_20171025T1100.json": 24.482901, "WX_20171025T1200.json": 25.67851, "WX_20171025T1300.json": 27.620552, "WX_20171025T1400.json": 27.947078, "WX_20171025T1500.json": 24.698765, "WX_20171025T1600.json": 22.06951, "overall": 27.947078}}, "files": ["WX_20171025T1200.json", "WX_20171025T1300.json", "WX_20171025T1400.json", "WX_20171025T1500.json", "WX_20171025T1600.json","WX_20171025T1000.json", "WX_20171025T1100.json"], "format": "json", "name": "Weather Json Vectors", "package": "wx_geojson.zip", "type": "vector"}}, "status": "succeeded"}'


def test_job():
    actual = wnmodels.Job.from_json(MockModels.job_json)
    validate_job(actual)


def test_job_create():
    # completely flat structure
    initiaizer = {
        "name": "this is a test",
        "account": "unknown_account",
        "email": "sendalerts@here.com",
        "xmin": -113.99492384878174,
        "xmax": -113.96402480093018,
        "ymin": 46.831572491414505,
        "ymax": 46.86509153123788,
        "parameters": "duration:5",
        "forecast": "UCAR-NAM-CONUS-12-KM",
        "products": "stuff",
    }

    expected = wnmodels.Job()
    expected.status = wnmodels.JobStatus.new
    expected.name = initiaizer["name"]
    expected.account = initiaizer["account"]
    expected.email = initiaizer["email"]
    expected.input.parameters = initiaizer["parameters"]
    expected.input.products = initiaizer["products"]
    expected.input.forecast = initiaizer["forecast"]
    expected.input.domain.xmin = initiaizer["xmin"]
    expected.input.domain.ymin = initiaizer["ymin"]
    expected.input.domain.xmax = initiaizer["xmax"]
    expected.input.domain.ymax = initiaizer["ymax"]
    expected.add_message("job created", wnmodels.JobMessageType.info)

    actual = wnmodels.Job.create(initiaizer)
    assert_jobs_equal(actual, expected, exact_id=False, exact_messages=False)

    # flat with bbox dict
    initiaizer = {
        "name": "this is a test",
        "account": "unknown_account",
        "email": "sendalerts@here.com",
        "domain": {
            "xmin": -113.99492384878174,
            "xmax": -113.96402480093018,
            "ymin": 46.831572491414505,
            "ymax": 46.86509153123788,
        },
        "parameters": "duration:5",
        "forecast": "UCAR-NAM-CONUS-12-KM",
        "products": "stuff",
    }

    actual = wnmodels.Job.create(initiaizer)
    assert_jobs_equal(actual, expected, exact_id=False, exact_messages=False)

    # structured
    initiaizer = {
        "name": "this is a test",
        "account": "unknown_account",
        "email": "sendalerts@here.com",
        "input": {
            "domain": {
                "xmin": -113.99492384878174,
                "xmax": -113.96402480093018,
                "ymin": 46.831572491414505,
                "ymax": 46.86509153123788,
            },
            "parameters": "duration:5",
            "forecast": "UCAR-NAM-CONUS-12-KM",
            "products": "stuff",
        },
    }

    actual = wnmodels.Job.create(initiaizer)
    assert_jobs_equal(actual, expected, exact_id=False, exact_messages=False)


def test_account():
    actual = wnmodels.Account.from_json(MockModels.account_json)
    validate_account(actual)


def test_account_has_device():
    account = wnmodels.Account.from_json(MockModels.account_json)

    device = wnmodels.Device()
    device.id = MockModels.device_id

    assert account.has_device(device)

    device.id = "NOT FOUND"
    assert not account.has_device(device)


def test_account_generate_code():
    target = wnmodels.Account.from_json(MockModels.account_json)
    expected = MockModels.account_hash
    actual = target.generate_code()

    assert actual == expected, "Incorrect account hash"


def test_feedback():
    actual = wnmodels.Feedback.from_json(MockModels.feedback_json)
    validate_feedback(actual)


def test_feedback_create():
    initializer = {"account": "my@account.com", "comments": "this is a test"}

    expected = wnmodels.Feedback()
    expected.account = initializer["account"]
    expected.comments = initializer["comments"]
    expected.date_time_stamp = datetime.datetime.now()

    actual = wnmodels.Feedback.create(initializer)
    # assert_feedback_equal(actual, expected, exact_id=False, dt_delta=datetime.timedelta(seconds=1))

    # invalid initialier
    initializer = {"wrong": "keys"}
    with pytest.raises(KeyError) as excinfo:
        wnmodels.Feedback.create(initializer)

    assert "account" in str(excinfo.value)


def test_device_create():
    id = "d.id.X"
    model = "d.model.XX"
    platform = "d.platform.XXX"
    version = "d.version.XXXX"

    actual = wnmodels.Device.create(id, model, platform, version)
    assert actual.id == id, "Incorrect device id"
    assert actual.model == model, "Incorrect device model"
    assert actual.platform == platform, "Incorrect device platform"
    assert actual.version == version, "Incorrect device version"

    # requirements validation
    with pytest.raises(ValueError) as excinfo:
        wnmodels.Device.create("", model, platform, version)

    assert "Invalid device id" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        wnmodels.Device.create(1, model, platform, version)

    assert "Invalid device id: <class 'int'>" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        wnmodels.Device.create(id, "", platform, version)

    assert "Invalid device model" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        wnmodels.Device.create(id, 1.1, platform, version)

    assert "Invalid device model: <class 'float'>" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        wnmodels.Device.create(id, model, "", version)

    assert "Invalid device platform" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        wnmodels.Device.create(id, model, {"a": "a"}, version)

    assert "Invalid device platform: <class 'dict'>" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        wnmodels.Device.create(id, model, platform, "")

    assert "Invalid device version" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        wnmodels.Device.create(id, model, platform, ["a"])

    assert "Invalid device version: <class 'list'>" in str(excinfo.value)


# VALIDATORS
def assert_jobs_equal(actual, expected, exact_id=True, exact_messages=True):

    assert actual.id is not None, "Job id is none"
    if exact_id:
        assert actual.id == expected.id, "Incorrect job id"
    else:
        assert re.match(_id_regex, actual.id) is not None, "Incorrect job id format"

    assert actual.name == expected.name, "Incorrect job name"
    assert actual.account == expected.account, "Incorrect job account"
    assert actual.email == expected.email, "Incorrect job email"
    assert actual.status == expected.status, "Incorrect job status"

    if exact_messages:
        assert actual.messages == expected.messages, "Mismatched job messages"
    else:
        assert len(actual.messages) == len(
            expected.messages
        ), "Incorrect job message length"

    if expected.input is None:
        assert actual.input, "Job input is something, expected None"
    else:
        assert actual.input is not None, "Job input is None"
        assert (
            actual.input.forecast == expected.input.forecast
        ), "Incorrect job forecast"
        assert (
            actual.input.parameters == expected.input.parameters
        ), "Incorrect job parameters"
        assert actual.input.products == expected.input.products, "Incorrect job product"

        if expected.input.domain is None:
            assert actual.input.domain is None
        else:
            assert actual.input.domain is not None, "Job input domain is None"
            assert (
                actual.input.domain.xmin == expected.input.domain.xmin
            ), "Incorrect job domain xmin"
            assert (
                actual.input.domain.ymin == expected.input.domain.ymin
            ), "Incorrect job domain ymin"
            assert (
                actual.input.domain.xmax == expected.input.domain.xmax
            ), "Incorrect job domain xmax"
            assert (
                actual.input.domain.ymax == expected.input.domain.ymax
            ), "Incorrect job domain ymax"

    if expected.output is None:
        assert actual.output is None, "Job output is something, expected None"
    else:
        assert actual.output is not None, "Job outputput is None"
        assert len(actual.output.products) == len(
            expected.output.products
        ), "Incorrect job output products length"

        for i, p in enumerate(zip(actual.output.products, expected.output.products)):
            assert type(p[0]) is wnmodels.Product, f"Incorrect product[{i}] class/type"
            assert p[0].name == p[1].name, f"Incorrect job output product[{i}] name"
            assert (
                p[0].package == p[1].package
            ), f"Incorrect job output product[{i}] package"
            assert p[0].type == p[1].type, f"Incorrect job output product[{i}] type"
            assert (
                p[0].format == p[1].format
            ), f"Incorrect job output product[{i}] format"

            assert p[0].files == p[1].files, f"Mismatched job output product[{i}] files"
            assert p[0].data == p[1].data, f"Mismatched job output product[{i}] data"


def assert_feedback_equal(
    actual, expected, exact_id=True, dt_delta=datetime.timedelta(seconds=0)
):
    assert actual.id is not None, "Feedback id is none"
    if exact_id:
        assert actual.id == expected.id, "Incorrect feedback id"
    else:
        assert re.match(_id_regex, actual.id), "Incorrect feedback id format"

    assert actual.account == expected.account, "Incorrect feedback account"
    assert actual.comments == expected.comments, "Incorrect feedback comments"
    assert (
        abs(actual.date_time_stamp - expected.date_time_stamp) <= dt_delta
    ), "Incorrect feedback date time stamp"
