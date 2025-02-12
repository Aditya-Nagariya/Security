#!/bin/bash
# =============================================================================
# SECURITY MAINTENANCE SCRIPT
#
# =============================================================================

########################################
#       INITIAL SETUP & FUNCTIONS      #
########################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global Variables
LOG_DIR="/var/log/security_maintenance"
LOG_FILE="$LOG_DIR/security_scan_$(date +%Y%m%d_%H%M%S).log"
START_TIME=$(date +%s)

# Create log directory and file
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

# Redirect stdout and stderr to both console and log file
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Logging function with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

# Enhanced print functions with borders for a better look
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
    log "[STATUS] $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
    log "[ERROR] $1"
}

print_warning() {
    echo -e "${YELLOW}[*]${NC} $1"
    log "[WARNING] $1"
}

# Function to print the disclaimer and warning in the terminal
print_disclaimer() {
    echo -e "${RED}=============================================================================${NC}"
    echo -e "${RED}SECURITY MAINTENANCE SCRIPT${NC}"
    echo -e "${RED}=============================================================================${NC}"
    echo -e "${RED}DISCLAIMER:${NC}"
    echo -e "${RED}  THIS SCRIPT IS PROVIDED \"AS IS\" WITHOUT ANY WARRANTY OF ANY KIND,${NC}"
    echo -e "${RED}  EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES${NC}"
    echo -e "${RED}  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.${NC}"
    echo -e "${RED}  USE THIS SCRIPT AT YOUR OWN RISK. THE AUTHOR IS NOT RESPONSIBLE FOR ANY${NC}"
    echo -e "${RED}  DAMAGE, DATA LOSS, OR SYSTEM INSTABILITY THAT MAY RESULT FROM ITS USE.${NC}"
    echo ""
    echo -e "${RED}WARNING:${NC}"
    echo -e "${RED}  THIS SCRIPT MAKES SYSTEM-LEVEL CHANGES, INCLUDING PACKAGE UPGRADES,${NC}"
    echo -e "${RED}  SECURITY SCANS, AND FILE DELETIONS. INTERRUPTING CRITICAL OPERATIONS${NC}"
    echo -e "${RED}  (E.G., SYSTEM UPDATES OR VIRUS DATABASE UPDATES) MAY RESULT IN AN UNSTABLE${NC}"
    echo -e "${RED}  OR BROKEN SYSTEM. PLEASE TEST IN A SAFE ENVIRONMENT BEFORE DEPLOYING${NC}"
    echo -e "${RED}  IN PRODUCTION.${NC}"
    echo ""
    echo -e "${RED}BY USING THIS SCRIPT, YOU AGREE THAT THE AUTHOR IS NOT RESPONSIBLE FOR ANY${NC}"
    echo -e "${RED}  DAMAGES OR LOSSES INCURRED.${NC}"
    echo -e "${RED}=============================================================================${NC}"
    echo ""
    read -p "Press Enter to acknowledge and continue, or Ctrl+C to abort... " ack
}

# Display a fancy ASCII banner using figlet if available
display_banner() {
    if command -v figlet &>/dev/null; then
        figlet -c "Security Maintenance"
    else
        echo -e "${BLUE}========================================"
        echo -e "      SECURITY MAINTENANCE SCRIPT"
        echo -e "========================================${NC}"
    fi
}
display_banner

# Print the disclaimer at startup
print_disclaimer

# Trap function for cleanup on exit/interruption
cleanup() {
    print_warning "Script interrupted. Cleaning up background processes..."
    pkill -P $$ 2>/dev/null
    exit 1
}
trap cleanup SIGINT SIGTERM

########################################
#  ADVANCED PROGRESS BAR ANIMATION     #
########################################

# Function: run_task_with_progress
# Runs a given command in the background and displays a dynamic progress bar
run_task_with_progress() {
    local task_desc="$1"
    local cmd="$2"
    local est_time="$3"  # estimated time in seconds
    local bar_width=50
    local spinner_chars=( '|' '/' '-' '\\' )
    local spinner_index=0

    print_status "Starting: $task_desc (Estimated: ${est_time}s)"
    log "Starting task: $task_desc"

    # Run the command in the background
    eval "$cmd" &
    local pid=$!
    local elapsed=0

    # Animate until the command finishes
    while kill -0 $pid 2>/dev/null; do
        local percent=$(( elapsed * 100 / est_time ))
        if [ $percent -ge 100 ]; then
            percent=99
        fi
        local filled=$(( percent * bar_width / 100 ))
        local unfilled=$(( bar_width - filled ))
        local bar_filled=$(printf '%0.s█' $(seq 1 $filled))
        local bar_unfilled=$(printf '%0.s-' $(seq 1 $unfilled))
        local spinner=${spinner_chars[$spinner_index]}
        spinner_index=$(( (spinner_index + 1) % ${#spinner_chars[@]} ))
        printf "\r${GREEN}%-30s${NC}: [${bar_filled}${bar_unfilled}] %3d%% %s - Elapsed: %02ds" \
            "$task_desc" "$percent" "$spinner" "$elapsed"
        sleep 1
        ((elapsed++))
    done

    # Wait for command to complete and capture exit status
    wait $pid
    local exit_status=$?
    # Show 100% on completion
    local bar_filled=$(printf '%0.s█' $(seq 1 $bar_width))
    printf "\r${GREEN}%-30s${NC}: [${bar_filled}] 100%% - Completed in %02ds\n" "$task_desc" "$elapsed"

    if [ $exit_status -eq 0 ]; then
        print_status "$task_desc completed successfully."
    else
        print_error "$task_desc failed with exit status $exit_status."
    fi
    return $exit_status
}

########################################
#         USER SELECTION MENU          #
########################################

clear
display_banner
echo -e "${BLUE}Welcome to the Ultimate Kali Linux Security Maintenance Script${NC}"
echo -e "${BLUE}Please select the desired scan intensity:${NC}"
echo -e "${GREEN}1) Light Scan ${NC}(Critical areas only - Faster)"
echo -e "${GREEN}2) Medium Scan ${NC}(System + important directories)"
echo -e "${GREEN}3) Deep Scan ${NC}(Full system scan)"
read -p "Enter your choice (1-3): " scan_choice

case $scan_choice in
    1) SCAN_PATHS="/etc /usr /var /home"; TIME_ESTIMATE=600 ;;   # ~10 minutes estimated
    2) SCAN_PATHS="/"; TIME_ESTIMATE=3600 ;;                    # ~1 hour estimated
    3) SCAN_PATHS="/"; TIME_ESTIMATE=7200 ;;                    # ~2 hours estimated
    *) print_warning "Invalid choice, defaulting to Medium Scan"; SCAN_PATHS="/"; TIME_ESTIMATE=3600 ;;
esac
print_status "Scan mode: $scan_choice - Estimated Time: ${TIME_ESTIMATE}s"

# Display estimated time per GB table for ClamAV
print_status "Estimated Time Per GB for ClamAV (clamscan):"
printf "%-40s %-20s %-20s\n" "System Type" "Time per GB (SSD)" "Time per GB (HDD/VM)"
printf "%-40s %-20s %-20s\n" "----------------------------------------" "--------------------" "--------------------"
printf "%-40s %-20s %-20s\n" "Light System (Few Large Files)" "30 sec – 2 min" "1 – 3 min"
printf "%-40s %-20s %-20s\n" "Moderate System (Mixed Files)" "2 – 5 min" "3 – 7 min"
printf "%-40s %-20s %-20s\n" "Heavy System (Millions of Small Files)" "5 – 10+ min" "7 – 15+ min"
echo ""

########################################
#        MAINTENANCE TASKS             #
########################################

print_status "Starting Kali Linux Security Maintenance..."

# Task 1: System Update & Upgrade
run_task_with_progress "System Update & Upgrade" \
    "apt update && apt full-upgrade -y && apt autoremove -y && apt autoclean" 300

# Task 2: Fix Broken Dependencies
run_task_with_progress "Fix Broken Dependencies" "apt --fix-broken install -y" 60

# Task 3: Install Essential Security Tools
run_task_with_progress "Install Security Tools" "apt install -y rkhunter chkrootkit clamav clamav-daemon preload htop iotop nmon" 120

# Task 4: Clean System Logs
run_task_with_progress "Clean System Logs" "journalctl --vacuum-time=7d" 30

# Task 5: Update ClamAV Database
run_task_with_progress "Update ClamAV Database" \
    "systemctl stop clamav-freshclam && freshclam && systemctl start clamav-freshclam" 120

# Task 6: Run RKHunter Scan
run_task_with_progress "Run RKHunter" "rkhunter --update && rkhunter --propupd && rkhunter --check --sk" 300

# Task 7: Run ChkRootkit Scan
run_task_with_progress "Run ChkRootkit" "chkrootkit" 180

# Task 8: Multi-threaded ClamAV Scan
if command -v clamdscan &>/dev/null; then
    CLAM_CMD="clamdscan -r --multiscan --remove --exclude-dir='^/sys|^/proc|^/dev' $SCAN_PATHS"
    TASK_DESC="Multi-threaded ClamAV Scan (clamdscan)"
else
    CLAM_CMD="clamscan -r --bell --remove --multiscan --exclude-dir='^/sys|^/proc|^/dev' $SCAN_PATHS"
    TASK_DESC="Multi-threaded ClamAV Scan (clamscan)"
fi
run_task_with_progress "$TASK_DESC" "$CLAM_CMD" $TIME_ESTIMATE

# Task 9: Disk Space & System Resource Check
print_status "Checking Disk Space..."
df -h | tee -a "$LOG_FILE"
print_status "Current System Resource Usage:"
top -b -n 1 | head -n 20 | tee -a "$LOG_FILE"

########################################
#            FINAL SUMMARY             #
########################################

END_TIME=$(date +%s)
TOTAL_TIME=$(( END_TIME - START_TIME ))
print_status "Security Maintenance Completed in $(date -ud \"@$TOTAL_TIME\" +'%H:%M:%S')!"
print_status "Logs saved at: $LOG_FILE"
