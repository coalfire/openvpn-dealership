class IpsSaturatedError(Exception): pass

class DuplicateClientError(Exception): pass

clients_dir = '/etc/openvpn/clients'
conf = '/etc/openvpn/server.conf'

def next_available_ip():
    return 'foo'

def new_client(name, ip, netmask):
    pass

