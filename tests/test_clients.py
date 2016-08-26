import unittest
import os
import sys
from shutil import rmtree
sys.path.insert(0, os.path.abspath('..'))

import clients

#class ThereAreNoClientsTest(unittest.TestCase):
#    
#    def test(self):
#        expected = '10.0.0.2'
#        result = clients.next_available_ip()
#        self.assertEqual(expected, result)
#
#class ClientsHaveAnOpeningTest(unittest.TestCase):
#
#    def setUp(self):
#        netmask = '255.255.255.0'
#        clients.new_client('one', '10.0.0.2', netmask)
#        clients.new_client('one', '10.0.0.4', netmask)
#        
#    def test(self):
#        expected = '10.0.0.3'
#        result = clients.next_available_ip()
#        self.assertEqual(expected, result)
#
#    def tearDown(self):
#        pass
#
#class ClientsAreContiguousTest(unittest.TestCase):
#
#    def test(self):
#        expected = '10.0.0.5'
#        result = clients.next_available_ip()
#        self.assertEqual(expected, result)
#
#class IpsRollOverOctetsTest(unittest.TestCase):
#
#    def test(self):
#        expected = '10.0.1.0'
#        result = clients.next_available_ip()
#        self.assertEqual(expected, result)
#
#class ThereAreNoIpsAvailableTest(unittest.TestCase):
#
#    def test(self):
#        self.assertRaises(clients.IpsSaturatedError, clients.next_available_ip)

class NewClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './test_clients'
        os.makedirs(self.ccd)

    def testNewClient(self):
        expected = {'name': 'dummy', 'ifconfig': 'ifconfig_push 10.0.0.2 255.255.255.0'}
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        result = clients.new_client(name, ip, netmask, ccd=self.ccd)
        self.assertEqual(expected, result)

#    def testDupClient(self):
#        ip = '10.0.0.2'
#        netmask = '255.255.255.0'
#        name = 'dummy'
#        result = clients.new_client(name, ip, netmask, self.ccd)
#        self.assertRaises(clients.DuplicateClientError, clients.new_client, name, ip, netmask, self.ccd)


    def tearDown(self):
        rmtree(self.ccd)


if __name__ == '__main__':
    unittest.main
