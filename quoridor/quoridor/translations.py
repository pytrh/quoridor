import gettext
import os
import locale

def setup_translation():
    locale_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locales'))

    lang_code = os.getenv('LANG', 'en')[:2]  # Default to 'en' if LANG is not set or invalid

    if lang_code != 'fr':
        lang_code = 'en'

    try:
        translation = gettext.translation('quoridor', localedir=locale_dir, languages=[lang_code], fallback=True)
    except FileNotFoundError:
        translation = gettext.NullTranslations()

    gettext.bindtextdomain('quoridor', locale_dir)
    gettext.textdomain('quoridor')
    translation.install()

setup_translation()

T_ = gettext.gettext