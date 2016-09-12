FILES = clients.py tests/test_clients.py

test: 
	nosetests --rednose

lint: pylint pep8

pylint: 
	-$@ ${FILES} | less

pep8: 
	-$@ ${FILES} | less

.PHONY: test pylint pep8 lint
