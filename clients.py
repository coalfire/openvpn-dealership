import os
import re
import ipaddress
import tempfile


class IPsSaturatedError(Exception): pass


class DuplicateClientError(Exception): pass


def parse_server(conf='/etc/openvpn/server.conf'):
    """
    Return a dict of server info parsed from the server config file.
    """

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


def used_ips(ccd='/etc/openvpn/clients'):
    """
    Return a list of ipaddress objects in use by clients in the ccd directory.
    """

    ips_used = []

    for f in os.listdir(ccd):
        client = parse_client(f, ccd)
        if 'ip' in client:
            ip = client['ip']
            ips_used += [ipaddress.ip_address(ip)]

    return ips_used


def next_available_ip(conf='/etc/openvpn/server.conf',
                      ccd='/etc/openvpn/clients'):
    """
    Return a string representation of the next IP in the server's range
    not in used by a client in the ccd directory.
    """

    config = parse_server(conf)
    addresses = set(config['addresses'])
    ips_in_use = set(used_ips(ccd))

    remaining = list(addresses - ips_in_use)
    if len(remaining) == 0:
        raise IPsSaturatedError
    return sorted(remaining)[0].exploded


def new_client(name, ip, netmask, ccd='/etc/openvpn/clients'):
    """
    Create a new client file in the ccd directory.
    Return a dict of client information.
    """

    ifconfig = 'ifconfig_push {0} {1}'.format(ip, netmask)
    config = os.path.join(ccd, name)
    if os.path.isfile(config):
        raise DuplicateClientError
    with open(config, 'w') as f:
        f.write(ifconfig)

    return parse_client(name, ccd=ccd)

def delete_client(name, ccd='/etc/openvpn/clients'):
    """
    Delete a client file from the ccd directory.
    Return the full path of the file deleted on success.
    Raise an exception on failure.
    """
    config = os.path.join(ccd, name)
    os.remove(config) 
    return os.path.abspath(config)

def parse_client(name, ccd='/etc/openvpn/clients'):
    """
    Return a dict of client information.
    """

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


def lock_ccd(ccd='/etc/openvpn/clients'):
    """
    Create a ccd-specific lockfile.
    Return full path of lockfile if successful.
    Return False if lockfile already exists.
    """

    tmpdir = tempfile.gettempdir()
    lockdir = os.path.join(tmpdir, 'vpn-dealer')
    os.makedirs(lockdir, exist_ok=True)

    abspath = os.path.abspath(ccd)
    fn = abspath.replace('/', '_')
    lockfile = os.path.join(lockdir, fn)
    pid = str(os.getpid())

    try:
        with open(lockfile, 'x') as f:
            f.write(pid)
        return lockfile
    except:
        return False


def remove_ccd_lock(lockfile):
    """
    Remove the specified lockfile.
    Return the full path of the lockfile if successul.
    Raise an exception if not successfile.
    """

    print(lockfile)
    try:
        os.remove(lockfile)
        return lockfile
    except:
        raise
