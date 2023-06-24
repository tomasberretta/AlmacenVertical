import random
import time
import unittest.mock as mock


def random_readline():
    time.sleep(1)
    if random.random() < 0.25:
        return b"OK"
    else:
        return b"some data"


def get_serial_mock():
    serial_mock = mock.Mock()
    serial_mock.write = mock.Mock()
    serial_mock.readline = mock.Mock()
    serial_mock.readline.side_effect = random_readline
    serial_mock.write.return_value = None
    return serial_mock
