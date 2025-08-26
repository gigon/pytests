#!/usr/bin/env bash

# Comprehensive logging for Windows Task Scheduler
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/shufersal_execution_$(date +%Y%m%d_%H%M%S).log"
LATEST_LOG="$LOG_DIR/shufersal_latest.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages with timestamp
log_message() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to log and echo
log_echo() {
    echo "$*" | tee -a "$LOG_FILE"
}

# Start logging
log_message "INFO" "=== SHUFERSAL AUTOMATION EXECUTION STARTED ==="
log_message "INFO" "Log file: $LOG_FILE"
log_message "INFO" "Execution started by: $(whoami) on $(hostname)"

# Redirect all output to both console and log file
exec > >(tee -a "$LOG_FILE") 2>&1

source sbase_env/Scripts/activate

# Load credentials from .env file if it exists
if [ -f .env ]; then
    log_message "INFO" "Loading environment variables from .env file..."
    export $(grep -E '^SHUFERSAL_EMAIL=' .env | xargs)
    export $(grep -E '^SHUFERSAL_PSWD=' .env | xargs)
    
    # Check if credentials were loaded (without exposing them)
    if [ -n "$SHUFERSAL_EMAIL" ] && [ -n "$SHUFERSAL_PSWD" ]; then
        log_message "INFO" "Credentials loaded successfully"
    else
        log_message "ERROR" "Failed to load credentials from .env file"
    fi
else
    log_message "WARNING" ".env file not found"
fi

log_message "INFO" "Checking for running Chrome and driver instances..."

# Use our cross-platform cleanup script
if [ -f "./cleanup_processes.sh" ]; then
    log_message "INFO" "Running cross-platform process cleanup..."
    ./cleanup_processes.sh cleanup
else
    log_message "ERROR" "cleanup_processes.sh not found! Cannot proceed without proper process cleanup."
    log_message "ERROR" "Please ensure cleanup_processes.sh exists in the current directory."
    exit 1
fi

log_message "INFO" "Starting Shufersal automation with undetected-chrome mode..."

# Run tests with environment variables (undetected-chrome mode for stealth)
# Note: --uc mode uses temporary profiles, persistent Chrome profiles are not supported

# Set defaults if not already set
SAVE=${SAVE:-True}
ACTIVATE=${ACTIVATE:-True}
MAX_ROWS=${MAX_ROWS:-300}

log_message "INFO" "Configuration: SAVE=$SAVE ACTIVATE=$ACTIVATE MAX_ROWS=$MAX_ROWS"

# Run the test and capture exit code
log_message "INFO" "Executing pytest command..."
SAVE=$SAVE ACTIVATE=$ACTIVATE MAX_ROWS=$MAX_ROWS pytest test_shufersal.py -s -v --uc
PYTEST_EXIT_CODE=$?

# Log execution results
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    log_message "SUCCESS" "✅ SHUFERSAL AUTOMATION COMPLETED SUCCESSFULLY"
    log_message "SUCCESS" "Exit code: $PYTEST_EXIT_CODE"
    
    # Check if any coupons were found (look for CSV files)
    if ls data/*.csv 1> /dev/null 2>&1; then
        LATEST_CSV=$(ls -t data/*.csv | head -n1)
        if [ -f "$LATEST_CSV" ]; then
            COUPON_COUNT=$(tail -n +2 "$LATEST_CSV" | wc -l)
            log_message "SUCCESS" "Found CSV file: $LATEST_CSV with $COUPON_COUNT coupons"
        fi
    fi
else
    log_message "ERROR" "❌ SHUFERSAL AUTOMATION FAILED"
    log_message "ERROR" "Exit code: $PYTEST_EXIT_CODE"
    
    # Check for common error patterns in the log
    if grep -q "GEO-BLOCKING DETECTED" "$LOG_FILE"; then
        log_message "ERROR" "Failure reason: Geographic blocking detected (non-Israeli IP)"
    elif grep -q "Login failed" "$LOG_FILE"; then
        log_message "ERROR" "Failure reason: Login authentication failed"
    elif grep -q "NO COUPONS FOUND" "$LOG_FILE"; then
        log_message "ERROR" "Failure reason: No coupons found on the page"
    else
        log_message "ERROR" "Failure reason: Unknown error - check log details above"
    fi
fi

# Copy to latest log for easy access
cp "$LOG_FILE" "$LATEST_LOG"

log_message "INFO" "=== EXECUTION COMPLETED ==="
log_message "INFO" "Latest log available at: $LATEST_LOG"

# Exit with the same code as pytest for Task Scheduler
exit $PYTEST_EXIT_CODE
