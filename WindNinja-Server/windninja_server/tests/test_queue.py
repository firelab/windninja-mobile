import pytest
import tempfile
import os

import windninjaqueue.queue as wnqueue
from windninjaqueue.enums import QueueMode


@pytest.fixture
def filestore(tmpdir):
    # create a temp directory for the file store and initialize i
    filestore = tmpdir
    config = {"datastore": filestore, "mode": "enabled"}
    wnqueue.set_Queue(config, initialize=False)

    f = tmpdir.join("00000000-0000-0000-0000-000000000001.pending")
    f.write("")

    f = tmpdir.join("00000000-0000-0000-0000-000000000002.running")
    f.write("")

    f = tmpdir.join("00000000-0000-0000-0000-000000000003.complete")
    f.write("")

    return filestore


def test_enabled_enqueue(filestore):
    id = "00000000-0000-0000-0000-000000000000"
    status = wnqueue.QueueStatus.pending
    wnqueue.enqueue(id)

    expected_file = os.path.join(wnqueue._directories["queue"], f"{id}.{status.name}")
    assert os.path.exists(expected_file), f"Expected file not found: {expected_file}"

    with pytest.raises(KeyError) as excinfo:
        wnqueue.enqueue(id)

    expected_error_message = f"Item with id {id} already exists in queue"
    assert expected_error_message in str(excinfo.value)


def test_disabled_enqueue(filestore):
    config = {"datastore": filestore, "mode": "disabled"}
    wnqueue.set_Queue(config, initialize=False)

    id = "00000000-0000-0000-0000-000000000000"
    status = wnqueue.QueueStatus.pending
    wnqueue.enqueue(id)

    unexpected_file = os.path.join(wnqueue._directories["queue"], f"{id}.{status.name}")
    assert not os.path.exists(
        unexpected_file
    ), f"Unexpected file found: {expected_file}"


def test_dequeue(filestore):
    id = "00000000-0000-0000-0000-000000000002"
    status = wnqueue.QueueStatus.complete
    fh = filestore.join(f"{id}.running")
    assert fh.read() == ""

    wnqueue.dequeue(id, data="foo")

    # Confirm original .running file was renamed/moved to .complete
    unexpected_file = os.path.join(wnqueue._directories["queue"], f"{id}.running")
    assert not os.path.exists(
        unexpected_file
    ), f"Unexpected file found: {unexpected_file}"

    # Confirm that data was written to the .complete job file
    fh = filestore.join(f"{id}.complete")
    assert fh.read() == "foo\n"


def test_disabled_dequeue(filestore):
    config = {"datastore": filestore, "mode": "disabled"}
    wnqueue.set_Queue(config, initialize=False)

    id = "00000000-0000-0000-0000-000000000002"
    status = wnqueue.QueueStatus.complete
    fh = filestore.join(f"{id}.running")
    assert fh.read() == ""

    wnqueue.dequeue(id, data="foo")

    # Confirm original .running file was not modified
    expected_file = os.path.join(wnqueue._directories["queue"], f"{id}.running")
    assert os.path.exists(expected_file), f"Expected file not found: {expected_file}"

    # Confirm data was not written to the job status file
    fh = filestore.join(f"{id}.running")
    assert fh.read() == ""


def test_update_queue_item_status(filestore):
    id = "00000000-0000-0000-0000-000000000001"
    status = wnqueue.QueueStatus.running

    fh = filestore.join(f"{id}.pending")
    assert fh.read() == ""

    wnqueue.update_queue_item_status(id, status, data="test data")

    # Confirm status file was renamed from .pending to .running
    expected_file = os.path.join(wnqueue._directories["queue"], f"{id}.{status.name}")
    assert os.path.exists(expected_file), f"Expected file not found: {expected_file}"

    # Confirm data was written to the job status file
    fh = filestore.join(f"{id}.running")
    assert fh.read() == "test data\n"


def test_update_queue_item_status_bad_id(filestore):
    bad_id = "00000000-0000-0000-0000-000000000005"
    status = wnqueue.QueueStatus.running

    with pytest.raises(KeyError) as excinfo:
        wnqueue.update_queue_item_status(bad_id, status)

    expected_error_message = f"Item with id {bad_id} not found in queue"
    assert expected_error_message in str(excinfo.value)


def test_update_queue_item_status_bad_type(filestore):
    id = "00000000-0000-0000-0000-000000000001"

    with pytest.raises(TypeError) as excinfo:
        wnqueue.update_queue_item_status(id, "incorect status type")

    expected_error_message = "Status is not of type <QueueStatus>"
    assert expected_error_message in str(excinfo.value)


def test_find_items_by_status_pending(filestore):
    status = wnqueue.QueueStatus.pending
    results = wnqueue.find_items_by_status(status)

    assert len(results) == 1
    assert results[0]["id"] == "00000000-0000-0000-0000-000000000001"


def test_find_items_by_status_running(filestore):
    status = wnqueue.QueueStatus.running
    results = wnqueue.find_items_by_status(status)

    assert len(results) == 1
    assert results[0]["id"] == "00000000-0000-0000-0000-000000000002"


def test_find_items_by_status_complete(filestore):
    status = wnqueue.QueueStatus.complete
    results = wnqueue.find_items_by_status(status)

    assert len(results) == 1
    assert results[0]["id"] == "00000000-0000-0000-0000-000000000003"
