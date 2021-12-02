.PHONY: default clean pip

default:
	@awk -F\: '/^[a-z_]+:/ && !/default/ {printf "- %-20s %s\n", $$1, $$2}' Makefile


clean: # remove temporary files
	@find . -name \*.pyc -delete
	@find . -name \*.orig -delete
	@find . -name \*.bak -delete
	@find . -name __pycache__ -delete
	@find . -name coverage.xml -delete
	@find . -name test-report.xml -delete
	@find . -name .coverage -delete
	@find . -name build -delete

pip: # install pip libraries
	@pip install -r requirements.txt

pip_test: # install pip test libraries
	@pip install -r requirements-test.txt

start_test_env: # start docker containers and configure test environment
	@./docker/setup/prepare_test_env.sh start

stop_test_env: # stop docker containers
	@./docker/setup/prepare_test_env.sh stop

test: # run tests
	@py.test -v --cov-config .coveragerc --cov-report xml --cov foxha tests

shell:
	@cd docker && docker-compose exec dbrepo bash

release: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

release_globo: clean
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://artifactory.globoi.com/artifactory/api/pypi/pypi-local dist/*

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

develop:
	@python setup.py develop

install:
	@python setup.py install -f
