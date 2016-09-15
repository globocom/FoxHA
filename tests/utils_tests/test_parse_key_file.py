import pytest
from cryptography.fernet import Fernet


def test_parse_key_file_successculy(utils, cipher_suite, test_key_path):
    assert isinstance(cipher_suite, Fernet)

    fernet_encrypt = Fernet(open(test_key_path, 'r').readline())
    assert cipher_suite._signing_key == fernet_encrypt._signing_key
    assert cipher_suite._encryption_key == fernet_encrypt._encryption_key


def test_parse_key_throws_IO_error(utils, capsys, connection_config_not_exist):
    file_path = connection_config_not_exist
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_key_file(file_path)

    error_message = u'\x1b[38;5;160mERROR: "{}" file does not exist or you'\
        ' don`t have permission to read it.\x1b[0m'.format(file_path)
    out, err = capsys.readouterr()

    assert error_message == out.rstrip()
    assert str(exec_info.value) == '3'


def test_parse_empty_key_throws_exception(utils, capsys,
    connection_config_empty
):
    file_path = connection_config_empty
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_key_file(keyfile=file_path)

    error_message = u'\x1b[38;5;160mERROR: {} may be empty because'\
        ' Fernet key must be 32 url-safe base64-encoded'\
        ' bytes.\x1b[0m\n'.format(file_path)

    out, err = capsys.readouterr()

    assert error_message == out
    assert str(exec_info.value) == '3'


def test_parse_empty_key_throws_type_error_exception(
    utils, capsys, connection_config_with_pading_token
):
    file_path = connection_config_with_pading_token
    with pytest.raises(SystemExit) as exec_info:
        utils.parse_key_file(keyfile=file_path)

    key = utils.get_key_value_from_key_file(file_path)
    error_message = u'\x1b[38;5;160mERROR: {} is not a valid key'\
        ' because Incorrect padding\x1b[0m\n'.format(key)

    out, err = capsys.readouterr()

    assert error_message == out
    assert str(exec_info.value) == '3'


def test_key_value_from_key_file_succeds(utils, test_key_path):
    key = utils.get_key_value_from_key_file(test_key_path)
    assert key == 'H-fx88gflMH13dsnbF9oH8EG261j9lxeWAFirHVMTi4='


def test_key_value_from_key_file_throws_exception(utils,
    connection_config_not_exist
):
    with pytest.raises(IOError):
        utils.get_key_value_from_key_file(connection_config_not_exist)
