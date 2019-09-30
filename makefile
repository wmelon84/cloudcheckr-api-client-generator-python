all: dev

deploy:
	pip install -r requirements.txt

dev: 
	pip install -r requirements-dev.txt

# freeze:
# 	pip freeze | sort | grep -v ''

test:
	cd tests && ( pytest -rXs -vv --cov-report html --cov-report term-missing --cov pyramide )

doc: 
	cd docs && make html

find-version:
	egrep --recursive "(version|__version__|release) ?= ?['\"]\d+\.\d+\.\d+['\"]" .


build:
	python setup.py build bdist_wheel

install:
	python setup.py install