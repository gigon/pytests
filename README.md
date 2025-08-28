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
The automation uses undetected-chrome mode (`--uc`) for stealth browsing and bypassing bot detection.
Session persistence is handled via JSON cookie files, not Chrome profiles.

### Environment Setup
Create a `.env` file with your credentials:
```
SHUFERSAL_EMAIL=your.email@example.com
SHUFERSAL_PSWD=your_password
```

### Usage
Run the shell script (recommended):
```bash
./SHUFERSAL.sh
```

Or run directly with pytest:
```bash
# Production run
SAVE=True ACTIVATE=True MAX_ROWS=30 pytest test_shufersal.py --uc -s -v

# Test run (limited coupons, no activation)
SAVE=False ACTIVATE=False MAX_ROWS=3 pytest test_shufersal.py --uc -s -v
```
#### Run headless like in github wokflow:
```
ACTIVATE=False MAX_ROWS=2 SAVE=True pytest test_shufersal.py -s -v --uc --headless
```
### Features
- **Undetected Chrome Mode**: Bypasses bot detection automatically
- **Cookie Persistence**: Saves login sessions in JSON files for reuse
- **Auto Login**: Handles Hebrew interface and login flow
- **Data Export**: Saves coupon data to timestamped CSV files
- **Smart Activation**: Only activates available coupons