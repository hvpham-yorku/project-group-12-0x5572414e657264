import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

import numpy as np


class TestCustomerAttributesEstimator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "src.logic.customerAttributesEstimator" in sys.modules:
            del sys.modules["src.logic.customerAttributesEstimator"]
        with patch("cv2.dnn.readNet", return_value=MagicMock()):
            cls.cae = importlib.import_module("src.logic.customerAttributesEstimator")

    def setUp(self):
        self.patcher_imread = patch.object(self.cae.cv2, "imread")
        self.mock_imread = self.patcher_imread.start()
        self.addCleanup(self.patcher_imread.stop)

        self.patcher_face = patch.object(self.cae, "highlightFace")
        self.mock_highlightFace = self.patcher_face.start()
        self.addCleanup(self.patcher_face.stop)

        self.patcher_get_customer = patch.object(self.cae, "get_customer_by_id")
        self.mock_get_customer = self.patcher_get_customer.start()
        self.addCleanup(self.patcher_get_customer.stop)

        self.patcher_update_customer = patch.object(self.cae, "update_customer")
        self.mock_update_customer = self.patcher_update_customer.start()
        self.addCleanup(self.patcher_update_customer.stop)

        self.cae.genderNet = MagicMock()
        self.cae.ageNet = MagicMock()

    def test_estimate_attributes_updates_customer(self):
        self.mock_imread.return_value = np.zeros((500, 500, 3), dtype=np.uint8)
        self.mock_highlightFace.return_value = [[100, 100, 200, 200]]

        fake_customer = MagicMock()
        fake_customer.customer_id = 1
        fake_customer.age = ""
        fake_customer.sex = ""

        self.mock_get_customer.return_value = fake_customer
        self.mock_update_customer.return_value = fake_customer

        self.cae.genderNet.forward.return_value = np.array([[0.1, 0.9]])
        self.cae.ageNet.forward.return_value = np.array(
            [[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]]
        )

        age, gender = self.cae.estimateAttributes("fake_path.jpg", 1)

        self.assertEqual(age, "(25-32)")
        self.assertEqual(gender, "Female")
        self.assertEqual(fake_customer.age, "25-32")
        self.assertEqual(fake_customer.sex, "Female")
        self.mock_get_customer.assert_called_once_with(1)
        self.mock_update_customer.assert_called_once_with(fake_customer)

    def test_estimate_attributes_updates_customer_male_48_53(self):
        self.mock_imread.return_value = np.zeros((500, 500, 3), dtype=np.uint8)
        self.mock_highlightFace.return_value = [[120, 120, 220, 220]]

        fake_customer = MagicMock()
        fake_customer.customer_id = 2
        fake_customer.age = ""
        fake_customer.sex = ""

        self.mock_get_customer.return_value = fake_customer
        self.mock_update_customer.return_value = fake_customer

        self.cae.genderNet.forward.return_value = np.array([[0.9, 0.1]])
        self.cae.ageNet.forward.return_value = np.array(
            [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]]
        )

        age, gender = self.cae.estimateAttributes("fake_path.jpg", 2)

        self.assertEqual(age, "(48-53)")
        self.assertEqual(gender, "Male")
        self.assertEqual(fake_customer.age, "48-53")
        self.assertEqual(fake_customer.sex, "Male")
        self.mock_get_customer.assert_called_once_with(2)
        self.mock_update_customer.assert_called_once_with(fake_customer)


if __name__ == "__main__":
    unittest.main()
