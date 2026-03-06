from src.logic.singleton import *
import unittest


class TestSingleton(unittest.TestCase):

    def setUp(self):
        # Reset the Singleton before each test to ensure isolation
        Singleton._instance = None

    def test_same_instance_identity(self):
        """Verify that two calls return the exact same object in memory."""
        s1 = Singleton()
        s2 = Singleton()

        # 'is' checks for identity (memory address), not just equality
        self.assertIs(s1, s2, "The two variables do not point to the same instance.")

    def test_attribute_persistence(self):
        """Verify that data set on one instance is visible on the 'other'."""
        s1 = Singleton()
        s1.some_data = "Secret Value"

        s2 = Singleton()
        self.assertEqual(s2.some_data, "Secret Value")

    def test_reset_functionality(self):
        """Verify that our manual reset in setUp actually works (Meta-test)."""
        s1 = Singleton()
        s1.version = 1.0

        # Simulate what happens between tests
        Singleton._instance = None

        s2 = Singleton()
        # s2 should NOT have the 'version' attribute now
        self.assertFalse(hasattr(s2, "version"))


if __name__ == "__main__":
    unittest.main()
