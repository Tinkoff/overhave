from copy import copy
from typing import Dict, Optional, Tuple, cast

from transliterate.base import TranslitLanguagePack


class TranslitPack:
    """ Class for feature file name's transliteration before saving. """

    def __init__(
        self,
        language_code: Optional[str],
        language_name: Optional[str],
        pre_processor_mapping: Optional[Dict[str, str]],
        mapping: Tuple[str, str],
    ) -> None:
        pack = copy(TranslitLanguagePack)
        pack.language_code = language_code
        pack.language_name = language_name
        pack.pre_processor_mapping = pre_processor_mapping
        pack.mapping = mapping
        self._transliterator = pack()

    def translate(self, text: str) -> str:
        return cast(str, self._transliterator.translit(text.strip().lower()).strip('_'))
