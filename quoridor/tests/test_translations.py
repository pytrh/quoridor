import os
import gettext
from unittest.mock import patch

from quoridor.translations import setup_translation


def test_translation_default_to_english():
    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        setup_translation()
        assert gettext.gettext("") == ""


def test_translation_french():
    with patch.dict(os.environ, {"LANG": "fr_FR.UTF-8"}):
        setup_translation()
        assert gettext.gettext(" will play? ") == " va jouer? "


def test_translation_invalid_lang():
    with patch.dict(os.environ, {"LANG": "invalid_locale"}):
        setup_translation()
        assert gettext.gettext("") == ""


def test_translation_file_not_found():
    with patch("gettext.translation", side_effect=FileNotFoundError):
        setup_translation()
        assert isinstance(gettext.NullTranslations(), gettext.NullTranslations)


def test_textdomain():
    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        setup_translation()
        assert gettext.textdomain() == "quoridor"
