```
rm -rf build
rm -rf dist
python3 -m build
```

```
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
python3 -m pip install --index-url https://test.pypi.org/simple/ aihero
```

```
python3 -m twine upload dist/*
pip install --upgrade aihero
```