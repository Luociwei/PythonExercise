#!/bin/bash
# precondition:
# for coverage:
# pip install pytest --user
# pip install pytest-cov --user

# pip install pytest-pep8 --user
# pip install mock --user

basepath=$(cd `dirname $0`; pwd)
export PYTHONPATH=$basepath
#source testenv/bin/activate
pytest -vv --cov-config=.coveragerc --pep8 --cov=. --cov-report=term --cov-report=html:htmlcov --ignore=dependencies $@
#deactivate
