from overhave.extra import RUSSIAN_TRANSLIT_PACK


class TestTranslitPack:
    """ Unit tests for :class:`TranslitPack`. """

    def test_translit_pack_ru(self):
        assert (
            RUSSIAN_TRANSLIT_PACK.translate("абвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789_ ,.():?")
            == "abvgdeezhziyklmnoprstufkhtschshshchyeyuya0123456789"
        )
