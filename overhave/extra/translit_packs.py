from overhave.entities import TranslitPack

RUSSIAN_TRANSLIT_PACK = TranslitPack(
    language_code="ru",
    language_name="russian",
    pre_processor_mapping={
        u"ж": u"zh",
        u"х": u"kh",
        u"ц": u"ts",
        u"ч": u"ch",
        u"ш": u"sh",
        u"щ": u"shch",
        u"ю": u"yu",
        u"я": u"ya",
        u"ъ": u"",
        u"ь": u"",
        u" ": u"_",
        u",": u"",
        u".": u"",
        u"(": u"",
        u")": u"",
        u":": u"",
        u"?": u"",
    },
    mapping=(u"абвгдеёзийклмнопрстуфыэ₽", u"abvgdeeziyklmnoprstufye_"),
)
