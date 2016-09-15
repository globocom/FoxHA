import ConfigParser
import pytest


def test_config_file_successfully(
    cipher_suite, utils, test_connection_config_path, config_file_dict
):
    config_file = utils.parse_config_file(
        cipher_suite, test_connection_config_path
    )

    assert config_file[0] == config_file_dict['host']
    assert config_file[1] == config_file_dict['port']
    assert config_file[2] == config_file_dict['database']
    assert config_file[3] == config_file_dict['user']
    assert config_file[4] == cipher_suite.decrypt(config_file_dict['password'])


def test_config_file_throws_no_section_error(
    cipher_suite, utils, capsys, connection_config_without_section
):
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_config_file(
            cipher_suite, connection_config_without_section
        )

    error_message = u"\x1b[38;5;160mConfig file error: No section:"\
        " 'repository'\x1b[0m\n"

    out, err = capsys.readouterr()
    assert error_message == out
    assert str(exec_info.value) == '99'


def test_config_file_throws_no_option_error(
    cipher_suite, utils, capsys, connection_config_without_option
):
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_config_file(
            cipher_suite, connection_config_without_option
        )

    error_message = u"\x1b[38;5;160mConfig file error: No option"\
        " 'database' in section: 'repository'\x1b[0m\n"

    out, err = capsys.readouterr()
    assert error_message == out
    assert str(exec_info.value) == '99'


def test_config_file_throws_invalid_token(
    cipher_suite, utils, capsys, connection_config_with_invalid_token
):
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_config_file(
            cipher_suite, connection_config_with_invalid_token
        )

    error_message = u"\x1b[38;5;160mERROR: InvalidToken\x1b[0m\n"

    out, err = capsys.readouterr()
    assert error_message == out
    assert str(exec_info.value) == '99'


def test_config_file_throws_exception(
    cipher_suite, utils, capsys, test_connection_config_path
):
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_config_file(
            'empty string', test_connection_config_path
        )

    error_message = u"\x1b[38;5;160mERROR: 'str' object has no attribute"\
        " 'decrypt'\x1b[0m\n"

    out, err = capsys.readouterr()
    assert error_message == out
    assert str(exec_info.value) == '3'


def test_get_config_values_from_config_file_successfully(
    cipher_suite, utils, test_connection_config_path, config_file_dict
):
    config_values = utils.get_config_values_from_config_file(
        test_connection_config_path
    )

    assert config_values[0] == config_file_dict['host']
    assert config_values[1] == config_file_dict['port']
    assert config_values[2] == config_file_dict['database']
    assert config_values[3] == config_file_dict['user']
    assert config_values[4] == config_file_dict['password']


def test_get_config_values_from_config_file_throws_no_section_error(
    utils, connection_config_without_section
):
    with pytest.raises(ConfigParser.NoSectionError) as exec_info:
        utils.get_config_values_from_config_file(
            connection_config_without_section
        )

    assert str(exec_info.value) == "No section: 'repository'"


def test_get_config_values_from_config_file_throws_no_option_error(
    utils, connection_config_without_option
):
    with pytest.raises(ConfigParser.NoOptionError) as exec_info:
        utils.get_config_values_from_config_file(
            connection_config_without_option
        )

    assert str(exec_info.value) == "No option 'database' in section: 'repository'"
