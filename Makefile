clean:
	rm -rf aihero.egg-info build dist

.PHONY: build
build: clean
	python setup.py check && python setup.py sdist && python setup.py bdist_wheel --universal 

pypi_test: build
	twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*
