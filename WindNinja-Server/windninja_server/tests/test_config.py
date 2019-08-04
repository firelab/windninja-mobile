import pytest


yaml_string = """
auto_register:
    domains:
        - fs.fed.us
        - yourdatasmarter.com
    emails:
        - someone@mail.com
        - me@mail.com
    mode: EMAILS
datastore: C:/WindNinjaServer/Data
mail:
    from_address: from_account@mail.com
queue:
    datastore: C:/WindNinjaServer/Data/Queue
    loop_interval: 5
    max_running_jobs: 5
    python_executable: C:/python.exe
    windninja_wrapper: C:/WindNinjaServer/windninja.py
"""


@pytest.fixture
def config(tmpdir, monkeypatch):
    # create a temp directory for the file store and initialize it
    fh = tmpdir.join("config.yaml")
    fh.write(yaml_string)

    monkeypatch.setenv("WNSERVER_CONFIG", str(fh))
    monkeypatch.setenv("AWS_SMTP_HOST", "smtp.mail.com:587")
    monkeypatch.setenv("AWS_SMTP_KEY", "admin_account@mail.com")
    monkeypatch.setenv("AWS_SMTP_SECRET", "pwd4mail")

    return fh


def test_config(config):
    import windninjaconfig as wnconfig

    assert (
        wnconfig.Config.DATASTORE == "C:/WindNinjaServer/Data"
    ), "Incorrect DATASTORE value"

    assert wnconfig.Config.MAIL is not None, "MAIL is None"
    assert wnconfig.Config.MAIL["server"] is not None, "MAIL server is None"
    assert (
        wnconfig.Config.MAIL["server"]["address"] == "smtp.mail.com:587"
    ), "Incorrect MAIL server address value"
    assert (
        wnconfig.Config.MAIL["server"]["user"] == "admin_account@mail.com"
    ), "Incorrect MAIL server user value"
    assert (
        wnconfig.Config.MAIL["server"]["password"] == "pwd4mail"
    ), "Incorrect MAIL server password value"
    assert (
        wnconfig.Config.MAIL["from_address"] == "from_account@mail.com"
    ), "Incorrect MAIL from address value"

    assert wnconfig.Config.AUTO_REGISTER is not None, "AUTO_REGISTER is None"
    assert wnconfig.Config.AUTO_REGISTER["mode"] in (
        "ALL",
        "EMAILS",
        "NONE",
    ), "Invalid AUTO_REGISTER mode value"
    assert (
        wnconfig.Config.AUTO_REGISTER["domains"] is not None
    ), "AUTO_REGISTER domains is None"
    assert wnconfig.Config.AUTO_REGISTER["domains"] == [
        "fs.fed.us",
        "yourdatasmarter.com",
    ], "Mismatched AUTO_REGISTER domains list"
    assert (
        wnconfig.Config.AUTO_REGISTER["emails"] is not None
    ), "AUTO_REGISTER emails is None"
    assert wnconfig.Config.AUTO_REGISTER["emails"] == [
        "someone@mail.com",
        "me@mail.com",
    ], "Mismatched AUTO_REGISTER emails list"

    assert wnconfig.Config.QUEUE is not None, "QUEUE is None"
    assert (
        wnconfig.Config.QUEUE["datastore"] == "C:/WindNinjaServer/Data/Queue"
    ), "Invalid QUEUE datastore value"
    assert (
        wnconfig.Config.QUEUE["max_running_jobs"] == 5
    ), "Invalid QUEUE max_running_jobs value"
    assert (
        wnconfig.Config.QUEUE["loop_interval"] == 5
    ), "Invalid QUEUE loop_interval value"
    assert (
        wnconfig.Config.QUEUE["python_executable"] == "C:/python.exe"
    ), "Invalid QUEUE python_executable value"
    assert (
        wnconfig.Config.QUEUE["windninja_wrapper"] == "C:/WindNinjaServer/windninja.py"
    ), "Invalid QUEUE windninja_wrapper value"
