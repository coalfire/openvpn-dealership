PREFIX = /usr/local
PROG = vpn-dealer
SRC = clients.py
FILES = ${SRC} tests/test_clients.py

test: 
	nosetests --rednose

verbose-test: 
	nosetests --verbose --rednose

lint: pylint pep8

pylint: 
	-$@ ${FILES} | less

pep8: 
	-$@ ${FILES} | less

venv:
	virtualenv -p `which python3` venv

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	cp -f ${SRC} ${DESTDIR}${PREFIX}/bin/${PROG}
	chmod 755 ${DESTDIR}${PREFIX}/bin/${PROG}

.PHONY: test verbose-test pylint pep8 lint install venv
