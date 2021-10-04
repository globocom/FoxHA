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
	@py.test -v --cov-config .coveragerc --cov-report html --cov foxha tests

shell:
	@cd docker && docker-compose exec dbrepo bash

release:
	python setup.py sdist upload

release_globo:
	python setup.py sdist upload -r ipypiglobo
