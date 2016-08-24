import unittest

class ThereAreNoClientsTest(unittest.TestCase):

    def test(self):
        self.assertEqual(0,1)

class ClientsHaveAnOpeningTest(unittest.TestCase):

    def test(self):
        self.assertEqual(0,1)

class ThereAreNoIpsAvailableTest(unittest.TestCase):

    def test(self):
        self.assertEqual(0,1)


if __name__ == '__main__':
    unittest.main
