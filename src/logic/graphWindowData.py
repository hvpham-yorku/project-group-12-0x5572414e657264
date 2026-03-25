from typing import List
from src.database.model_managers import (
    get_allProductCategories,
    get_allProducts,
    get_allProductsAndProductCategories,
    get_allDemographicCategories,
    get_allPossibleDateTimes,
    get_AllProductAndTimeDataToGraph,
)
from datetime import datetime

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
        self._categoriesAvailable = []
        self._countsAvailable = []
        self._possibleDateTimes = []
        self._countTypeSelected = "product"
        self._countsSelected = []
        self._checkBoxCounts = {}
        self._checkBoxCategories = {}
        self._selectedTimeFrame = []
        self.refresh_available_options()

    def refresh_available_options(self) -> None:
        self._categoriesAvailable = get_allDemographicCategories()
        self._countsAvailable = get_allProductsAndProductCategories()
        self._possibleDateTimes = get_allPossibleDateTimes()

    def getValuesToGraph(self) -> None:
        if len(self._selectedTimeFrame) < 2:
            return [[], []]

        # need to filter by time frame
        ages = []
        genders = []
        products = []
        productCategories = []
        for category, is_selected in self._checkBoxCategories.items():
            if is_selected:
                cleaned_category = category.rstrip()
                if not cleaned_category:
                    continue
                if cleaned_category[0] == "M" or cleaned_category[0] == "F":
                    genders.append(cleaned_category[0])
                else:
                    ages.append(cleaned_category)
        for product, is_selected in self._checkBoxCounts.items():
            if is_selected:
                # check if it is a product or an aisle
                cleaned_product = product.rstrip()
                if not cleaned_product:
                    continue
                if "#" in cleaned_product:
                    # then this is a product
                    products.append(cleaned_product[: cleaned_product.index("#")])
                elif ":" in cleaned_product:
                    productCategories.append(
                        cleaned_product[cleaned_product.index(":") + 2 :]
                    )
        return get_AllProductAndTimeDataToGraph(
            self._selectedTimeFrame[0],
            self._selectedTimeFrame[1],
            ages,
            genders,
            products,
            productCategories,
            self._countTypeSelected,
        )

    def resetSelectedTimeFrame(self) -> None:
        self._selectedTimeFrame = []

    def setSelectedTimeFrame(self, time1: datetime, time2: datetime) -> None:
        self._selectedTimeFrame = [time1, time2]

    def set_checkBoxCounts(self, box: str, newValue: bool) -> None:
        self._checkBoxCounts[box] = newValue

    def set_checkBoxCategories(self, box: str, newValue: bool) -> None:
        self._checkBoxCategories[box] = newValue

    def get_checkBoxCountsTrue(self) -> None:
        ret = []
        for key in self._checkBoxCounts.keys():
            if self._checkBoxCounts[key]:
                ret.append(key)
        return ret

    def get_checkBoxCategoriesTrue(self) -> None:
        ret = []
        counter = 0
        maxPerLine = 3
        if self._countTypeSelected == "product":
            for key in self._checkBoxCategories.keys():
                if self._checkBoxCategories[key]:
                    if counter > maxPerLine:
                        ret.append("\n")
                        counter = 0
                    ret.append(key.rstrip())
                    counter += 1
        else:
            for key in self._checkBoxCounts.keys():
                if self._checkBoxCounts[key]:
                    if counter > maxPerLine:
                        ret.append("\n")
                        counter = 0
                    ret.append(key.rstrip())
                    counter += 1
        return ret

    def clearBoxesValues(self) -> None:
        self._checkBoxCounts = {}
        self._checkBoxCategories = {}

    def _get_possibleDateTimes(self) -> List[datetime]:
        self.refresh_available_options()
        return self._possibleDateTimes

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

    def get_dataTypeIsCountAndCategory(self) -> None:
        return self._countTypeSelected

    def _set_dataTypeIsCountAndCategory(self) -> None:
        if self._countTypeSelected == "product":
            self._countTypeSelected = "demographic"
        else:
            self._countTypeSelected = "product"

    def set_countsSelected(self, countsSelected: List[str]) -> None:
        self._countsSelected = countsSelected

    def swap_category_and_counted(self) -> None:
        self._set_dataTypeIsCountAndCategory()

    def is_validState(self) -> List[bool, str]:
        """
        index 0 is if the query is in valid state
        index 1 is reason if query is not in valid state
        """
        if len(self._selectedTimeFrame) == 2:
            return [True, "All good mate! :)"]
        else:
            return [False, "SELECT PROPER TIME FRAME >:("]

    def test_func(self):
        return get_AllProductAndTimeDataToGraph()
