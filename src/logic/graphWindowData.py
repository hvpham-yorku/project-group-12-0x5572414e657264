from typing import List


class GraphWindow:
    """
    This class contains the state of the data analytics window

    """

    def __init__(self):
        self._countValues = [15, 30, 45, 10]
        self._categoriesValues = ["Apples", "Bananas", "Cherries", "Dates"]
        self._chartType = "NONE"
        self._categorySelected = "NONE"
        self._countsSelected = []

    def get_graphPieData(self) -> List[int, str]:
        return [self._countValues, self._categoriesValues]

    def set_chartType(self, chartType: str) -> None:
        self._chartType = chartType

    def set_categorySelected(self, categorySelected: str) -> None:
        self._categorySelected = categorySelected

    def set_countsSelected(self, countsSelected: List[str]) -> None:
        self._countsSelected = countsSelected
