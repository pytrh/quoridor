import pytest
import re
from unittest import mock
from quoridor.main import main

# Test Positif

def test_version_option(capsys):
    with mock.patch('sys.argv', ['src.main.py', '--version']):
        with mock.patch("importlib.metadata.version", return_value="0.2.0"):
            with pytest.raises(SystemExit) as exitinfo:
                main()

            captured = capsys.readouterr()
            assert captured.out.strip() == "Quoridor : version 0.2.0"
            assert exitinfo.value.code == 0

def test_version_verbose(capsys):
    with mock.patch('sys.argv', ['src.main.py', '--verbose']):
         with pytest.raises(SystemExit):
            main()

            captured = capsys.readouterr()
            assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - INFO - Mode verbose activé : Affichage des informations supplémentaires',
                captured.out.strip())

def test_version_debug(capsys):
    with mock.patch('sys.argv', ['src.main.py', '--debug']):
         with pytest.raises(SystemExit):
            main()

            captured = capsys.readouterr()
            assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - DEBUG - Mode debug activé : Affichage des logs détaillés (dev)',
                captured.out.strip())


def test_init(capsys):
    from src import main
    with mock.patch.object(main, "main", return_value=42):
        with mock.patch.object(main, "__name__", "__main__"):
            with mock.patch.object(main.sys, 'exit') as mock_exit:
                main.init()         
                assert mock_exit.call_args[0][0] == 42

# Test Négatif

def test_invalid_argument(capsys):
    with mock.patch('sys.argv', ['src.main.py', '--invalid']):
        with pytest.raises(SystemExit) as exitinfo:
            main()
        
        captured = capsys.readouterr()
        assert "error:" in captured.err or "unrecognized arguments" in captured.err
        assert exitinfo.value.code == 2
