#!/usr/bin/env python3

import os
import re
import ipaddress
import tempfile
import hashlib
import datetime
import math
import time
import functools
import argparse

class IPsSaturatedError(Exception): pass


class DuplicateClientError(Exception): pass

SERVER = '/etc/openvpn/server.conf'
CCD    = '/etc/openvpn/clients'


def lock(func):
    '''
    Return a decorated function
    which locks before running
    and unlocks after running.
    '''

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        lock_kwargs = {}
        if kwargs:
            lock_kwargs = kwargs
        ccd = lock_kwargs.get('ccd', CCD)
        timeout = lock_kwargs.get('timeout', 5)
        wait = lock_kwargs.get('wait', 1)
        lockfile = _wait_for_lock(ccd=ccd, timeout=timeout, wait=wait)

        try:
            result = func(*args, **kwargs)
        finally:
            _unlock_ccd(lockfile)

        return result

    return decorated


def parse_server(conf=SERVER):
    '''
    Return a dict of server info parsed from the server config file.
    '''

    # for example:
    # server 192.168.1.0 255.255.255.0
    server = re.compile(r'^server\s+(?P<ip>[0-9.]+)\s+(?P<netmask>[0-9.]+)')

    # for example:
    # client-config-dir /etc/openvpn/clients
    ccd = re.compile(r'^client-config-dir\s+(?P<ccd>.*)')
    ret = {}

    with open(conf, 'r') as f:
        for line in f:
            match = ccd.search(line)
            if match:
                ret['ccd'] = match.group('ccd')

            match = server.search(line)
            if match:
                ret['ip'] = match.group('ip')
                ret['netmask'] = match.group('netmask')

    # for example: '192.168.1.0/255.255.255.0'
    cidr = '/'.join([ret['ip'], ret['netmask']])

    network = ipaddress.IPv4Network(cidr)

    # we slice off the first address since it is in use by the server
    ret['addresses'] = list(network.hosts())[1:]

    return ret


def used_ips(ccd=CCD):
    '''
    Return a list of ipaddress objects in use by clients in the ccd directory.
    '''

    ips_used = []

    for f in os.listdir(ccd):
        client = parse_client(f, ccd)
        if 'ip' in client:
            ip = client['ip']
            ips_used += [ipaddress.ip_address(ip)]

    return ips_used


def get_new_conf(server=SERVER, ccd=None):
    '''
    Return a dict of next available IP, netmask, and ccd 
    for the server in question.
    We only allow passing in the ccd for testing purposes 
    - you really shouldn't use that parameter.
    '''

    result = {}

    server_dict = parse_server(server)
    addresses = set(server_dict['addresses'])
    if not ccd: 
        ccd = server_dict['ccd']
    ips_in_use = set(used_ips(ccd))
    

    remaining = list(addresses - ips_in_use)
    if len(remaining) == 0:
        raise IPsSaturatedError

    result['ip']      = sorted(remaining)[0].exploded

    result['netmask'] = server_dict['netmask']
    result['ccd']     = server_dict['ccd']

    return result


@lock
def new_client(name, server=SERVER, ccd=None):
    '''
    Create a new client, automagically figuring out the correct network info.
    Return a dict of the client information.
    The ccd parameter is for testing purposes only.
    '''

    conf = {}
    if ccd:
        conf = get_new_conf(server, ccd=ccd)
    else:
        conf = get_new_conf(server)
    ip = conf['ip']

    netmask = conf['netmask']
    if not ccd:
        ccd = conf['ccd']

    return _write_client(name, ip, netmask, ccd)


def _write_client(name, ip, netmask, ccd=CCD):
    '''
    Create a new client file in the ccd directory.
    Return a dict of client information.
    '''

    ifconfig = 'ifconfig_push {0} {1}'.format(ip, netmask)
    config = os.path.join(ccd, name)
    if os.path.isfile(config):
        raise DuplicateClientError
    with open(config, 'w') as f:
        f.write(ifconfig)

    return parse_client(name, ccd=ccd)


@lock
def delete_client(name, ccd=CCD):
    '''
    Delete a client file from the ccd directory.
    Return the full path of the file deleted on success.
    Raise an exception on failure.
    '''
    config = os.path.join(ccd, name)
    os.remove(config) 
    return os.path.abspath(config)


def parse_client(name, ccd=CCD):
    '''
    Return a dict of client information.
    '''

    config = os.path.join(ccd, name)

    # for example:
    # ifconfig_push 192.168.1.2 255.255.255.0
    r = re.compile(r'^ifconfig_push\s+(?P<ip>[0-9.]+)\s+(?P<netmask>[0-9.]+)')

    with open(config, 'r') as c:
        for line in c:
            match = r.search(line)
            if match:
                ip      = match.group('ip')
                netmask = match.group('netmask')

    return {'name': name, 'ip': ip, 'netmask': netmask}


def _try_lock_ccd(ccd=CCD):
    '''
    Create a ccd-specific lockfile.
    Return full path of lockfile if successful.
    Return False if lockfile already exists.
    '''

    tmpdir = tempfile.gettempdir()
    lockdir = os.path.join(tmpdir, 'vpn-dealer')
    os.makedirs(lockdir, exist_ok=True)
    abspath = os.path.abspath(ccd)
    under = abspath.replace('/', '_')
    
    # Our lockfile is named by replacing the CCD's '/' with '_'.
    # Conceivably, a CCD with underscores in the path could clobber another.
    # We add a hash to the lockfile name to enforce uniqueness.
    digest = hashlib.sha256(abspath.encode()).hexdigest()
    fn = under + digest

    lockfile = os.path.join(lockdir, fn)
    pid = str(os.getpid())

    try:
        with open(lockfile, 'x') as f:
            f.write(pid)
        return lockfile
    except:
        return False


def _wait_for_lock(ccd=CCD, timeout=10, wait=1):
    '''
    Wait up to timeout seconds to acheive a lock.
    Recheck every wait seconds. 
    timeout and wait may integers or floating point numbers.
    Return lockfile if lock is acheived,
    Otherwise return False.
    '''

    ms = math.ceil(timeout * 1000)
    timedelta = datetime.timedelta(milliseconds=ms)

    start_time = datetime.datetime.now()
    while True:
        lockfile = _try_lock_ccd(ccd=ccd)
        if lockfile:
            return lockfile
        time.sleep(wait)
        now = datetime.datetime.now()
        if now - start_time > timedelta:
            return False


def _unlock_ccd(lockfile):
    '''
    Remove the specified lockfile.
    Return the full path of the lockfile if successul.
    Raise an exception if not successfile.
    '''

    try:
        os.remove(lockfile)
        return lockfile
    except:
        raise

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('action', choices=['new', 'delete'])
    #parser.add_argument('action', choices=['new', 'delete', 'display'])
    parser.add_argument(
        'client',
        help='Name of the client to act upon',
        )
    parser.add_argument(
        '-s',
        '--server',
        help='Use the server config SERVER. Default to {0}.'.format(SERVER),
        default=SERVER,
        action='store',
        )
    args = parser.parse_args()
    
    actions = {'new': new_client,
               'delete': delete_client,
               #'display': display_client,
               }

    client = args.client
    server = args.server
    action = args.action
    actions[action](client, server=server)

    

if __name__ == '__main__':
    main()

