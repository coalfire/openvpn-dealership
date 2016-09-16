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
        expected = '255.255.255.0'
        result = clients.parse_server(self.conf)['netmask']
        self.assertEqual(expected, result)

    def testIP(self):
        expected = '10.0.0.0'
        result = clients.parse_server(self.conf)['ip']
        self.assertEqual(expected, result)

    def testCCD(self):
        expected = '/etc/openvpn/clients'
        result = clients.parse_server(self.conf)['ccd']
        self.assertEqual(expected, result)

    def testAddresses(self):
        # 256 in a /24 minus the broadcast, network, and server addresses
        expected = 253

        result = clients.parse_server(self.conf)['addresses']
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
            clients._write_client(name, ip, netmask, self.ccd)

    def testUsedIPs(self):
        expected = 10
        result = clients.used_ips(self.ccd)
        self.assertEqual(expected, len(result))

    def tearDown(self):
        rmtree(self.ccd)


class GetNewConfTest(unittest.TestCase):
    
    def setUp(self):
        self.ccd = './tests/files/ccd_empty'
        os.makedirs(self.ccd)
        self.server = './tests/files/server.conf'
        self.netmask = clients.parse_server(self.server)['netmask']

    def testThereAreNoClients(self):
        expected = {
                'ip': '10.0.0.2',
                'netmask': '255.255.255.0',
                'ccd': '/etc/openvpn/clients',
                }
        result = clients.get_new_conf(server=self.server, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testClientsHaveAnOpening(self):
        for i in range(2, 13):
            s = str(i)
            name = 'client' + s
            ip = '10.0.0.' + s
            clients._write_client(name, ip, self.netmask, self.ccd)
        clients._write_client('client1', '10.0.0.129', self.netmask, self.ccd)

        expected = {
                'ip': '10.0.0.13',
                'netmask': '255.255.255.0',
                'ccd': '/etc/openvpn/clients',
                }
        result = clients.get_new_conf(server=self.server, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testNoIPsAvailable(self):
        for i in range(2, 255):
            s = str(i)
            name = 'client' + s
            ip = '10.0.0.' + s
            clients._write_client(name, ip, self.netmask, self.ccd)

        err = clients.IPsSaturatedError
        self.assertRaises(err,
                          clients.get_new_conf,
                          server=self.server,
                          ccd=self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class NewClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)
        self.server = './tests/files/server.conf'

    def testNewClientTest(self):
        name = 'dummy'

        expected = {
            'name':    name,
            'ip':      '10.0.0.2',
            'netmask': '255.255.255.0',
            }
        result = clients.new_client(name, server=self.server, ccd=self.ccd)
        self.assertEqual(expected, result)

    def tearDown(self):
        rmtree(self.ccd)


class WriteClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)

    def testWriteClient(self):
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'

        expected = {
            'name':    name,
            'ip':      ip,
            'netmask': netmask,
            }
        result = clients._write_client(name, ip, netmask, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testDupClient(self):
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        name = 'dummy'
        clients._write_client(name, ip, netmask, self.ccd)

        err = clients.DuplicateClientError
        self.assertRaises(err, clients._write_client, name, ip, netmask, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class DeleteClientTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        os.makedirs(self.ccd)
        self.name = 'dummy'
        ip = '10.0.0.2'
        netmask = '255.255.255.0'
        clients._write_client(self.name, ip, netmask, self.ccd)

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
        clients._write_client(self.name, self.ip, self.netmask, ccd=self.ccd)

        expected = {
            'name':    self.name,
            'ip':      self.ip,
            'netmask': self.netmask,
            }
        result = clients.parse_client(self.name, ccd=self.ccd)
        self.assertEqual(expected, result)

    def testClientMissing(self):
        name = 'does_not_exist'
        err = FileNotFoundError
        self.assertRaises(err, clients.parse_client, name, self.ccd)

    def tearDown(self):
        rmtree(self.ccd)


class TryLockCCDTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        self.lockfile = clients._try_lock_ccd(ccd=self.ccd)
        self.lockfile2 = ''

    def testTryLockCCD(self):
        self.assertTrue(self.lockfile)

    def testTryLockedLockCCD(self):
        self.assertFalse(clients._try_lock_ccd(ccd=self.ccd))

    def testPathHashing(self):
        abspath = os.path.abspath(self.ccd)
        path_components = abspath.split(os.sep)[1:]

        # for example: 'etc_openvpn_clients'
        underscored = '_'.join(path_components)

        # for example: '/etc_openvpn_clients'
        non_unique = os.sep + underscored 

        self.lockfile2 = clients._try_lock_ccd(ccd=non_unique)
        self.assertTrue(self.lockfile2)

    def tearDown(self):
        os.remove(self.lockfile)
        if self.lockfile2:
            os.remove(self.lockfile2)


class WaitForLockTest(unittest.TestCase):
    def setUp(self):
        self.ccd = './tests/clients/ccd'
        self.lockfile = ''

    def testNotLocked(self):
        self.lockfile = clients._wait_for_lock(ccd=self.ccd, timeout=1, wait=0.5)
        self.assertTrue(self.lockfile)
    
    def testTimeoutLocked(self):
        self.lockfile = clients._try_lock_ccd(ccd=self.ccd)
        self.assertFalse(clients._wait_for_lock(ccd=self.ccd, timeout=0.1, wait=0.1))

    def tearDown(self):
        os.remove(self.lockfile)


class RemoveCCDLockTest(unittest.TestCase):

    def setUp(self):
        self.ccd = './tests/clients/ccd'
        self.lockfile = clients._try_lock_ccd(self.ccd)
        self.fakelockfile = './tests/files/nosuchlockfile'

    def testRemoveCCDLockTest(self):
        expected = self.lockfile
        result = clients._unlock_ccd(self.lockfile)
        self.assertEqual(expected, result)

    def tearDown(self):
        try:
            os.remove(self.lockfile)
        except OSError:
            pass


@unittest.skip("Not implemented yet")
class DisplayClientTest(unittest.TestCase):

    def setUp(self):
        pass

    def testDisplayClient(self):
        self.assertTrue(False)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main
