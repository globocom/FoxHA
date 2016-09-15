# -*- coding: utf-8 -*-
import pytest
from foxha.utils import Utils
import foxha.connection


@pytest.fixture
def logger():
    import logging
    return logging.getLogger(__name__)


def test_open_new_connection_succeds(test_key_path):
    assert foxha.connection.Connection(
        'localhost', 3306, '', 'root', '',
        Utils.parse_key_file(test_key_path)
    ).connect()


def test_connection_from_config_file():
    conn = foxha.connection.from_config_file()
    assert conn.connect()
