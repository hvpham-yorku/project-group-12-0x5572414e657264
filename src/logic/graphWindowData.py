from typing import List


class GraphWindow:
    """
    This class contains the state of the data analytics window

    """

    def __init__(self):
        self._countValues = [15, 30, 45, 10]
        self._categoriesValues = ["Apples", "Bananas", "Cherries", "Dates"]
        self._chartType = ""

    def get_graphPieData(self) -> List[int, str]:
        return [self._countValues, self._categoriesValues]
