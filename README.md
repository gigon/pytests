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
* Need to use a chrome profile where i logged-in, and give its path to the script!
* DO NOT run another Chrome instance with same profile at same time (can corrupt!) 
```
SAVE=True ACTIVATE=True MAX_ROWS=30 SHUFERSAL_PROFILE_DIR="$SHUFERSAL_PROFILE_DIR" SHUFERSAL_PROFILE_NAME="$SHUFERSAL_PROFILE_NAME" pytest test_shufersal.py --uc -s -v
```
Just to test:
```
SAVE=False ACTIVATE=False MAX_ROWS=3 SHUFERSAL_PROFILE_DIR="$SHUFERSAL_PROFILE_DIR" SHUFERSAL_PROFILE_NAME="$SHUFERSAL_PROFILE_NAME" pytest test_shufersal.py --uc -s -v
```