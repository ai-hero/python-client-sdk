build:
	python setup.py check && python setup.py sdist && python setup.py bdist_wheel --universal 

pypi_test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
