import json
import os

import bpy


_TRANSLATION_CONTEXTS = (
    "*",
    "Operator",
    "Property",
    "Report",
    "UI",
)


def _load_translation_file(file_path):
    with open(file_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    locales = payload.get("locales")
    locale = payload.get("locale")
    messages = payload.get("messages", {})
    if not isinstance(messages, dict):
        return None, None

    if locales and isinstance(locales, list):
        normalized_locales = [item for item in locales if isinstance(item, str) and item]
    elif isinstance(locale, str) and locale:
        normalized_locales = [locale]
    else:
        return None, None

    return normalized_locales, messages


def _build_dictionary():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dictionary = {}

    for file_name in os.listdir(root_dir):
        if not file_name.lower().endswith(".json"):
            continue

        file_path = os.path.join(root_dir, file_name)
        try:
            locales, messages = _load_translation_file(file_path)
        except Exception as exc:
            print(f"[fbx_importer] Failed to load translation file {file_name}: {exc}")
            continue

        if not locales:
            continue

        for locale in locales:
            locale_dict = dictionary.setdefault(locale, {})
            for source_text, translated_text in messages.items():
                if not source_text or not translated_text:
                    continue
                for context in _TRANSLATION_CONTEXTS:
                    locale_dict[(context, source_text)] = translated_text

    return dictionary


def register(module_name):
    dictionary = _build_dictionary()
    if not dictionary:
        return

    try:
        bpy.app.translations.register(module_name, dictionary)
    except ValueError:
        bpy.app.translations.unregister(module_name)
        bpy.app.translations.register(module_name, dictionary)


def unregister(module_name):
    try:
        bpy.app.translations.unregister(module_name)
    except ValueError:
        pass
