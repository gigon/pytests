#!/usr/bin/env bash

source sbase_env/Scripts/activate

python -m pip install --upgrade pip
python -m pip install --upgrade wheel
pip install -r requirements.txt

#pip install seleniumbase
#pip install pandas
#pip install Pyarrow
