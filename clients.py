import os
import re
import ipaddress

class IpsSaturatedError(Exception): pass

class DuplicateClientError(Exception): pass

def parse_server(conf='/etc/openvpn/server.conf'):

    server = re.compile(r'^server\s+(?P<ip>[0-9.]+)\s+(?P<netmask>[0-9.]+)')
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
    push = re.compile(r'^ifconfig_push\s+(?P<ip>[0-9.]+)\s+(?P<netmask>[0-9.]+)')
    used_ips = []

    for f in os.listdir(ccd):
        config = os.path.join(ccd, f)
        with open(config, 'r') as c:
            for line in c:
                match = push.search(line)
                if match:
                    ip = match.group('ip')
                    used_ips += [ipaddress.ip_address(ip)]

    return used_ips

def next_available_ip(conf='/etc/openvpn/server.conf', ccd='/etc/openvpn/clients'):
    config = parse_server(conf)
    addresses = set(config['addresses'])
    ips_in_use = set(used_ips(ccd))

    remaining = sorted(list(addresses - ips_in_use))
    return remaining[0].exploded

def new_client(name, ip, netmask, ccd='/etc/openvpn/clients'):
    ifconfig = 'ifconfig_push {0} {1}'.format(ip, netmask)
    config = os.path.join(ccd, name)
    if os.path.isfile(config):
        raise DuplicateClientError
    with open(config, 'w') as f:
        f.write(ifconfig)

    return {'name': name, 'ifconfig': ifconfig}
