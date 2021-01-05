from overhave.entities import StepPrefixesModel

RUSSIAN_PREFIXES = StepPrefixesModel(
    FEATURE="Функция:",
    SCENARIO_OUTLINE="Структура сценария:",
    SCENARIO="Сценарий:",
    BACKGROUND="Предыстория:",
    EXAMPLES="Примеры:",
    EXAMPLES_VERTICAL="Примеры: Вертикально",
    GIVEN="Дано ",
    WHEN="Когда ",
    THEN="То ",
    AND="И ",
    BUT="Но ",
)
