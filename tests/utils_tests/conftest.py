import os
import pytest
import ConfigParser
from foxha.utils import Utils


@pytest.fixture(scope='module')
def utils():
    return Utils()


@pytest.fixture(scope='module')
def cipher_suite(utils, test_key_path):
    return utils.parse_key_file(keyfile=test_key_path)


@pytest.fixture(scope='module')
def config_files_dir_utils(test_dir):
    return os.path.dirname(__file__) + '/config_files/'


@pytest.fixture(scope='module')
def connection_config_not_exist(config_files_dir_utils):
    return config_files_dir_utils + '.file_does_not_exists'


@pytest.fixture(scope='module')
def connection_config_empty(config_files_dir_utils):
    return config_files_dir_utils + '.test_empty_key'


@pytest.fixture(scope='module')
def connection_config_without_section(utils, config_files_dir_utils):
    return config_files_dir_utils + '.config_file_with_no_section_error.ini'


@pytest.fixture(scope='module')
def connection_config_without_option(utils, config_files_dir_utils):
    return config_files_dir_utils + '.config_file_with_no_option_error.ini'


@pytest.fixture(scope='module')
def connection_config_with_invalid_token(utils, config_files_dir_utils):
    return config_files_dir_utils + '.config_file_with_invalid_token.ini'


@pytest.fixture(scope='module')
def connection_config_with_pading_token(utils, config_files_dir_utils):
    return config_files_dir_utils + '.test_key_with_pading_error'

@pytest.fixture(scope='module')
def config_file_dict(test_connection_config_path):
    config = ConfigParser.ConfigParser()
    config.read(test_connection_config_path)

    return {
        'host': config.get('repository', 'Host'),
        'port': int(config.get('repository', 'Port')),
        'database': config.get('repository', 'Database'),
        'user': config.get('repository', 'User'),
        'password': config.get('repository', 'Pass')
    }
