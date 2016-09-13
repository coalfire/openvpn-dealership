# vpn-dealership

Auto-create openvpn client configs

This project is currently not functional.
Watch or check in later for updates.

## requirements
* openvpn
* python3.3 or higher (for `ipaddress`)

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
