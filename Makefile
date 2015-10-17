PYTHON = python
PROG = mog-commons

build:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

uninstall: dev-uninstall
	pip uninstall $(PROG)

dev-install:
	$(PYTHON) setup.py develop

dev-uninstall:
	$(PYTHON) setup.py develop -u

pep8:
	pep8 --max-line-length 120 --ignore E402,E731 src tests

test: pep8
	$(PYTHON) setup.py test

coverage:
	coverage run --source=src setup.py test

clean:
	$(PYTHON) setup.py clean

console:
	cd src && $(PYTHON)

register:
	$(PYTHON) setup.py register

publish:
	$(PYTHON) setup.py sdist upload

.PHONY: build install uninstall dev_install dev_uninstall pep8 test coverage clean console register publish
