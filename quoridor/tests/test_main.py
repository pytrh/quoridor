import importlib
import pytest
import re
from unittest import mock
from quoridor.main import main, setup_logging


def test_version_option(capsys):
    version = importlib.metadata.version("quoridor")
    with mock.patch("sys.argv", ["quoridor.main.py", "--version"]):
        with mock.patch("importlib.metadata.version", return_value=version):
            with pytest.raises(SystemExit) as exitinfo:
                main()

            captured = capsys.readouterr()
            assert captured.out.strip() == f"Quoridor : version {version}"
            assert exitinfo.value.code == 0


def test_version_verbose(capsys):
    setup_logging(True, False)
    with mock.patch("sys.argv", ["quoridor.main.py", "--verbose"]):
        with pytest.raises(SystemExit):
            main()

            captured = capsys.readouterr()
            assert re.match(
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - INFO - Verbose mode activated: Additional information",
                captured.out.strip(),
            )


def test_version_debug(capsys):
    setup_logging(False, True)
    with mock.patch("sys.argv", ["quoridor.main.py", "--debug"]):
        with pytest.raises(SystemExit):
            main()

            captured = capsys.readouterr()
            assert re.match(
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - DEBUG - Debug mode activated: Detailed logs \(dev\)",
                captured.out.strip(),
            )


def test_init():
    from quoridor import main

    with mock.patch.object(main, "main", return_value=42):
        with mock.patch.object(main, "__name__", "__main__"):
            with mock.patch.object(main.sys, "exit") as mock_exit:
                main.init()
                assert mock_exit.call_args[0][0] == 42


# Test Négatif


def test_invalid_argument(capsys):
    with mock.patch("sys.argv", ["quoridor.main.py", "--invalid"]):
        with pytest.raises(SystemExit) as exitinfo:
            main()

        captured = capsys.readouterr()
        assert "error:" in captured.err or "unrecognized arguments" in captured.err
        assert exitinfo.value.code == 2
