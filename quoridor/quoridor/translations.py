import gettext
import os
import locale

def setup_translation():
    # Set the locale directory
    locale_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locales'))

    # Set up translation for the current language
    current_locale = os.getenv('LANG', 'en_US.UTF-8')  # Default to 'en_US.UTF-8' if LANG is not set
    lang_code = current_locale.split('.')[0]  # Get the language code, e.g., 'fr_FR' or 'en_US'

    # locale.setlocale(locale.LC_ALL, '')

    # Load the translation
    print(lang_code)
    translation = gettext.translation('quoridor', localedir=locale_dir, languages=[lang_code], fallback=True)
    gettext.bindtextdomain('quoridor', locale_dir)
    gettext.textdomain('quoridor')

    # Install the translation function (this will make _() work for translations)
    translation.install()

setup_translation()

T_ = gettext.gettext  # or from i18n setup