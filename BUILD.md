```
rm -rf build
rm -rf dist
python -m build
```

```
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
python -m pip install --index-url https://test.pypi.org/simple/ aihero
```

```
python -m twine upload dist/*
pip install --upgrade aihero
```
