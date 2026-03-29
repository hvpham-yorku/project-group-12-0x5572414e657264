"""
Unit tests for src.logic.basketAnalysis

All model_managers calls are mocked so that the tests exercise only
the computation logic — no database needed.
"""

import unittest
from unittest.mock import patch

from src.database.models import Checkout, Product, Purchase
from src.logic.basketAnalysis import (
    BasketAnalysis,
    BasketSummary,
    ProductPairAssociation,
    ProductSummary,
    _empty_analysis,
    get_basket_analysis,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(product_id, store_id=1, name="", price=0.0, aisle_id=1):
    return Product(
        product_id=product_id, store_id=store_id, aisle_id=aisle_id,
        name=name or f"Product {product_id}", price=price,
    )


def _make_checkout(checkout_id, store_id=1, customer_id=1, total_price=0.0):
    return Checkout(
        checkout_id=checkout_id, store_id=store_id,
        customer_id=customer_id, total_price=total_price,
    )


def _make_purchase(purchase_id, product_id, checkout_id, quantity=1):
    return Purchase(
        purchase_id=purchase_id, product_id=product_id,
        checkout_id=checkout_id, quantity=quantity,
    )


# ---------------------------------------------------------------------------
# _empty_analysis
# ---------------------------------------------------------------------------

class TestEmptyAnalysis(unittest.TestCase):

    def test_zeroed_summary(self):
        result = _empty_analysis()
        self.assertEqual(result.basket_summary.total_transactions, 0)
        self.assertEqual(result.basket_summary.total_revenue, 0.0)
        self.assertEqual(result.basket_summary.average_basket_size, 0.0)
        self.assertEqual(result.basket_summary.average_basket_quantity, 0.0)
        self.assertEqual(result.basket_summary.average_basket_value, 0.0)
        self.assertEqual(result.product_summaries, [])
        self.assertEqual(result.product_pair_associations, [])


# ---------------------------------------------------------------------------
# get_basket_analysis
# ---------------------------------------------------------------------------

_MM = "src.logic.basketAnalysis.model_managers"


class TestNoCheckouts(unittest.TestCase):

    @patch(f"{_MM}.get_checkouts_by_store", return_value=[])
    def test_returns_empty_when_no_checkouts(self, _mock):
        result = get_basket_analysis(store_id=1)
        self.assertEqual(result.basket_summary.total_transactions, 0)
        self.assertEqual(result.product_summaries, [])
        self.assertEqual(result.product_pair_associations, [])


class TestCheckoutWithNoPurchases(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout", return_value=[])
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_empty_basket_still_counted_in_transactions(self, mock_co, mock_prod, _mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=0.0)]
        mock_prod.return_value = [_make_product(10, price=5.0)]

        result = get_basket_analysis(store_id=1)

        self.assertEqual(result.basket_summary.total_transactions, 1)
        self.assertAlmostEqual(result.basket_summary.total_revenue, 0.0)
        self.assertAlmostEqual(result.basket_summary.average_basket_size, 0.0)
        self.assertAlmostEqual(result.basket_summary.average_basket_quantity, 0.0)
        self.assertEqual(result.product_summaries, [])
        self.assertEqual(result.product_pair_associations, [])


class TestSingleCheckoutSingleProduct(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_product_summary_and_basket_stats(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=15.0)]
        mock_prod.return_value = [_make_product(10, name="Milk", price=5.0)]
        mock_purch.return_value = [
            _make_purchase(1, product_id=10, checkout_id=1, quantity=3),
        ]

        result = get_basket_analysis(store_id=1)

        self.assertEqual(len(result.product_summaries), 1)
        ps = result.product_summaries[0]
        self.assertEqual(ps.product_id, 10)
        self.assertEqual(ps.product_name, "Milk")
        self.assertEqual(ps.total_quantity_sold, 3)
        self.assertEqual(ps.transaction_count, 1)
        self.assertAlmostEqual(ps.total_revenue, 15.0)

        self.assertEqual(result.product_pair_associations, [])

        bs = result.basket_summary
        self.assertEqual(bs.total_transactions, 1)
        self.assertAlmostEqual(bs.total_revenue, 15.0)
        self.assertAlmostEqual(bs.average_basket_size, 1.0)
        self.assertAlmostEqual(bs.average_basket_quantity, 3.0)
        self.assertAlmostEqual(bs.average_basket_value, 15.0)


class TestSingleCheckoutMultipleProducts(unittest.TestCase):
    """One transaction with products A and B — pair has
    support=1, confidence=1, lift=1."""

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_pair_metrics_single_transaction(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=8.0)]
        mock_prod.return_value = [
            _make_product(1, name="Bread", price=3.0),
            _make_product(2, name="Butter", price=5.0),
        ]
        mock_purch.return_value = [
            _make_purchase(1, product_id=1, checkout_id=1, quantity=1),
            _make_purchase(2, product_id=2, checkout_id=1, quantity=1),
        ]

        result = get_basket_analysis(store_id=1)

        self.assertEqual(len(result.product_pair_associations), 1)
        pair = result.product_pair_associations[0]
        self.assertEqual(pair.product_a_id, 1)
        self.assertEqual(pair.product_b_id, 2)
        self.assertEqual(pair.co_occurrence_count, 1)
        self.assertAlmostEqual(pair.support, 1.0)
        self.assertAlmostEqual(pair.confidence_a_to_b, 1.0)
        self.assertAlmostEqual(pair.confidence_b_to_a, 1.0)
        self.assertAlmostEqual(pair.lift, 1.0)


class TestMultipleCheckoutsDisjointProducts(unittest.TestCase):
    """Two transactions with no shared products — no pairs generated."""

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_no_pairs_when_disjoint(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [
            _make_checkout(1, total_price=3.0),
            _make_checkout(2, total_price=5.0),
        ]
        mock_prod.return_value = [
            _make_product(1, name="Bread", price=3.0),
            _make_product(2, name="Butter", price=5.0),
        ]

        def purchases_side_effect(checkout_id):
            if checkout_id == 1:
                return [_make_purchase(1, product_id=1, checkout_id=1)]
            return [_make_purchase(2, product_id=2, checkout_id=2)]

        mock_purch.side_effect = purchases_side_effect

        result = get_basket_analysis(store_id=1)

        self.assertEqual(len(result.product_summaries), 2)
        self.assertEqual(result.product_pair_associations, [])

        bs = result.basket_summary
        self.assertEqual(bs.total_transactions, 2)
        self.assertAlmostEqual(bs.total_revenue, 8.0)
        self.assertAlmostEqual(bs.average_basket_size, 1.0)
        self.assertAlmostEqual(bs.average_basket_quantity, 1.0)
        self.assertAlmostEqual(bs.average_basket_value, 4.0)


class TestAssociationMetricsHandComputed(unittest.TestCase):
    """Four transactions with known product overlap — verify support,
    confidence, and lift against hand-computed values.

    Txn 1: {A, B, C}    Txn 2: {A, B}
    Txn 3: {A, C}       Txn 4: {B, D}

    txn_count: A=3, B=3, C=2, D=1
    support:   A=3/4, B=3/4, C=2/4, D=1/4
    """

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_all_pair_metrics(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [
            _make_checkout(1, total_price=10.0),
            _make_checkout(2, total_price=5.0),
            _make_checkout(3, total_price=7.0),
            _make_checkout(4, total_price=7.0),
        ]
        mock_prod.return_value = [
            _make_product(1, name="A", price=2.0),
            _make_product(2, name="B", price=3.0),
            _make_product(3, name="C", price=5.0),
            _make_product(4, name="D", price=4.0),
        ]

        def purchases_side_effect(checkout_id):
            mapping = {
                1: [
                    _make_purchase(1, 1, 1), _make_purchase(2, 2, 1),
                    _make_purchase(3, 3, 1),
                ],
                2: [_make_purchase(4, 1, 2), _make_purchase(5, 2, 2)],
                3: [_make_purchase(6, 1, 3), _make_purchase(7, 3, 3)],
                4: [_make_purchase(8, 2, 4), _make_purchase(9, 4, 4)],
            }
            return mapping.get(checkout_id, [])

        mock_purch.side_effect = purchases_side_effect

        result = get_basket_analysis(store_id=1)
        pairs = {
            (p.product_a_id, p.product_b_id): p
            for p in result.product_pair_associations
        }

        self.assertEqual(len(pairs), 4)

        # (A,B): co=2, support=2/4, conf_A->B=2/3, conf_B->A=2/3
        ab = pairs[(1, 2)]
        self.assertEqual(ab.co_occurrence_count, 2)
        self.assertAlmostEqual(ab.support, 0.5)
        self.assertAlmostEqual(ab.confidence_a_to_b, 2 / 3)
        self.assertAlmostEqual(ab.confidence_b_to_a, 2 / 3)
        self.assertAlmostEqual(ab.lift, 0.5 / (0.75 * 0.75))

        # (A,C): co=2, support=2/4, conf_A->C=2/3, conf_C->A=1.0
        ac = pairs[(1, 3)]
        self.assertEqual(ac.co_occurrence_count, 2)
        self.assertAlmostEqual(ac.support, 0.5)
        self.assertAlmostEqual(ac.confidence_a_to_b, 2 / 3)
        self.assertAlmostEqual(ac.confidence_b_to_a, 1.0)
        self.assertAlmostEqual(ac.lift, 0.5 / (0.75 * 0.5))

        # (B,C): co=1, support=1/4, conf_B->C=1/3, conf_C->B=1/2
        bc = pairs[(2, 3)]
        self.assertEqual(bc.co_occurrence_count, 1)
        self.assertAlmostEqual(bc.support, 0.25)
        self.assertAlmostEqual(bc.confidence_a_to_b, 1 / 3)
        self.assertAlmostEqual(bc.confidence_b_to_a, 0.5)
        self.assertAlmostEqual(bc.lift, 0.25 / (0.75 * 0.5))

        # (B,D): co=1, support=1/4, conf_B->D=1/3, conf_D->B=1.0
        bd = pairs[(2, 4)]
        self.assertEqual(bd.co_occurrence_count, 1)
        self.assertAlmostEqual(bd.support, 0.25)
        self.assertAlmostEqual(bd.confidence_a_to_b, 1 / 3)
        self.assertAlmostEqual(bd.confidence_b_to_a, 1.0)
        self.assertAlmostEqual(bd.lift, 0.25 / (0.75 * 0.25))


class TestProductSummariesSortedByQuantity(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_descending_quantity_order(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=20.0)]
        mock_prod.return_value = [
            _make_product(1, name="Few", price=10.0),
            _make_product(2, name="Many", price=2.0),
        ]
        mock_purch.return_value = [
            _make_purchase(1, product_id=1, checkout_id=1, quantity=1),
            _make_purchase(2, product_id=2, checkout_id=1, quantity=5),
        ]

        result = get_basket_analysis(store_id=1)

        self.assertEqual(result.product_summaries[0].product_name, "Many")
        self.assertEqual(result.product_summaries[0].total_quantity_sold, 5)
        self.assertEqual(result.product_summaries[1].product_name, "Few")
        self.assertEqual(result.product_summaries[1].total_quantity_sold, 1)


class TestPairsSortedByLiftDescending(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_lift_ordering(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [
            _make_checkout(1, total_price=10.0),
            _make_checkout(2, total_price=5.0),
            _make_checkout(3, total_price=7.0),
            _make_checkout(4, total_price=7.0),
        ]
        mock_prod.return_value = [
            _make_product(1, name="A", price=2.0),
            _make_product(2, name="B", price=3.0),
            _make_product(3, name="C", price=5.0),
            _make_product(4, name="D", price=4.0),
        ]

        def purchases_side_effect(checkout_id):
            return {
                1: [
                    _make_purchase(1, 1, 1), _make_purchase(2, 2, 1),
                    _make_purchase(3, 3, 1),
                ],
                2: [_make_purchase(4, 1, 2), _make_purchase(5, 2, 2)],
                3: [_make_purchase(6, 1, 3), _make_purchase(7, 3, 3)],
                4: [_make_purchase(8, 2, 4), _make_purchase(9, 4, 4)],
            }.get(checkout_id, [])

        mock_purch.side_effect = purchases_side_effect

        result = get_basket_analysis(store_id=1)
        lifts = [p.lift for p in result.product_pair_associations]

        self.assertEqual(lifts, sorted(lifts, reverse=True))


class TestProductNotInCatalog(unittest.TestCase):
    """Purchase references a product_id not returned by get_products_by_store."""

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store", return_value=[])
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_fallback_name_and_zero_revenue(self, mock_co, _mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=0.0)]
        mock_purch.return_value = [
            _make_purchase(1, product_id=99, checkout_id=1, quantity=2),
        ]

        result = get_basket_analysis(store_id=1)

        self.assertEqual(len(result.product_summaries), 1)
        ps = result.product_summaries[0]
        self.assertEqual(ps.product_name, "product_99")
        self.assertAlmostEqual(ps.total_revenue, 0.0)
        self.assertEqual(ps.total_quantity_sold, 2)


class TestMultipleCheckoutsBasketAverages(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_averages_across_baskets(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [
            _make_checkout(1, total_price=10.0),
            _make_checkout(2, total_price=20.0),
        ]
        mock_prod.return_value = [
            _make_product(1, name="A", price=5.0),
            _make_product(2, name="B", price=10.0),
            _make_product(3, name="C", price=5.0),
        ]

        def purchases_side_effect(checkout_id):
            if checkout_id == 1:
                return [_make_purchase(1, product_id=1, checkout_id=1, quantity=2)]
            return [
                _make_purchase(2, product_id=2, checkout_id=2, quantity=1),
                _make_purchase(3, product_id=3, checkout_id=2, quantity=1),
            ]

        mock_purch.side_effect = purchases_side_effect

        result = get_basket_analysis(store_id=1)
        bs = result.basket_summary

        self.assertEqual(bs.total_transactions, 2)
        self.assertAlmostEqual(bs.total_revenue, 30.0)
        self.assertAlmostEqual(bs.average_basket_size, 1.5)      # (1+2)/2
        self.assertAlmostEqual(bs.average_basket_quantity, 2.0)   # (2+2)/2
        self.assertAlmostEqual(bs.average_basket_value, 15.0)     # 30/2


class TestRevenueAccumulatesAcrossCheckouts(unittest.TestCase):
    """Same product bought in multiple transactions."""

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_revenue_and_quantity_summed(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [
            _make_checkout(1, total_price=10.0),
            _make_checkout(2, total_price=15.0),
        ]
        mock_prod.return_value = [_make_product(1, name="Milk", price=5.0)]

        def purchases_side_effect(checkout_id):
            if checkout_id == 1:
                return [_make_purchase(1, product_id=1, checkout_id=1, quantity=2)]
            return [_make_purchase(2, product_id=1, checkout_id=2, quantity=3)]

        mock_purch.side_effect = purchases_side_effect

        result = get_basket_analysis(store_id=1)

        self.assertEqual(len(result.product_summaries), 1)
        ps = result.product_summaries[0]
        self.assertEqual(ps.total_quantity_sold, 5)
        self.assertEqual(ps.transaction_count, 2)
        self.assertAlmostEqual(ps.total_revenue, 25.0)


class TestThreeProductsInOneBasket(unittest.TestCase):
    """Three products in one basket should generate three pairs."""

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_three_pairs_generated(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=12.0)]
        mock_prod.return_value = [
            _make_product(1, name="A", price=2.0),
            _make_product(2, name="B", price=4.0),
            _make_product(3, name="C", price=6.0),
        ]
        mock_purch.return_value = [
            _make_purchase(1, product_id=1, checkout_id=1),
            _make_purchase(2, product_id=2, checkout_id=1),
            _make_purchase(3, product_id=3, checkout_id=1),
        ]

        result = get_basket_analysis(store_id=1)
        pair_keys = {
            (p.product_a_id, p.product_b_id)
            for p in result.product_pair_associations
        }

        self.assertEqual(pair_keys, {(1, 2), (1, 3), (2, 3)})
        for pair in result.product_pair_associations:
            self.assertAlmostEqual(pair.support, 1.0)
            self.assertAlmostEqual(pair.confidence_a_to_b, 1.0)
            self.assertAlmostEqual(pair.confidence_b_to_a, 1.0)
            self.assertAlmostEqual(pair.lift, 1.0)


class TestPairNamesResolvedFromCatalog(unittest.TestCase):

    @patch(f"{_MM}.get_purchases_by_checkout")
    @patch(f"{_MM}.get_products_by_store")
    @patch(f"{_MM}.get_checkouts_by_store")
    def test_pair_names(self, mock_co, mock_prod, mock_purch):
        mock_co.return_value = [_make_checkout(1, total_price=8.0)]
        mock_prod.return_value = [
            _make_product(1, name="Bread", price=3.0),
            _make_product(2, name="Butter", price=5.0),
        ]
        mock_purch.return_value = [
            _make_purchase(1, product_id=1, checkout_id=1),
            _make_purchase(2, product_id=2, checkout_id=1),
        ]

        result = get_basket_analysis(store_id=1)

        pair = result.product_pair_associations[0]
        self.assertEqual(pair.product_a_name, "Bread")
        self.assertEqual(pair.product_b_name, "Butter")


if __name__ == "__main__":
    unittest.main()
