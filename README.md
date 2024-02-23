# pytests

Only once:
```
python -m venv sbase_env
./firstTime.sh
```

Then every time:
```
source sbase_env/Scripts/activate
```
and: 
```
EMAIL=dan_meil@yahoo.com PSWD=xxxx pytest test_y2.py -s --demo
```

## Shufersal
```
MAX_ROWS=3 SAVE=True ACTIVATE=True SHUFF_ID=1234567 pytest test_shufersal.py --uc -s -v
```