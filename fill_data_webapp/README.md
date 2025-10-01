## Check and fix code automatically:
``` bash
ruff check . --fix
```

## Format code
``` bash
ruff format .
```

## Run unit tests and check test coverage
``` bash
python -m coverage run -m pytest
python -m coverage report -m 
```