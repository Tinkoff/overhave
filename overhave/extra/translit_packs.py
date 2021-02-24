from overhave.entities import TranslitPack

RUSSIAN_TRANSLIT_PACK = TranslitPack(
    language_code="ru",
    language_name="russian",
    pre_processor_mapping={
        "ж": "zh",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ю": "yu",
        "я": "ya",
        "ъ": "",
        "ь": "",
        " ": "_",
        ",": "",
        ".": "",
        "(": "",
        ")": "",
        ":": "",
        "?": "",
    },
    mapping=("абвгдеёзийклмнопрстуфыэ₽", "abvgdeeziyklmnoprstufye_"),
)
