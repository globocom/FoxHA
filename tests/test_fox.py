import pytest
from foxha import fox


def test_version_message(capsys):
    with pytest.raises(SystemExit) as e:
        fox.main(['--version'])
    assert str(e.value) == '0'

    out, err = capsys.readouterr()
    assert '0.9.0' in err


def test_can_get_config(environment, capsys):
    fox.main(['-c', '-g', environment.group])
    out, err = capsys.readouterr()
    assert 'GROUP_NAME: {}'.format(environment.group) in out


def test_can_get_status(environment, capsys):
    fox.main(['--status', '-g', environment.group])

    out, err = capsys.readouterr()
    assert environment.master in out
    assert environment.replication in out


def test_can_list_nodes(environment, capsys):
    with pytest.raises(SystemExit) as e:
        fox.main(['-l', '-g', environment.group])
    assert str(e.value) == '0'

    out, err = capsys.readouterr()
    assert environment.master in out
    assert environment.replication in out


def test_can_list_groups(environment, capsys):
    with pytest.raises(SystemExit) as e:
        fox.main(['-l'])
    assert str(e.value) == '0'

    out, err = capsys.readouterr()
    assert environment.group in out
