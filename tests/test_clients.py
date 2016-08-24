import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import clients

class ThereAreNoClientsTest(unittest.TestCase):
    
    def test(self):
        expected = '10.0.0.2'
        result = clients.next_available_ip()
        self.assertEqual(expected, result)

class ClientsHaveAnOpeningTest(unittest.TestCase):

    def setUp(self):
        netmask = '255.255.255.0'
        clients.new_client('one', '10.0.0.2', netmask)
        clients.new_client('one', '10.0.0.4', netmask)
        
    def test(self):
        expected = '10.0.0.3'
        result = clients.next_available_ip()
        self.assertEqual(expected, result)

    def tearDown(self):
        pass

class ClientsAreContiguousTest(unittest.TestCase):

    def test(self):
        expected = '10.0.0.5'
        result = clients.next_available_ip()
        self.assertEqual(expected, result)

class IpsRollOverOctetsTest(unittest.TestCase):

    def test(self):
        expected = '10.0.1.0'
        result = clients.next_available_ip()
        self.assertEqual(expected, result)

class ThereAreNoIpsAvailableTest(unittest.TestCase):

    def test(self):
        self.assertRaises(clients.IpsSaturatedError, clients.next_available_ip)

class NewClientTest(unittest.TestCase):

    def testDupClient(self):
        expected = ['ifconfig_push 10.0.0.2 255.255.255.0']
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        result = clients.new_client(name, ip, netmask)
        self.assertRaises(clients.DuplicateClientError, clients.new_client, name, ip, netmask)


    def testNewClient(self):
        expected = ['ifconfig_push 10.0.0.2 255.255.255.0']
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        result = clients.new_client(name, ip, netmask)
        self.assertEqual(expected, result)

    def tearDown(self):
        #FIXME remove old client config
        pass


if __name__ == '__main__':
    unittest.main
