import unittest
import os
import sys
from shutil import rmtree
sys.path.insert(0, os.path.abspath('..'))

import clients


class ParseServerTest(unittest.TestCase):

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


class NextAvailableIPTest(unittest.TestCase):
    
    def setUp(self):
        self.ccd = './tests/files/ccd_empty'
        os.makedirs(self.ccd)
        self.conf = './tests/files/server.conf'
        self.netmask = clients.parse_server(self.conf)['netmask']

    def testThereAreNoClients(self):
        expected = '10.0.0.2'
        result = clients.next_available_ip(conf=self.conf, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testClientsHaveAnOpening(self):
        for i in range(2, 13):
            s = str(i)
            name = 'client' + s
            ip = '10.0.0.' + s
            clients.new_client(name, ip, self.netmask, self.ccd)
        clients.new_client('client1', '10.0.0.129', self.netmask, self.ccd)

        expected = '10.0.0.13'
        result = clients.next_available_ip(self.conf, self.ccd)
        self.assertEqual(expected, result)

    def testNoIPsAvailable(self):
        for i in range(2, 255):
            s = str(i)
            name = 'client' + s
            ip = '10.0.0.' + s
            clients.new_client(name, ip, self.netmask, self.ccd)

        err = clients.IPsSaturatedError
        self.assertRaises(err, clients.next_available_ip, self.conf, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class NewClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)

    def testNewClient(self):
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        expected = {
            'name':    name,
            'ip':      ip,
            'netmask': netmask,
            }
        result = clients.new_client(name, ip, netmask, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testDupClient(self):
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        clients.new_client(name, ip, netmask, self.ccd)

        err = clients.DuplicateClientError
        self.assertRaises(err, clients.new_client, name, ip, netmask, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class DeleteClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)
        self.name = 'dummy'
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        clients.new_client(self.name, ip, netmask, self.ccd)

    def testDeleteClient(self):
        path = os.path.join(self.ccd, self.name)
        expected = os.path.abspath(path)
        result = clients.delete_client(self.name, ccd=self.ccd)

        self.assertEqual(expected, result)
        self.assertFalse(os.path.isfile(path))

    def testClientMissing(self):
        name = 'does_not_exist'
        err = FileNotFoundError
        self.assertRaises(err, clients.delete_client, name, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class ParseClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)

    def testParseClient(self):
        self.ip = '10.0.0.2'
        self.netmask = '255.255.255.0'
        self.name = 'dummy'
        clients.new_client(self.name, self.ip, self.netmask, ccd=self.ccd)

        result = clients.parse_client(self.name, ccd=self.ccd)
        expected = {
            'name':    self.name,
            'ip':      self.ip,
            'netmask': self.netmask,
            }
        self.assertEqual(expected, result)

    def testClientMissing(self):
        name = 'does_not_exist'
        err = FileNotFoundError
        self.assertRaises(err, clients.parse_client, name, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class LockCCDTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        self.lockfile = clients.lock_ccd(self.ccd)

    def testLockCCD(self):
        self.assertTrue(self.lockfile)

    def testLockedLockCCD(self):
        self.assertFalse(clients.lock_ccd(self.ccd))

    def tearDown(self):
        if self.lockfile:
            os.remove(self.lockfile)


class RemoveCCDLockTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        self.lockfile = clients.lock_ccd(self.ccd)
        print(self.lockfile)
        self.fakelockfile = './tests/files/nosuchlockfile'

    def testRemoveCCDLockTest(self):
        expected = self.lockfile
        result = clients.remove_ccd_lock(self.lockfile)
        self.assertEqual(expected, result)

    def tearDown(self):
        try:
            os.remove(self.lockfile)
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main
