import os
import pytest

from foxha import connection
from foxha.utils import Utils
from test_helpers import BuildEnvironment


@pytest.fixture(scope='module')
def test_dir():
    return os.path.dirname(__file__) + '/'


def test_config_dir():
    return test_dir() + 'config/'


@pytest.fixture(scope='module')
def test_key_path():
    return test_config_dir() + '.test_key'


@pytest.fixture(scope='module')
def test_connection_config_path():
    return test_config_dir() + 'foxha_config.ini'


def test_config_environment():
    return test_config_dir() + 'environment.ini'


def output_log_path():
    return '/tmp/foxha_tests.log'


@pytest.fixture(scope='module')
def environment(path=test_config_environment(), key_path=test_key_path()):
    return BuildEnvironment(path, key_path)


@pytest.fixture(scope='module')
def default_connection():
    return connection.from_config_file(
        Utils.parse_key_file(test_key_path()),
        test_connection_config_path()
    )


@pytest.fixture(scope='module')
def default_logger():
    return Utils.logfile(output_log_path())
