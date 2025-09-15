import unittest
from example_pkg.core import greet


class TestGreet(unittest.TestCase):
    def test_happy_path(self):
        self.assertEqual(greet('Alice'), 'Hello, Alice!')

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            greet('')


if __name__ == '__main__':
    unittest.main()
