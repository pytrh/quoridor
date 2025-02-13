import pytest
from src.main import main

# Test Positif

def test_version_option(capsys, monkeypatch):
    monkeypatch.setattr('sys.argv', ['src.main.py', '--version'])
    monkeypatch.setattr("importlib.metadata.version", lambda _: "0.1.0")  # Simule la version

    with pytest.raises(SystemExit) as exitinfo:
        main()

    captured = capsys.readouterr()
    assert captured.out.strip() == "Quoridor : version 0.1.0"
    assert exitinfo.value.code == 0


def test_no_argument_exit_success():
    with pytest.raises(SystemExit) as exitinfo:
        main()
    assert exitinfo.value.code == 0

# Test Negatif

def test_invalid_argument(capsys, monkeypatch):
    monkeypatch.setattr('sys.argv', ['src.main.py', '--invalid'])
    with pytest.raises(SystemExit) as exitinfo:
        main()
    
    captured = capsys.readouterr()
    assert "error:" in captured.err or "unrecognized arguments" in captured.err
    assert exitinfo.value.code != 0