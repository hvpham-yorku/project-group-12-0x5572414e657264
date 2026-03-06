import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from src.logic.customerAttributesEstimator import estimateAttributes



# Run using: 
# python -m test.test_logic.test_customerAttributesEstimator


class TestCustomerAttributesEstimator(unittest.TestCase):

    def setUp(self):
        """
        setUp() runs before every test.

        Here we patch all external dependencies once so that:
        - no real images are loaded
        - no real ML models run
        - no real database is accessed
        """

        # Patch image loading
        self.patcher_imread = patch(
            "src.logic.customerAttributesEstimator.cv2.imread"
        )
        self.mock_imread = self.patcher_imread.start()
        self.addCleanup(self.patcher_imread.stop)


        # Patch face detection
        self.patcher_face = patch(
            "src.logic.customerAttributesEstimator.highlightFace"
        )
        self.mock_highlightFace = self.patcher_face.start()
        self.addCleanup(self.patcher_face.stop)


        # Patch database functions
        self.patcher_get_customer = patch(
            "src.logic.customerAttributesEstimator.get_customer_by_id"
        )
        self.mock_get_customer = self.patcher_get_customer.start()
        self.addCleanup(self.patcher_get_customer.stop)


        self.patcher_update_customer = patch(
            "src.logic.customerAttributesEstimator.update_customer"
        )
        self.mock_update_customer = self.patcher_update_customer.start()
        self.addCleanup(self.patcher_update_customer.stop)


        # Patch models
        # improves consistency for the sake of testing

        self.patcher_genderNet = patch(
            "src.logic.customerAttributesEstimator.genderNet"
        )
        self.mock_genderNet = self.patcher_genderNet.start()
        self.addCleanup(self.patcher_genderNet.stop)


        self.patcher_ageNet = patch(
            "src.logic.customerAttributesEstimator.ageNet"
        )
        self.mock_ageNet = self.patcher_ageNet.start()
        self.addCleanup(self.patcher_ageNet.stop)
        
        


    def test_estimate_attributes_updates_customer(self):

        # Instead of reading a real image from disk, cv2.imread will return a dummy image.

        self.mock_imread.return_value = np.zeros((500, 500, 3), dtype=np.uint8)


        # Simulate the model detecting one face.

        self.mock_highlightFace.return_value = [[100, 100, 200, 200]]


        # Mock Customer 

        fake_customer = MagicMock()
        fake_customer.customer_id = 1
        fake_customer.age = ""
        fake_customer.sex = ""

        self.mock_get_customer.return_value = fake_customer
        self.mock_update_customer.return_value = fake_customer


        # Mock gender prediction: 10% chance male, 90% chance female

        self.mock_genderNet.forward.return_value = np.array([[0.1, 0.9]])


        # Mock age prediction: index 4 -> "(25-32)"

        self.mock_ageNet.forward.return_value = np.array([
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        ])
        age, gender = estimateAttributes("fake_path.jpg", 1)

        # Return values
        self.assertEqual(age, "(25-32)")
        self.assertEqual(gender, "Female")


        # Customer object updates
        self.assertEqual(fake_customer.age, "25-32")
        self.assertEqual(fake_customer.sex, "Female")

        # Database calls
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

        # Mock gender prediction: 90% chance male, 10% chance female
        self.mock_genderNet.forward.return_value = np.array([[0.9, 0.1]])

        # Mock age prediction: index 6 -> "(48-53)"
        self.mock_ageNet.forward.return_value = np.array([
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        ])

        age, gender = estimateAttributes("fake_path.jpg", 2)


        # Return values 

        self.assertEqual(age, "(48-53)")
        self.assertEqual(gender, "Male")


        # Customer object updates

        self.assertEqual(fake_customer.age, "48-53")
        self.assertEqual(fake_customer.sex, "Male")


        # Database calls

        self.mock_get_customer.assert_called_once_with(2)
        self.mock_update_customer.assert_called_once_with(fake_customer)


if __name__ == "__main__":
    unittest.main()