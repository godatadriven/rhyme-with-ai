.PHONY: clean clean-test clean-pyc clean-build clean-docs docs help
.PHONY: download-data streamlit
.PHONY: docker-build docker-serve docker-train
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-docs ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean-docs: ## remove built docs
	rm -rf docs/_build

lint: ## check style with pylint
	pylint titanic

test: ## run tests quickly with the default Python
	py.test tests

coverage: ## check code coverage quickly with the default Python
	coverage run --source titanic -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/titanic.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ titanic
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

download-data:
	curl \
		-o data/bert-large-cased-whole-word-masking/config.json \
		https://s3.amazonaws.com/models.huggingface.co/bert/bert-large-cased-whole-word-masking-config.json
	curl \
		-o data/bert-large-cased-whole-word-masking/vocab.txt \
		https://s3.amazonaws.com/models.huggingface.co/bert/bert-large-cased-whole-word-masking-vocab.txt
	curl \
		-o data/bert-large-cased-whole-word-masking/tf_model.h5 \
		https://s3.amazonaws.com/models.huggingface.co/bert/bert-large-cased-whole-word-masking-tf_model.h5

streamlit:
	streamlit run app/app.py

docker-build: ## build a docker container for the package
	docker build --rm -f "Dockerfile" -t textgenerator:latest "."

docker-train: ## train a model insider docker
	docker run --rm -it -p 8080:8080/tcp textgenerator:latest
	#docker run -v `pwd`/model:/model -v `pwd`/../../data:/data \
	#	titanic-model fit --output_path /model/model.pkl /data/train.csv

docker-serve: ## serve a trained model from inside docker
	#docker run -v `pwd`/model:/model -p 5000:5000 titanic-model serve --host 0.0.0.0 /model/model.pkl
	docker run --rm -it -p 8080:8080/tcp textgenerator:latest
