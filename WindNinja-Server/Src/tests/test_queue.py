import unittest
import tempfile
import os

import windninjaqueue.queue as wnqueue

class TestQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a temp directory for the file store and initialize it
        cls._store = tempfile.TemporaryDirectory()
        wnqueue.set_Queue(cls._store.name, False)
        
        open(os.path.join(cls._store.name, "00000000-0000-0000-0000-000000000001.pending"), "x").close()
        open(os.path.join(cls._store.name, "00000000-0000-0000-0000-000000000002.running"), "x").close()
        open(os.path.join(cls._store.name, "00000000-0000-0000-0000-000000000003.complete"), "x").close()
        
    def test_enqueue(self):
        id = "00000000-0000-0000-0000-000000000000"
        status = wnqueue.QueueStatus.pending
        wnqueue.enqueue(id)

        expected_file = os.path.join(wnqueue._directories["queue"], "{0}.{1}".format(id, status.name))
        self.assertTrue(os.path.exists(expected_file), "Expected file not found: {}".format(expected_file))

        # raises KEYERROR
        expected_error_message = "Item with id {} already exists in queue".format(id)
        with self.assertRaisesRegex(KeyError, expected_error_message):
            wnqueue.enqueue(id)

    def test_dequeue(self):
        id = "00000000-0000-0000-0000-000000000003"
        status = wnqueue.QueueStatus.complete
        wnqueue.dequeue(id)

        unexpected_file = os.path.join(wnqueue._directories["queue"], "{0}.{1}".format(id, status.name))
        self.assertFalse(os.path.exists(unexpected_file), "Unexpected file not found: {}".format(unexpected_file))

        # raises KEYERROR
        expected_error_message = "Item with id {} not found in queue".format(id)
        with self.assertRaisesRegex(KeyError, expected_error_message):
            wnqueue.dequeue(id)

    def test_update_queue_item_status(self):
        id = "00000000-0000-0000-0000-000000000001"
        status = wnqueue.QueueStatus.running
        wnqueue.update_queue_item_status(id, status, "test data")

        expected_file = os.path.join(wnqueue._directories["queue"], "{0}.{1}".format(id, status.name))
        self.assertTrue(os.path.exists(expected_file), "Expected file not found: {}".format(expected_file))

        #TODO: read file data

        # raises KEYERROR
        bad_id = "00000000-0000-0000-0000-000000000005"
        expected_error_message = "Item with id {} not found in queue".format(bad_id)
        with self.assertRaisesRegex(KeyError, expected_error_message):
            wnqueue.update_queue_item_status(bad_id, status)

        # raises TYPEEERROR
        expected_error_message = "Status is not of type <QueueStatus>"
        with self.assertRaisesRegex(TypeError, expected_error_message):
            wnqueue.update_queue_item_status(id, "incorect status type")


    @classmethod
    def tearDownClass(cls):
        cls._store.cleanup()

if __name__ == '__main__':
    unittest.main()