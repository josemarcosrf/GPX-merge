.PHONY: clean test lint init check-readme

JOBS ?= 1

help:
	@echo "	install"
	@echo "		Install dependencies and download needed models."
	@echo "	clean"
	@echo "		Remove Python/build artifacts."
	@echo "	formatter"
	@echo "		Apply black formatting to code."
	@echo "	lint"
	@echo "		Lint code with flake8, and check if black formatter should be applied."
	@echo "	types"
	@echo "		Check for type errors using pytype."
	@echo "	pyupgrade"
	@echo "		Uses pyupgrade to upgrade python syntax."
	@echo "	readme-toc"
	@echo "			Generate a Table Of Content for the README.md"
	@echo "	check-readme"
	@echo "		Check if the README can be converted from .md to .rst for PyPI."
	@echo "	test"
	@echo "		Run pytest on tests/."
	@echo "		Use the JOBS environment variable to configure number of workers (default: 1)."
	@echo "	build-docker"
	@echo "		Build package's docker image"
	@echo "	upload-package"
	@echo "		Upload package to Melior Pypi server"
	@echo " git-tag"
	@echo "		Create a git tag based on the current pacakge version and push"


install:
	pip install -r requirements.txt
	pip install -e .
	pip list

clean:
	find . -not \( -path .venv -prune \) -name 'README.md.*' -exec rm -f  {} +
	find . -not \( -path .venv -prune \) -name '*.pyc' -exec rm -f {} +
	find . -not \( -path .venv -prune \) -name '*.pyo' -exec rm -f {} +
	find . -not \( -path .venv -prune \) -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/
	rm -rf docs/_build
	# rm -rf *egg-info
	# rm -rf pip-wheel-metadata

formatter:
	black gptcx --exclude tests/

lint:
	flake8 gptcx tests --exclude tests/
	black --check gptcx tests --exclude tests/

types:
	# https://google.github.io/pytype/
	pytype --keep-going gptcx --exclude gptcx/tests

pyupgrade:
	find gptcx  -name '*.py' | grep -v 'proto\|eggs\|docs' | xargs pyupgrade --py36-plus

readme-toc:
	# https://github.com/ekalinin/github-markdown-toc
	find . -name README.md -exec gh-md-toc --insert {} \;

test: clean
	# OMP_NUM_THREADS can improve overral performance using one thread by process
	# (on tensorflow), avoiding overload
	OMP_NUM_THREADS=1 pytest tests -n $(JOBS) --cov gnes

build-docker:
	# Examples:
	# make build-docker version=0.1
	./scripts/build_docker.sh $(version)

tag:
	git tag $$( python -c 'import gptcx; print(gptcx.__version__)' )
	git push --tags


