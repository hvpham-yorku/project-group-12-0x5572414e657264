from typing import List
from src.database.model_managers import (
    get_allProductCategories,
    get_allProducts,
    get_allProductsAndProductCategories,
    get_allDemographicCategories,
)

# from src.database.model_managers import (
#     get_all_categories,
# )


class GraphWindow:
    """
    This class contains the state of the data analytics window

    """

    def __init__(self):
        self._countValues = [15, 30, 45, 10]
        self._categoriesValues = ["Apples", "Bananas", "Cherries", "Dates"]
        self._chartType = "NONE"
        self._categoriesAvailable = get_allDemographicCategories()
        self._countsAvailable = get_allProductsAndProductCategories()
        self._categorySelected = "NONE"
        self._countsSelected = []

    def _get_allProducts(self) -> List[str]:
        pass

    def _get_allAgeRanges(self) -> List[str]:
        pass

    def _get_allGenders(self) -> List[str]:
        pass

    def get_graphPieData(self) -> List[int, str]:
        return [self._countValues, self._categoriesValues]

    def get_categoriesAvailable(self) -> List[str]:
        return self._categoriesAvailable

    def get_countsAvailable(self) -> List[str]:
        return self._countsAvailable

    def set_chartType(self, chartType: str) -> None:
        self._chartType = chartType

    def set_categorySelected(self, categorySelected: str) -> None:
        self._categorySelected = categorySelected

    def set_countsSelected(self, countsSelected: List[str]) -> None:
        self._countsSelected = countsSelected

    def swap_category_and_counted(self) -> None:
        self._categoriesAvailable, self._countsAvailable = (
            self._countsAvailable,
            self._categoriesAvailable,
        )

    def is_validState(self) -> List[bool, str]:
        """
        index 0 is if the query is in valid state
        index 1 is reason if query is not in valid state
        """
        pass
