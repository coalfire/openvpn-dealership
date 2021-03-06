PREFIX = /usr/local
PROG = vpn-dealer
SRC = clients.py
FILES = ${SRC} tests/test_clients.py

test: 
	nosetests --rednose

verbose-test: 
	nosetests --verbose --rednose

lint: pylint pycodestyle black py.test mccabe

pylint: 
	-$@ --rcfile pylint.cfg ${FILES}

pycodestyle: 
	-$@ ${FILES}

black:
	-$@ ${FILES}

coverage: py.test

py.test:
	-$@ --cov-report term-missing --cov=clients tests/test_clients.py

mccabe: 
	-python -m $@ --min 10 ${FILES}

venv:
	virtualenv -p `which python3` venv

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	cp -f ${SRC} ${DESTDIR}${PREFIX}/bin/${PROG}
	chmod 755 ${DESTDIR}${PREFIX}/bin/${PROG}

.PHONY: test verbose-test pylint pycodestyle black coverage py.test mccabe lint install venv
