import os
import re

class IpsSaturatedError(Exception): pass

class DuplicateClientError(Exception): pass


def parse_conf(conf='/etc/openvpn/server.conf'):

    server = re.compile(r'^server (?P<ip>[0-9.]+) (?P<netmask>[0-9.]+)')
    ccd = re.compile(r'^client-config-dir (?P<ccd>.*)')
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

    return ret

def next_available_ip(conf='/etc/openvpn/server.conf', ccd='/etc/openvpn/clients'):
    ip, netmask, ccd = parse_conf(conf)
    return 'foo'

def new_client(name, ip, netmask, ccd='/etc/openvpn/clients'):
    ifconfig = 'ifconfig_push {0} {1}'.format(ip, netmask)
    config = os.path.join(ccd, name)
    if os.path.isfile(config):
        raise DuplicateClientError
    with open(config, 'w') as f:
        f.write(ifconfig)

    return {'name': name, 'ifconfig': ifconfig}
