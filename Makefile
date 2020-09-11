TARGETS=build clean dependencies check deploy install test uninstall
VERSION=`cat VERSION`
all:
	@echo "Try one of: ${TARGETS}"

build: clean
	python setup.py sdist
	python setup.py bdist_wheel --universal

clean:
	python setup.py clean --all
	find . -name '*.pyc' -delete
	rm -rf dist *.egg-info __pycache__ build

dependencies: requirements.txt
	pip install -r requirements.txt

check: build
	twine check dist/*

deploy: build
	twine upload dist/*

install: build dependencies
	pip install dist/*.whl

tag:
	git tag v${VERSION}

test:
	@echo "test"

uninstall: clean
	pip uninstall -y bikaclient