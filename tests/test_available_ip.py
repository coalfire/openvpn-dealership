import unittest

class ThereAreNoClientsTest(unittest.TestCase):

    def test(self):
        expected = '10.0.0.2'
        actual = clients.next_available_ip()
        self.assertEqual(expected, actual)

class ClientsHaveAnOpeningTest(unittest.TestCase):

    def test(self):
        expected = '10.0.0.3'
        actual = clients.next_available_ip()
        self.assertEqual(expected, actual)

class ClientsAreContiguousTest(unittest.TestCase):

    def test(self):
        expected = '10.0.0.5'
        actual = clients.next_available_ip()
        self.assertEqual(expected, actual)

class IpsRollOverOctetsTest(unittest.TestCase):

    def test(self):
        expected = '10.0.1.0'
        actual = clients.next_available_ip()
        self.assertEqual(expected, actual)

class ThereAreNoIpsAvailableTest(unittest.TestCase):

    def test(self):
        self.assertRaises(clients.IpsSaturatedError, clients.next_available_ip)


if __name__ == '__main__':
    unittest.main
