import windninjaweb.models as wnmodels
import unittest
import datetime
import dateutil

_id_regex = "\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"


def validate_job(actual):
    assert actual is not None, "Job is None"
    assert actual.account == "test@yourdatasmarter.com", "Incorrect job account"

    assert actual.name == "Point Six (test)", "Incorrect job name"
    assert actual.status == wnmodels.JobStatus.succeeded, "Incorrect job status"
    assert actual.id == "11111111-1111-1111-1111-111111111111", "Incorrect job id"
    assert actual.email == "5555555555@vtext.com", "Incorrect job email"

    assert actual.messages is not None, "Job messages is None"
    assert len(actual.messages) == 9, "Incorrect job messages length"
    #TODO: test some messages or split each to verify format

    assert actual.input is not None, "Job input is None"
    assert actual.input.products == "vector:true;raster:true;topofire:true;geopdf:false;clustered:true;weather:true", "Incorrect job input products"
    assert actual.input.parameters == "forecast_duration:6;vegetation:trees;mesh_choice:fine", "Incorrect job input parameters"
    assert actual.input.forecast == "NOMADS-NAM-CONUS-12-KM", "Incorrect job forecast"

    assert actual.input.domain is not None, "Job input domain is None"
    assert actual.input.domain.xmax == -113.97925790543299, "Incorrect job input domain xmax"
    assert actual.input.domain.ymax == 47.038565315467025, "Incorrect job input domain ymax"
    assert actual.input.domain.xmin == -114.0235465406869, "Incorrect job input domain xmin"
    assert actual.input.domain.ymin == 46.99526210560205, "Incorrect job input domain ymin"

    assert actual.output is not None, "Job output is None"
    #assert actual.output.products is not None, "Job output products is None"
    #assert len(actual.output.products) == 4, "Incorrect job output products length"

    assert actual.output.simulations is not None, "Job output simulation is None"
    assert actual.output.products is not None, "Job output products is None"
    assert len(actual.output.products.keys()) == 5, "Incorrect job output products length"

    assert actual.output.products["vector"] is not None, "Job output product vector is None"
    assert actual.output.products["topofire"] is not None, "Job output product topofire is None"
    assert actual.output.products["clustered"] is not None, "Job output product clustered is None"
    assert actual.output.products["weather"] is not None, "Job output product weather is None"
    assert actual.output.products["raster"] is not None, "Job output product raster is None"

    #actual_product = actual.output.products[0]
    #context.assertIsNotNone(actual_product, msg="Job output product[0] is None")
    #TODO: test others are not None
    #context.assertEqual(actual_product.name, "WindNinja Raster Tiles", msg="Incorrect job output product[0] name")
    #context.assertEqual(actual_product.package, "tiles.zip", msg="Incorrect job output product[0] package")
    #context.assertEqual(actual_product.type, "raster", msg="Incorrect job output product[0] type")
    #context.assertEqual(actual_product.format, "tiles", msg="Incorrect job output product[0] format")

    #context.assertEqual(len(actual_product.files), 4, "Incorrect job output product[0] files length")
    #context.assertEqual(actual_product.files[0], "dem_12-15-2015_1700_29m", msg="Incorrect job output product[0] file[0]")

    #context.assertEqual(len(actual_product.data), 4, "Incorrect job output product[0] data length")
    #context.assertEqual(actual_product.data[0], "dem_12-15-2015_1700_29m:24.722978", msg="Incorrect job output product[0] data[0]")

    #TODO: test other products

    actual_product = actual.output.products["raster"]
    assert actual_product.name == "WindNinja Raster Tiles", "Incorrect job output raster name"
    assert actual_product.package == "tiles.zip", "Incorrect job output raster package"
    assert actual_product.type == "raster", "Incorrect job output raster type"
    assert actual_product.format ==  "tiles", "Incorrect job output raster format"
    assert len(actual_product.files) == 7, "Incorrect job output raster files length"
    assert actual_product.files[0] == "20171025T1200", "Incorrect job output raster file[0]"
    assert actual_product.data is not None, "Job output raster data is None"
    assert actual_product.data["maxSpeed"] is not None, "Job output raster data max speed is None"

    assert len(actual_product.data["maxSpeed"].keys()) == 8, "Incorrect job output raster max speed keys length"
    assert actual_product.data["maxSpeed"]["overall"] == 32.541089, "Incorrect job output raster max speed overall value"
    assert actual_product.data["speedBreaks"] is not None, "Job output raster data speed breaks is None"
    assert len(actual_product.data["speedBreaks"]) == 5, "Incorrect job output raster speed breaks keys"


def validate_account(actual):
    #TODO: finish validation
    assert actual is not None, "Account is None"
    assert wnmodels.AccountStatus.accepted == actual.status, "Status is not 'accepted'"
    assert len(actual.devices) == 1, "Device length is not 1"
    assert actual.devices[0] is not None, "Device[0] is None"


def validate_feedback(actual):
    assert actual is not None, "Feedback is None"
    assert actual.id == "5a46dfb6-70c1-400d-8361-f9b9c000ecbd", "Incorrect feedback id"
    assert actual.account == "nwagenbrenner@gmail.com", "Incorrect feedback account"
    assert actual.date_time_stamp == datetime.datetime(2015, 12, 16, 14, 10, 54, 455516, dateutil.tz.gettz("America/Denver")), "Incorrect feedback account"
    assert actual.comments == "Does this work? Where is this sent to?\n", "Incorrect feedback comments"


class MockModels:
    account_json = r'{"id":"nwagenbrenner@gmail.com","email":"nwagenbrenner@gmail.com","name":"Natalie","devices":[{"id":"34168dabe324072c","model":"SAMSUNG-SM-G850A","platform":"Android","version":"5.0.2"}],"createdOn":"2015-12-15T15:34:20.422737-07:00","status":"Accepted"}'
    account_id = "nwagenbrenner@gmail.com"
    account_hash = "bb8f07d34b662c5889bffd2684c647febdde7e092beb897f8d52abf23df21f07"
    device_id = "34168dabe324072c"

    feedback_json = r'{"id":"5a46dfb6-70c1-400d-8361-f9b9c000ecbd","account":"nwagenbrenner@gmail.com","dateTimeStamp":"2015-12-16T14:10:54.4555168-07:00","comments":"Does this work? Where is this sent to?\n"}'
    feedback_id = "5a46dfb6-70c1-400d-8361-f9b9c000ecbd"

    job_json = r'{"account": "test@yourdatasmarter.com", "email": "5555555555@vtext.com", "id": "11111111-1111-1111-1111-111111111111", "input": {"domain": {"xmax": -113.97925790543299, "xmin": -114.0235465406869, "ymax": 47.038565315467025, "ymin": 46.99526210560205}, "forecast": "NOMADS-NAM-CONUS-12-KM", "parameters": "forecast_duration:6;vegetation:trees;mesh_choice:fine", "products": "vector:true;raster:true;topofire:true;geopdf:false;clustered:true;weather:true"}, "messages": ["2015-02-27T16:48:45.2949952-07:00 | INFO | job created", "2017-10-25T10:43:02.508000 | INFO | Initializing WindNinja Run", "2017-10-25T10:43:02.579000 | INFO | DEM created", "2017-10-25T10:44:00.881000 | INFO | WindNinjaCLI executed", "2017-10-25T10:44:02.114000 | INFO | Weather converted to geojson", "2017-10-25T10:44:44.107000 | INFO | Output converted to geojson", "2017-10-25T10:44:47.937000 | INFO | TopoFire tiles compiled", "2017-10-25T10:45:03.387000 | INFO | Output converted to cluster", "2017-10-25T10:45:03.537000 | INFO | Complete - total processing: 0:02:01.055000"], "name": "Point Six (test)", "output": {"clustered": {"baseUrl": "", "data": {"maxSpeed": {"20171025T1000.shp": 10.287882, "20171025T1100.shp": 11.524338, "20171025T1200.shp": 17.897222, "20171025T1300.shp": 27.699691, "20171025T1400.shp": 32.205115, "20171025T1500.shp": 31.833992, "20171025T1600.shp": 32.541089, "overall": 32.541089}, "speedBreaks": [6.51, 13.02, 19.52, 26.03, 32.54]}, "files": ["clustered_total.csv"], "format": "csv", "name": "WindNinja Cluster Vectors", "package": "wx_clustered.zip", "type": "cluster"}, "raster": {"data": {"maxSpeed": {"20171025T1000": 10.287882, "20171025T1100": 11.524338, "20171025T1200": 17.897222, "20171025T1300": 27.699691, "20171025T1400": 32.205115, "20171025T1500": 31.833992, "20171025T1600": 32.541089, "overall": 32.541089}, "speedBreaks": [6.51, 13.02, 19.52, 26.03, 32.54]}, "files": ["20171025T1200", "20171025T1300", "20171025T1400", "20171025T1500", "20171025T1600", "20171025T1000", "20171025T1100"], "format": "tiles", "name": "WindNinja Raster Tiles", "package": "tiles.zip", "type": "raster"}, "simulations": {"times": ["20171025T1000", "20171025T1100", "20171025T1200", "20171025T1300", "20171025T1400", "20171025T1500", "20171025T1600"], "utcOffset": "-0600"}, "topofire": {"files": [], "format": "tiles", "name": "TopoFire Basemap", "package": "topofire.zip", "type": "basemap"}, "vector": {"data": {"maxSpeed": {"20171025T1000.json": 10.287882, "20171025T1100.json": 11.524338, "20171025T1200.json": 17.897222, "20171025T1300.json": 27.699691, "20171025T1400.json": 32.205115, "20171025T1500.json": 31.833992, "20171025T1600.json": 32.541089, "overall": 32.541089}}, "files": ["20171025T1200.json", "20171025T1300.json", "20171025T1400.json", "20171025T1500.json", "20171025T1600.json", "20171025T1000.json", "20171025T1100.json"], "format": "json", "name": "WindNinja Json Vectors", "package": "wn_geojson.zip", "type": "vector"}, "weather": {"data": {"maxSpeed": {"WX_20171025T1000.json": 24.730692, "WX_20171025T1100.json": 24.482901, "WX_20171025T1200.json": 25.67851, "WX_20171025T1300.json": 27.620552, "WX_20171025T1400.json": 27.947078, "WX_20171025T1500.json": 24.698765, "WX_20171025T1600.json": 22.06951, "overall": 27.947078}}, "files": ["WX_20171025T1200.json", "WX_20171025T1300.json", "WX_20171025T1400.json", "WX_20171025T1500.json", "WX_20171025T1600.json", "WX_20171025T1000.json", "WX_20171025T1100.json"], "format": "json", "name": "Weather Json Vectors", "package": "wx_geojson.zip", "type": "vector"}}, "status": "succeeded"}'
    job_id = r"11111111-1111-1111-1111-111111111111"

    @classmethod
    def validate_job(cls, context, actual):
        context.assertIsNotNone(actual, "Job is None")
        context.assertEqual(actual.account, "test@yourdatasmarter.com", msg="Incorrect job account")
        context.assertEqual(actual.name, "Point Six (test)", msg="Incorrect job name")
        context.assertEqual(actual.status, wnmodels.JobStatus.succeeded, msg="Incorrect job status")
        context.assertEqual(actual.id, "11111111-1111-1111-1111-111111111111", msg="Incorrect job id")
        context.assertEqual(actual.email, "5555555555@vtext.com", msg="Incorrect job email")

        context.assertIsNotNone(actual.messages, "Job messages is None")
        context.assertEqual(len(actual.messages), 9, "Incorrect job messages length")
        #TODO: test some messages or split each to verify format

        context.assertIsNotNone(actual.input, "Job input is None")
        context.assertEqual(actual.input.products, "vector:true;raster:true;topofire:true;geopdf:false;clustered:true;weather:true", msg="Incorrect job input products")
        context.assertEqual(actual.input.parameters, "forecast_duration:6;vegetation:trees;mesh_choice:fine", msg="Incorrect job input parameters")
        context.assertEqual(actual.input.forecast, "NOMADS-NAM-CONUS-12-KM", msg="Incorrect job forecast")
        context.assertIsNotNone(actual.input.domain, "Job input domain is None")
        context.assertEqual(actual.input.domain.xmax, -113.97925790543299, msg="Incorrect job input domain xmax")
        context.assertEqual(actual.input.domain.ymax, 47.038565315467025, msg="Incorrect job input domain ymax")
        context.assertEqual(actual.input.domain.xmin, -114.0235465406869, msg="Incorrect job input domain xmin")
        context.assertEqual(actual.input.domain.ymin, 46.99526210560205, msg="Incorrect job input domain ymin")

        context.assertIsNotNone(actual.output, "Job output is None")
        #context.assertIsNotNone(actual.output.products, "Job output products is None")
        #context.assertEqual(len(actual.output.products), 4, "Incorrect job output products length")

        context.assertIsNotNone(actual.output.simulations, "Job output simulation is None")
        context.assertIsNotNone(actual.output.products, "Job output products is None")
        context.assertEqual(len(actual.output.products.keys()), 5, "Incorrect job output products length")

        context.assertIsNotNone(actual.output.products["vector"], "Job output product vector is None")
        context.assertIsNotNone(actual.output.products["topofire"], "Job output product topofire is None")
        context.assertIsNotNone(actual.output.products["clustered"], "Job output product clustered is None")
        context.assertIsNotNone(actual.output.products["weather"], "Job output product weather is None")
        context.assertIsNotNone(actual.output.products["raster"], "Job output product raster is None")

        #actual_product = actual.output.products[0]
        #context.assertIsNotNone(actual_product, msg="Job output product[0] is None")
        #TODO: test others are not None
        #context.assertEqual(actual_product.name, "WindNinja Raster Tiles", msg="Incorrect job output product[0] name")
        #context.assertEqual(actual_product.package, "tiles.zip", msg="Incorrect job output product[0] package")
        #context.assertEqual(actual_product.type, "raster", msg="Incorrect job output product[0] type")
        #context.assertEqual(actual_product.format, "tiles", msg="Incorrect job output product[0] format")

        #context.assertEqual(len(actual_product.files), 4, "Incorrect job output product[0] files length")
        #context.assertEqual(actual_product.files[0], "dem_12-15-2015_1700_29m", msg="Incorrect job output product[0] file[0]")

        #context.assertEqual(len(actual_product.data), 4, "Incorrect job output product[0] data length")
        #context.assertEqual(actual_product.data[0], "dem_12-15-2015_1700_29m:24.722978", msg="Incorrect job output product[0] data[0]")

        #TODO: test other products

        actual_product = actual.output.products["raster"]
        context.assertEqual(actual_product.name, "WindNinja Raster Tiles", msg="Incorrect job output raster name")
        context.assertEqual(actual_product.package, "tiles.zip", msg="Incorrect job output raster package")
        context.assertEqual(actual_product.type, "raster", msg="Incorrect job output raster type")
        context.assertEqual(actual_product.format, "tiles", msg="Incorrect job output raster format")
        context.assertEqual(len(actual_product.files), 7, "Incorrect job output raster files length")
        context.assertEqual(actual_product.files[0], "20171025T1200", msg="Incorrect job output raster file[0]")
        context.assertIsNotNone(actual_product.data, "Job output raster data is None")
        context.assertIsNotNone(actual_product.data["maxSpeed"], "Job output raster data max speed is None")
        context.assertEqual(len(actual_product.data["maxSpeed"].keys()), 8, msg="Incorrect job output raster max speed keys length")
        context.assertEqual(actual_product.data["maxSpeed"]["overall"], 32.541089, msg="Incorrect job output raster max speed overall value")
        context.assertIsNotNone(actual_product.data["speedBreaks"], "Job output raster data speed breaks is None")
        context.assertEqual(len(actual_product.data["speedBreaks"]), 5, msg="Incorrect job output raster speed breaks keys")

class TestModels(unittest.TestCase):

    #TODO: add other scenarios

    def setUp(self):
        pass

    def test_job(self):
        actual = wnmodels.Job.from_json(MockModels.job_json)
        MockModels.validate_job(self, actual)


    def test_job_create(self):
        # completely flat structure
        initiaizer = {
            "name": "this is a test", "account" : "unknown_account", "email" : "sendalerts@here.com",
            "xmin" : -113.99492384878174, "ymin" : 46.831572491414505, "ymax" : 46.86509153123788, "xmax" : -113.96402480093018,
            "parameters" : "duration:5", "forecast" : "UCAR-NAM-CONUS-12-KM", "products" : "stuff" }

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
        self.validate_job(actual, expected, exact_id=False, exact_messages=False)

        # flat with bbox dict
        initiaizer = {
            "name": "this is a test", "account" : "unknown_account", "email" : "sendalerts@here.com",
            "domain": {"xmin" : -113.99492384878174, "ymin" : 46.831572491414505, "ymax" : 46.86509153123788, "xmax" : -113.96402480093018},
            "parameters" : "duration:5", "forecast" : "UCAR-NAM-CONUS-12-KM", "products" : "stuff" }

        actual = wnmodels.Job.create(initiaizer)
        self.validate_job(actual, expected, exact_id=False, exact_messages=False)

        # structured
        initiaizer = {
            "name": "this is a test", "account" : "unknown_account", "email" : "sendalerts@here.com",
            "input" : {
            "domain": {"xmin" : -113.99492384878174, "ymin" : 46.831572491414505, "ymax" : 46.86509153123788, "xmax" : -113.96402480093018},
            "parameters" : "duration:5", "forecast" : "UCAR-NAM-CONUS-12-KM", "products" : "stuff" }}

        actual = wnmodels.Job.create(initiaizer)
        self.validate_job(actual, expected, exact_id=False, exact_messages=False)

    def test_account(self):
        actual = wnmodels.Account.from_json(MockModels.account_json)
        MockModels.validate_account(self, actual)

    def test_account_has_device(self):
        account = wnmodels.Account.from_json(MockModels.account_json)

        device = wnmodels.Device()
        device.id = MockModels.device_id

        self.assertTrue(account.has_device(device))

        device.id = "NOT FOUND"
        self.assertFalse(account.has_device(device))

    def test_account_generate_code(self):
        target = wnmodels.Account.from_json(MockModels.account_json)
        expected = MockModels.account_hash
        actual = target.generate_code()

        self.assertEqual(actual, expected, "Incorrect account hash")

    def test_feedback(self):
        actual  = wnmodels.Feedback.from_json(MockModels.feedback_json)
        MockModels.validate_feedback(self, actual)

    def test_feedback_create(self):
        initializer = {
                "account": "my@account.com",
                "comments": "this is a test"
            }

        expected = wnmodels.Feedback()
        expected.account = initializer["account"]
        expected.comments = initializer["comments"]
        expected.date_time_stamp = datetime.datetime.now()

        actual = wnmodels.Feedback.create(initializer)
        self.validate_feedback(actual, expected, exact_id=False, dt_delta=datetime.timedelta(seconds=1))

        # invalid initialier
        initializer = {
            "wrong": "keys"
        }
        with self.assertRaises(KeyError):
            wnmodels.Feedback.create(initializer)

    def test_device_create(self):
        target = wnmodels.Device.create

        id = "d.id.X"
        model = "d.model.XX"
        platform = "d.platform.XXX"
        version = "d.version.XXXX"

        actual = target(id, model, platform, version)
        self.assertEqual(actual.id, id, "Incorrect device id")
        self.assertEqual(actual.model, model, "Incorrect device model")
        self.assertEqual(actual.platform, platform, "Incorrect device platform")
        self.assertEqual(actual.version, version, "Incorrect device version")

        # requirements validation
        self.assertRaisesRegex(ValueError, "Invalid device id: ", target, "", model, platform, version)
        self.assertRaisesRegex(TypeError, "Invalid device id: <class 'int'>", target, 1, model, platform, version)

        self.assertRaisesRegex(ValueError, "Invalid device model: ", target, id, "", platform, version)
        self.assertRaisesRegex(TypeError, "Invalid device model: <class 'float'>", target, id, 1.1, platform, version)

        self.assertRaisesRegex(ValueError, "Invalid device platform: ", target, id, model, "", version)
        self.assertRaisesRegex(TypeError, "Invalid device platform: <class 'dict'>", target, id, model, {"a": "a"}, version)

        self.assertRaisesRegex(ValueError, "Invalid device version: ", target, id, model, platform, "")
        self.assertRaisesRegex(TypeError, "Invalid device version: <class 'list'>", target, id, model, platform, ["a"])


    #VALIDATORS
    def validate_job(self, actual, expected, exact_id=True, exact_messages=True):

        self.assertIsNotNone(actual.id,  msg="Job id is none")
        if exact_id:
            self.assertEqual(actual.id, expected.id, msg="Incorrect job id")
        else:
            self.assertRegex(actual.id, _id_regex, msg="Incorrect job id format")

        self.assertEqual(actual.name, expected.name, msg="Incorrect job name")
        self.assertEqual(actual.account, expected.account, msg="Incorrect job account")
        self.assertEqual(actual.email, expected.email, msg="Incorrect job email")
        self.assertEqual(actual.status, expected.status, msg="Incorrect job status")

        if exact_messages:
            self.assertListEqual(actual.messages, expected.messages, msg="Mismatched job messages")
        else:
            self.assertEqual(len(actual.messages), len(expected.messages), msg="Incorrect job message length")

        if (expected.input is None):
            self.assertIsNone(actual.input, "Job input is something, expected None")
        else:
            self.assertIsNotNone(actual.input, msg="Job input is None")
            self.assertEqual(actual.input.forecast, expected.input.forecast, msg="Incorrect job forecast")
            self.assertEqual(actual.input.parameters, expected.input.parameters, msg="Incorrect job parameters")
            self.assertEqual(actual.input.products, expected.input.products, msg="Incorrect job product")

            if (expected.input.domain is None):
                self.assertIsNone(actual.input.domain)
            else:
                self.assertIsNotNone(actual.input.domain, msg="Job input domain is None")
                self.assertEqual(actual.input.domain.xmin, expected.input.domain.xmin, msg="Incorrect job domain xmin")
                self.assertEqual(actual.input.domain.ymin, expected.input.domain.ymin, msg="Incorrect job domain ymin")
                self.assertEqual(actual.input.domain.xmax, expected.input.domain.xmax, msg="Incorrect job domain xmax")
                self.assertEqual(actual.input.domain.ymax, expected.input.domain.ymax, msg="Incorrect job domain ymax")

        if (expected.output is None):
            self.assertIsNone(actual.output, "Job output is something, expected None")
        else:
            self.assertIsNotNone(actual.output, msg="Job outputput is None")
            self.assertEqual(len(actual.output.products), len(expected.output.products), "Incorrect job output products length")

            i=0
            for p in zip(actual.output.products, expected.output.products):
                self.assertIs(type(p[0]), wnmodels.Product, msg="Incorrect product[{}] class/type".format(i))
                self.assertEqual(p[0].name, p[1].name, msg="Incorrect job output product[{}] name".format(i))
                self.assertEqual(p[0].package, p[1].package, msg="Incorrect job output product[{}] package".format(i))
                self.assertEqual(p[0].type, p[1].type, msg="Incorrect job output product[{}] type".format(i))
                self.assertEqual(p[0].format, p[1].format, msg="Incorrect job output product[{}] format".format(i))

                self.assertListEqual(p[0].files, p[1].files, msg="Mismatched job output product[{}] files".format(i))
                self.assertListEqual(p[0].data, p[1].data, msg="Mismatched job output product[{}] data".format(i))

                i+=1

    def validate_feedback(self, actual, expected, exact_id=True, dt_delta=datetime.timedelta(seconds=0)):
        self.assertIsNotNone(actual.id,  msg="Feedback id is none")
        if exact_id:
            self.assertEqual(actual.id, expected.id, msg="Incorrect feedback id")
        else:
            self.assertRegex(actual.id, _id_regex , msg="Incorrect feedback id format")

        self.assertEqual(actual.account, expected.account, msg="Incorrect feedback account")
        self.assertEqual(actual.comments, expected.comments, msg="Incorrect feedback comments")
        self.assertAlmostEqual(actual.date_time_stamp, expected.date_time_stamp, delta=dt_delta, msg="Incorrect feedback date time stamp")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
