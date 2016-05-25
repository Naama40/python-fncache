.PHONY: tests devinstall
APP=fncache
COV=fncache
OPTS=

tests:
	py.test $(APP)

devinstall:
	pip install -e .
	pip install -e .[tests]
