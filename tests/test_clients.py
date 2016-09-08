import unittest
import os
import sys
from shutil import rmtree
sys.path.insert(0, os.path.abspath('..'))

import clients

class ParseConfTest(unittest.TestCase):

    def setUp(self):
        self.conf = './tests/files/server.conf'

    def testNetmask(self):
        result = clients.parse_server(self.conf)['netmask']
        expected = '255.255.255.0'
        self.assertEqual(expected, result)

    def testIP(self):
        result = clients.parse_server(self.conf)['ip']
        expected = '10.0.0.0'
        self.assertEqual(expected, result)

    def testCCD(self):
        result = clients.parse_server(self.conf)['ccd']
        expected = '/etc/openvpn/clients'
        self.assertEqual(expected, result)

    def testAddresses(self):
        result = clients.parse_server(self.conf)['addresses']
        # 256 in a /24 minus the broadcast, network, and server addresses
        expected = 253 
        self.assertEqual(expected, len(result))

class UsedIPsTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/files/ccd'
        os.makedirs(self.ccd)
        netmask = '255.255.255.0'
        for i in range(2, 12):
            s = str(i)
            name = 'client' + s
            ip = '192.168.1.' + s
            clients.new_client(name, ip, netmask, self.ccd)

    def testUsedIPs(self):
        result = clients.used_ips(self.ccd)
        expected = 10
        self.assertEqual(expected, len(result))

    def tearDown(self):
        rmtree(self.ccd)

class ThereAreNoClientsTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/files/ccd_empty'
        os.makedirs(self.ccd)
        self.conf = './tests/files/server.conf'

    def testThereAreNoClients(self):
        expected = '10.0.0.2'
        result = clients.next_available_ip(conf=self.conf, ccd=self.ccd)
        self.assertEqual(expected, result)

    def tearDown(self):
        rmtree(self.ccd)

class ClientsHaveAnOpeningTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/files/ccd'
        os.makedirs(self.ccd)
        self.conf = './tests/files/server.conf'
        netmask = clients.parse_server(self.conf)['netmask']
        for i in range(2, 13):
            s = str(i)
            name = 'client' + s
            ip = '10.0.0.' + s
            clients.new_client(name, ip, netmask, self.ccd)
        clients.new_client('client1', '10.0.0.129', netmask, self.ccd)

    def test(self):
        expected = '10.0.0.13'
        result = clients.next_available_ip(self.conf, self.ccd)
        self.assertEqual(expected, result)

    def tearDown(self):
        rmtree(self.ccd)

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

    def testDupClient(self):
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        result = clients.new_client(name, ip, netmask, self.ccd)
        self.assertRaises(clients.DuplicateClientError, clients.new_client, name, ip, netmask, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)

if __name__ == '__main__':
    unittest.main
