clean:
	rm -rf aihero.egg-info build dist aihero/__pycache__

.PHONY: build
build: clean
	pylint --disable=R,C ./**/*.py && python setup.py check && python setup.py sdist && python setup.py bdist_wheel --universal 

pypi_test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi_release:
	twine upload dist/*