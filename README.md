# vpn-dealership

Auto-create static openvpn client configs

## installation

`make install`

## usage

    vpn-dealer [-h] [-s SERVER] new CLIENT
    vpn-dealer [-h] [-s SERVER] delete CLIENT
    vpn-dealer [-h] [-s SERVER] show CLIENT

where `SERVER` is a vpn server configuration file
(defaulting to `/etc/openvpn/server.conf`),
and `CLIENT` is the name of a client.

## requirements

* openvpn
* python 3.3 or higher (for `ipaddress`)

## testing/devel requirements

* make
* nosetest
* rednose
* pylint
* pep8

## testing

Run `make` in the top directory.

## concept

The vpn server should not host the CA. 
A provisioning server should host the CA,
and scp keys over to the vpn server.
The provisioning server should not be accessible from the vpn server.

Sample server and client configs can be found in [examples](examples),
along with stubs for CA, server, and client setup scripts.
