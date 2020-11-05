#!/bin/bash

basepath=$(cd `dirname $0`; pwd)
export PYTHONPATH=$basepath

if [[ -d virtualenv ]]; then
	rm -rf virtualenv
fi
virtualenv virtualenv --no-site-packages
source virtualenv/bin/activate
pip install -r requirements.txt
python start_python_rpc_server.py
deactivate
rm -rf virtualenv