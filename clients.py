import os

class IpsSaturatedError(Exception): pass

class DuplicateClientError(Exception): pass

conf = '/etc/openvpn/server.conf'

def next_available_ip():
    return 'foo'

def new_client(name, ip, netmask, ccd='/etc/openvpn/clients'):
    ifconfig = 'ifconfig_push {0} {1}'.format(ip, netmask)
    config = os.path.join(ccd, name)
    print(ccd)
    print(config)
    print(ifconfig)
    with open(config, 'w') as f:
        f.write(ifconfig)

    return {'name': name, 'ifconfig': ifconfig}

    

