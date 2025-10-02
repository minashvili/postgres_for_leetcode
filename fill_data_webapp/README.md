# Fill Data WebApp

## How to run the application locally
### Prerequisites:
```
Python 3.12
virtualenv (optional but recommended)
```

### Steps:

Clone the repository:
``` bash
git clone https://github.com/minashvili/postgres_for_leetcode.git
cd postgres_for_leetcode
```

Create and activate a virtual environment (optional but recommended): 
``` bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
``` bash
pip install -r requirements.txt
```

Run the application:  
``` bash
python -m fill_data_webapp
```

Access the application in your browser at http://127.0.0.1:8005.  

# How to install pre-commit hook
## Steps:
1. Install the pre-commit package:  
``` bash
pip install pre-commit
```
2. Install the hooks defined in .pre-commit-config.yaml:  
``` bash
pre-commit install
```
3. Verify the hooks are installed:  
``` bash
4. pre-commit run --all-files
```
Now, the pre-commit hooks will automatically run before each commit to ensure code quality and consistency.

## Manual Check

### Check and fix code automatically:
```bash
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
