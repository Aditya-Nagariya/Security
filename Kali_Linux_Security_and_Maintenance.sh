#!/bin/bash
set -Eeuo pipefail

# Kali Security Toolkit - System Security & Maintenance
# Usage: sudo ./kali_security_maintenance.sh

# Force terminal compatibility
export TERM=linux
export LANG=C

# Ensure script is run as root. More robust check.
if [[ $(id -u) -ne 0 ]]; then
   echo "This script must be run as root" 1>&2  # Output to stderr
   exit 1
fi

# Ensure UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Box width - Defining BOX_WIDTH very early
BOX_WIDTH=50

# Colors and Styles - Using named constants for clarity and consistency
RED='\033[0;31m'
LIGHT_RED='\033[1;31m'
GREEN='\033[0;32m'
LIGHT_GREEN='\033[1;32m'
YELLOW='\033[0;33m'
LIGHT_YELLOW='\033[1;33m'
BLUE='\033[0;34m'
LIGHT_BLUE='\033[1;34m'
MAGENTA='\033[0;35m'
LIGHT_MAGENTA='\033[1;35m'
CYAN='\033[0;36m'
LIGHT_CYAN='\033[1;36m'
GRAY='\033[0;37m'
LIGHT_GRAY='\033[0;37m'
DARK_GRAY='\033[1;30m'
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'  # Not used much, but defined for completeness
UNDERLINE='\033[4m' # Not used much, but defined for completeness
BLINK='\033[5m'    # Generally avoided in terminals
REVERSE='\033[7m'   # Use sparingly
HIDDEN='\033[8m'    # Not typically useful in a script
STRIKE='\033[9m'   # Not used much
RESET='\033[0m'

# Progress Bar and UI Elements
PROGRESS_BAR_FILL='█'
PROGRESS_BAR_EMPTY='░'
SPINNER_FRAMES='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
BOX_HORIZONTAL='-'
BOX_VERTICAL='|'
BOX_TOP_LEFT='+'
BOX_TOP_RIGHT='+'
BOX_BOTTOM_LEFT='+'
BOX_BOTTOM_RIGHT='+'
BOX_T_RIGHT='|'    # These aren't actually used in draw_box
BOX_T_LEFT='|'     # but are kept for potential future UI extensions.
BOX_T_DOWN='|'
BOX_T_UP='|'
BOX_CROSS='+'

# Status Symbols
SUCCESS_SYMBOL='[OK]'
ERROR_SYMBOL='[FAIL]'
WARNING_SYMBOL='!'
INFO_SYMBOL='i'
SECURE_SYMBOL='*'  # Not used much
ALERT_SYMBOL='!'    # Redundant with WARNING_SYMBOL
WORKING_SYMBOL='*'

# --- UI Functions ---

# Consistent header with color
show_header() {
    local title="$1"
    local width=80
    printf "\n${CYAN}${BOLD}+%s+${RESET}\n" "$(printf '%*s' "$width" '' | tr ' ' '-')"
    printf "${CYAN}${BOLD}|${RESET} %-${width}s ${CYAN}${BOLD}|${RESET}\n" "  $title"
    printf "${CYAN}${BOLD}+%s+${RESET}\n" "$(printf '%*s' "$width" '' | tr ' ' '-')"
}

# Consistent section headers with color
show_section() {
    local title="$1"
    printf "\n${BLUE}${BOLD}-- %s --${RESET}\n" "$title"
}

# Consistent subsection headers with color
show_subsection() {
    local title="$1"
    printf "\n${MAGENTA}${BOLD}- %s${RESET}\n" "$title"
}


show_result() {
    local status=$1
    local message=$2
    local details=$3

    # Choose color and symbol based on status
    local color="${LIGHT_GREEN}"
    local symbol="${SUCCESS_SYMBOL}"
    case "$status" in
        "warning") color="${LIGHT_YELLOW}"; symbol="${WARNING_SYMBOL}" ;;
        "error")   color="${LIGHT_RED}";    symbol="${ERROR_SYMBOL}"   ;;
        "info")    color="${LIGHT_BLUE}";   symbol="${INFO_SYMBOL}"    ;;
        "secure")  color="${LIGHT_GREEN}";  symbol="${SECURE_SYMBOL}"  ;;
        "alert")   color="${LIGHT_RED}";    symbol="${ALERT_SYMBOL}"   ;; # Redundant
    esac

    printf "${DARK_GRAY}|${RESET} ${symbol} ${color}${BOLD}%s${RESET}" "$message"
    if [[ -n "$details" ]]; then
        printf " ${DIM}%s${RESET}" "$details"
    fi
    printf "\n"
}

# Consistent and clear status message functions
show_warning() {
    local message="$1"
    local details="$2"
    printf "${DARK_GRAY}|${RESET} ${WARNING_SYMBOL} ${LIGHT_YELLOW}${BOLD}Warning:${RESET} %s" "$message"
    if [[ -n "$details" ]]; then  printf " ${DIM}%s${RESET}" "$details"; fi
    printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}" # Use BOX_WIDTH
}

show_error() {
    local message="$1"
    local details="$2"
    printf "${DARK_GRAY}|${RESET} ${ERROR_SYMBOL} ${LIGHT_RED}${BOLD}Error:${RESET} %s" "$message"
    if [[ -n "$details" ]]; then printf " ${DIM}%s${RESET}" "$details"; fi
    printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}"  # Use BOX_WIDTH
}

show_success() {
    local message="$1"
    local details="$2"
    printf "${DARK_GRAY}|${RESET} ${SUCCESS_SYMBOL} ${LIGHT_GREEN}${BOLD}Success:${RESET} %s" "$message"
    if [[ -n "$details" ]]; then printf " ${DIM}%s${RESET}" "$details"; fi
    printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}" # Use BOX_WIDTH
}

show_info() {
    local message="$1"
    local details=${2:-""} # Default to empty string if no details
    printf "${DARK_GRAY}|${RESET} ${INFO_SYMBOL} ${LIGHT_BLUE}${BOLD}Info:${RESET} %s" "$message"
    if [[ -n "$details" ]]; then  printf " ${DIM}%s${RESET}" "$details";  fi
    printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}" # Use BOX_WIDTH
}

show_guidance() {  # Corrected BOX_WIDTH and formatting
    local title="$1"
    local description="$2"
    local recommendation="$3"
    local width=80 # Local width for consistent formatting, even if less than BOX_WIDTH

     # Print header
    printf "\n${DARK_GRAY}|${RESET} ${INFO_SYMBOL} ${LIGHT_BLUE}${BOLD}Security Guidance${RESET}\n"
    printf "${DARK_GRAY}+${BOX_HORIZONTAL}${RESET} ${BOLD}%s${RESET}\n" "$title"

    # Print description section, using consistent width
    printf "${DARK_GRAY}+${BOX_HORIZONTAL}${RESET} ${DIM}Description${RESET}\n"
    local desc_lines
    desc_lines=$(echo "$description" | fold -s -w $((width-4))) # Use local width
    while IFS= read -r line; do
        printf "${DARK_GRAY}|${RESET}   %s\n" "$line"
    done <<< "$desc_lines"

    # Print recommendation section, using consistent width
    printf "${DARK_GRAY}+${BOX_HORIZONTAL}${RESET} ${LIGHT_GREEN}${BOLD}Recommendation${RESET}\n"
    local rec_lines
    rec_lines=$(echo "$recommendation" | fold -s -w $((width-4))) # Use local width
     while IFS= read -r line; do
        printf "${DARK_GRAY}|${RESET}   %s\n" "$line"
    done <<< "$rec_lines"

    # Print footer, using BOX_WIDTH
    printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}"
}

# Hide/show cursor (for spinner and progress bar)
hide_cursor() { printf '\e[?25l'; }
show_cursor() { printf '\e[?25h'; }

# Cleanup on exit (show cursor)
trap 'show_cursor; exit 1' INT TERM

# Draw box - Now consistently using BOX_WIDTH
draw_box() {
    local lines=("$@")
    local max_length=0
    for line in "${lines[@]}"; do
      if [ ${#line} -gt $max_length ]; then
        max_length=${#line}
      fi
    done

    local border="+"
    for ((i=0; i<BOX_WIDTH; i++)); do # Fixed: using BOX_WIDTH
        border+="-"
    done
    border+="+"

    printf "\n%s\n" "$border"
    for line in "${lines[@]}"; do
       printf "| %-${BOX_WIDTH}s |\n" "$line"  # Fixed: using BOX_WIDTH
    done
    printf "%s\n" "$border"
}

# Enhanced spinner animation with status tracking - Corrected logic.
show_spinner() {
    local pid=$1
    local message=$2
    local status=${3:-"working"}  # Default status is "working"
    local delay=0.1
    local frame=0
    local frames_count=${#SPINNER_FRAMES}

    # Choose color and symbol based on status
    local color="${LIGHT_BLUE}"  # Default color
    local prefix="${WORKING_SYMBOL}" # Default symbol

    case "$status" in
        "warning") color="${LIGHT_YELLOW}"; prefix="${WARNING_SYMBOL}" ;;
        "error")   color="${LIGHT_RED}";    prefix="${ERROR_SYMBOL}"   ;;
        "success") color="${LIGHT_GREEN}";  prefix="${SUCCESS_SYMBOL}" ;;
        "info")    color="${LIGHT_BLUE}";   prefix="${INFO_SYMBOL}"    ;;
    esac

    while kill -0 "$pid" 2>/dev/null; do  # Corrected:  Check if the process is running.
        frame=$(( (frame + 1) % frames_count ))
        current_frame=${SPINNER_FRAMES:$frame:1}
        printf "\r${DARK_GRAY}|${RESET} ${prefix} ${color}${current_frame}${RESET} ${DIM}%s${RESET}" "$message"
        sleep "$delay"
    done

    wait "$pid" # Corrected:  Using "$pid" to wait for the specific process.
    local exit_status=$?  # Capture exit status *after* waiting.

    # Show final status *after* the spinner completes.
    if [ "$exit_status" -eq 0 ]; then
        printf "\r${DARK_GRAY}|${RESET} ${SUCCESS_SYMBOL} ${LIGHT_GREEN}${BOLD}Done${RESET} ${DIM}%s${RESET}\n" "$message"
    else
        printf "\r${DARK_GRAY}|${RESET} ${ERROR_SYMBOL} ${LIGHT_RED}${BOLD}Failed${RESET} ${DIM}%s${RESET}\n" "$message"
    fi
     printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}" # Use BOX_WIDTH
    return "$exit_status"
}

# Function to show task status
show_task_status() {
    local message="$1"
    local status="$2"
    local color="$3"
    printf "\r%-50s [%b%s%b]\n" "$message" "$color" "$status" "$RESET"
}

# Execute command with spinner - Now correctly using show_spinner
execute_task() {
    local cmd="$1"
    local message="$2"
    local need_sudo="${3:-false}" # Default to false if not provided

    printf "${CYAN}${BOLD}=== %s ===${RESET}\n" "$message"

    # Execute the command, capture PID *immediately*
    if [[ "$need_sudo" == "true" ]]; then
        sudo "$cmd" > /tmp/cmd.out 2> /tmp/cmd.err & local pid=$!
    else
        "$cmd" > /tmp/cmd.out 2> /tmp/cmd.err & local pid=$!  # Use local pid
    fi

    show_spinner "$pid" "$message"  # Corrected: Use show_spinner, pass PID.
    wait "$pid" # Correct: Wait for the correct process
    local status=$? # Capture status

    # Display output and errors
    if [[ "$status" -eq 0 ]]; then
        show_task_status "$message" "Done" "$GREEN"
        [ -s /tmp/cmd.out ] && printf "Output:\n%s\n" "$(cat /tmp/cmd.out)"
    else
        show_task_status "$message" "Failed" "$RED"
        [ -s /tmp/cmd.err ] && printf "Errors:\n%s\n" "$(cat /tmp/cmd.err)"
    fi
    printf "${CYAN}=================${RESET}\n\n"

    # Cleanup
    rm -f /tmp/cmd.out /tmp/cmd.err
    return "$status"  # Return the status code
}


# Safe command execution with timeout - Corrected and simplified
safe_execute() {
    local cmd="$1"
    local msg="${2:-"Executing"}"      # Default message
    local success_msg="${3:-"Done"}"    # Default success message
    local alt_cmd="${4:-}"           # Optional alternative command
    local timeout_sec="${5:-5}"        # Default timeout of 5 seconds

    local start_time=$(date +%s)
    local pid

    # Try the primary command
   eval "$cmd" > /tmp/cmd.out 2> /tmp/cmd.err &
    pid=$! # Capture PID immediately

   # Loop with a timeout.
    while kill -0 "$pid" 2>/dev/null; do
        sleep 0.1
        local curr_time=$(date +%s)
        if (( curr_time - start_time >= timeout_sec )); then
            printf "\n%s timed out after %d seconds.\n" "$msg" "$timeout_sec" 1>&2  # Error to stderr
            kill -9 "$pid" 2>/dev/null  # Kill the process
            wait "$pid" 2>/dev/null || true #wait and prevent a "wait" error, if already died.
            rm -f /tmp/cmd.out /tmp/cmd.err
            return 124  # Return timeout exit code
        fi
    done

    wait "$pid"
    local exit_code=$?

     # if primary command failed, and we have alternative, try the alternative
    if [[ $exit_code -ne 0 ]] && [[ -n "$alt_cmd" ]]; then
      printf "${YELLOW}Primary command failed, trying alternative...${RESET}\n"
      eval "$alt_cmd" > /tmp/cmd.out 2> /tmp/cmd.err &
      pid=$!

      # Loop for alternative, same timeout
      start_time=$(date +%s) #reset timer
       while kill -0 "$pid" 2>/dev/null; do
        sleep 0.1
        local curr_time=$(date +%s)
        if (( curr_time - start_time >= timeout_sec )); then
            printf "\n%s timed out after %d seconds.\n" "$msg" "$timeout_sec" 1>&2  # Error to stderr
            kill -9 "$pid" 2>/dev/null  # Kill the process
            wait "$pid" 2>/dev/null || true
            rm -f /tmp/cmd.out /tmp/cmd.err
            return 124  # Return timeout exit code
        fi
       done
       wait "$pid"
       exit_code=$? #update exit code
    fi


    if [[ "$exit_code" -eq 0 ]]; then
         printf "\n%s\n" "$success_msg"
    else
         printf "\nError: Command failed with exit code %d\n" "$exit_code" 1>&2 # Output to stderr
         cat /tmp/cmd.err 1>&2 # Output to stderr
    fi
    rm -f /tmp/cmd.out /tmp/cmd.err  # Cleanup
    return "$exit_code"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if a command exists and try alternatives
check_command() {
    local cmd="$1"
    local alternatives="$2"

    if command_exists "$cmd"; then
        echo "$cmd"
        return 0
    fi
    if [[ -n "$alternatives" ]]; then
        for alt in $alternatives; do
            if command_exists "$alt"; then
                echo "$alt"
                return 0
            fi
        done
    fi
    return 1
}

# Install required packages with progress - Added aide
install_dependencies() {
    printf "\n${CYAN}${BOLD}Installing Required Packages...${RESET}\n"
    local packages=(
        "rkhunter" "clamav" "lynis" "chkrootkit" "debsecan" "tiger"
        "bleachbit" "net-tools" "iftop" "nethogs" "bmon" "nmap" "nikto"
        "sslscan" "whatweb" "docker.io" "trivy" "aircrack-ng" "kismet"
        "aide" "aide-common" # Added aide and aide-common
    )

    # Update package list
    execute_task "apt-get update" "Updating package list" true

    # Install each package with progress
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            execute_task "apt-get install -y $package" "Installing $package" true
        else
            show_task_status "$package" "Already installed" "$GREEN"
        fi
    done
}

# Display banner
display_banner() {
    clear
    local title="KALI SECURITY TOOLKIT"
    local subtitle="System Security & Maintenance"

    printf "${CYAN}${BOLD}"
    draw_box "$title" \
        "" \
        "$(printf '%*s' "$(( (BOX_WIDTH-${#subtitle})/2 ))" '')$subtitle" \
        ""
    printf "${RESET}\n"

    # System info
    local sys_info=$(uname -n)
    local kernel_ver=$(uname -r)
    draw_box "SYSTEM INFO" \
        "Host: $sys_info" \
        "Kernel: $kernel_ver"
}

# Show menu
show_menu() {
    printf "\n"
     draw_box "MENU" \
        "" \
        "  1. System Security Scan" \
        "  2. Update System" \
        "  3. Clean System" \
        "  4. Malware Scan" \
        "  5. Security Hardening" \
        "  6. Network Security" \
        "  7. System Backup" \
        "  8. System Monitoring" \
        "  9. Log Analysis" \
        " 10. Secure SSH" \
        " 11. Penetration Testing" \
        " 12. Web Security" \
        " 13. Bandwidth Monitor" \
        " 14. Container Security" \
        " 15. Wireless Security" \
        " 16. Generate Report" \
        "  0. Exit" \
        ""

    printf "\n${YELLOW}Select an option [0-16]:${RESET} "
    read -r choice
    # Trim whitespace and validate input
    choice=$(echo "$choice" | tr -d '[:space:]')
    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [[ "$choice" -gt 16 ]]; then  # Corrected regex and comparison
        printf "${RED}Invalid option! Please enter a number between 0 and 16.${RESET}\n"
        sleep 1
        return  # Return to re-display the menu
    fi
}
# Modified security functions with simpler commands first
perform_rootkit_check() {
    show_header "Rootkit Detection & System Integrity Check"

    # First run RKHunter
    if command_exists "rkhunter"; then
        show_section "RKHunter Analysis"

        # Set log file
        local log_file="/var/log/rkhunter/rkhunter-$(date +%Y%m%d-%H%M%S).log"

        # Create log directory if needed
        if [[ ! -d "/var/log/rkhunter" ]]; then
            show_subsection "Initializing Environment"
             execute_task "mkdir -p /var/log/rkhunter" "Creating log directory" true
        fi

        # Update RKHunter database
        show_subsection "Updating Security Database"
        (rkhunter --update --nocolors --skip-keypress > /dev/null 2>&1) &
        local update_pid=$!
        show_spinner "$update_pid" "Updating RKHunter signatures" "info"  # Corrected
        wait "$update_pid"
        if [[ $? -ne 0 ]]; then
            show_error "Failed to update RKHunter signatures" "Check your internet connection and try again"
            return 1
        fi

        # Update file properties
        show_subsection "Updating System Properties"
        (rkhunter --propupd --nocolors --skip-keypress > /dev/null 2>&1) &
        local propupd_pid=$!
        show_spinner "$propupd_pid" "Creating file property baseline" "info"  # Corrected
        wait "$propupd_pid"
        if [[ $? -ne 0 ]]; then
             show_error "Failed to update file properties" "Check system permissions and try again"
            return 1
        fi

        # Run the check with detailed output
        show_section "System Scan in Progress"
        show_info "This comprehensive scan may take several minutes..."

        # Run RKHunter with progress, capture PID *immediately*
        local temp_log=$(mktemp)
        (sudo rkhunter --check --nocolors --skip-keypress --enable all --disable none --logfile "$log_file" > "$temp_log" 2>&1) &
        local rkhunter_pid=$! # Capture PID immediately.
        show_spinner "$rkhunter_pid" "Scanning system for security threats" # Corrected: Use show_spinner.
        wait "$rkhunter_pid"
        local status=$?

        # Process and display results
        show_section "Scan Results"
        if [[ -f "$log_file" ]]; then
            # Extract key metrics
            local suspect_files=$(grep "Suspect files:" "$log_file" | awk '{print $NF}')
            local possible_rootkits=$(grep "Possible rootkits:" "$log_file" | awk '{print $NF}')
            local apps_checked=$(grep "Applications checked:" "$log_file" | awk '{print $NF}')

            # Show summary metrics
            printf "\n${BOLD}System Check Summary:${RESET}\n"
            show_result "Suspect Files" "$suspect_files" "$([[ "$suspect_files" = "0" ]] && echo "$GREEN" || echo "$YELLOW")"
            show_result "Possible Rootkits" "$possible_rootkits" "$([[ "$possible_rootkits" = "0" ]] && echo "$GREEN" || echo "$RED")"
            show_result "Applications Checked" "$apps_checked" "$CYAN"

            # Show warnings if any
            if grep -q "Warning:" "$log_file"; then
                show_section "Security Warnings"
                printf "${YELLOW}${BOLD}The following security issues were detected:${RESET}\n"
                # Use a more robust way to extract warnings:
                grep -A 2 "Warning:" "$log_file" | while IFS= read -r line; do
                    if [[ $line == *"Warning:"* ]]; then
                        printf "\n${YELLOW}! %s${RESET}\n" "${line#*Warning: }"
                    elif [[ -n "$line" && "$line" != "--" ]]; then
                        printf "  ${DIM}%s${RESET}\n" "$line"
                    fi
                done

                # Show guidance
                show_guidance "Required Actions" "warning" \
                    "Run 'rkhunter --list' to see detailed file listings" \
                    "Check 'rkhunter --config-check' for configuration issues" \
                    "Verify system binaries with 'debsums -c'" \
                    "Monitor '/var/log/rkhunter.log' for changes"
            else
                show_guidance "System Status" "success" \
                    "Schedule regular scans with cron" \
                    "Keep RKHunter updated weekly" \
                    "Monitor logs for changes"
            fi
        else
            show_error "Failed to create log file"
            show_guidance "Error Recovery" "error" \
                "Check permissions on /var/log/rkhunter" \
                "Verify RKHunter installation" \
                "Run 'rkhunter --config-check'"
        fi

        # Cleanup
        rm -f "$temp_log"
    else
        show_warning "RKHunter not found. Installing..."
        if execute_task "apt-get install -y rkhunter" "Installing RKHunter" true; then
            execute_task "rkhunter --propupd" "Initial Setup" true
            perform_rootkit_check # Recursive call after successful install
            return
        fi
    fi

    # Run ChkRootkit
    show_section "ChkRootkit Analysis"
    if command_exists "chkrootkit"; then
        show_info "Starting secondary rootkit scan..."

        # Run ChkRootkit with progress, capture PID *immediately*
        local chkrootkit_log=$(mktemp)
        (sudo chkrootkit > "$chkrootkit_log" 2>&1) &
        local chkrootkit_pid=$!  # Capture PID immediately!
        show_spinner "$chkrootkit_pid" "Performing deep system scan" # Correct: Use show_spinner.
        wait "$chkrootkit_pid"  # Corrected: wait for the correct PID.
        local status=$?

        # Process results
        if [[ -f "$chkrootkit_log" ]]; then
            show_section "ChkRootkit Findings"

            # Process and categorize output
            local warnings=$(grep -i "INFECTED\|SUSPICIOUS\|WARNING" "$chkrootkit_log") # Corrected regex
            if [[ -n "$warnings" ]]; then
                show_warning "Suspicious Activity Detected"
                printf "${YELLOW}${BOLD}Potential Security Issues:${RESET}\n"
                echo "$warnings" | while IFS= read -r line; do  # Corrected
                    printf "  ${YELLOW}• %s${RESET}\n" "$line"
                done

                show_guidance "Required Actions" "warning" \
                    "Review all suspicious processes" \
                    "Verify system binary integrity" \
                    "Check network connections" \
                    "Consider additional security tools"
            else
                show_success "No rootkits or suspicious activity detected"
                show_guidance "Recommended Actions" "success" \
                    "Schedule regular security audits" \
                    "Keep system updated" \
                    "Monitor system logs"
            fi
        fi
        rm -f "$chkrootkit_log"
    else
        show_warning "ChkRootkit not found. Installing..."
        if execute_task "apt-get install -y chkrootkit" "Installing ChkRootkit" true; then
             execute_task "chkrootkit" "Initial Scan" true # Run an initial scan after install
        fi
    fi

    show_header "Security Scan Complete"
    if [[ -f "$log_file" ]] && grep -q "Warning:" "$log_file"; then
        show_warning "Security issues were found. Review the guidance above."
        show_info "Note: Some warnings are normal in Kali Linux due to security tools."
    else
        show_success "System appears clean. Maintain regular security checks."
    fi
}
update_system() {
    printf "\n${CYAN}${BOLD}Updating System...${RESET}\n"
    execute_task "apt-get update" "Updating Package Lists" true
    execute_task "apt-get upgrade -y" "Upgrading Packages" true
    execute_task "apt-get autoremove -y" "Cleaning Old Packages" true
}

clean_system() {
    printf "\n${CYAN}${BOLD}Cleaning System...${RESET}\n"
    execute_task "apt-get clean" "Cleaning Package Cache" true
    execute_task "apt-get autoclean" "Cleaning Old Package Versions" true
     # Display log sizes
    execute_task "du -sh /var/log" "Log Directory Size" false
    execute_task "journalctl --disk-usage" "Journal Size" false
}

malware_scan() {
     printf "\n${CYAN}${BOLD}Scanning for Malware...${RESET}\n"
    # Verify ClamAV installation.  Use command_exists for robustness.
    if ! command_exists "clamscan"; then
        show_warning "ClamAV not found" "Installing..."
        execute_task "apt-get install -y clamav clamav-daemon clamav-freshclam" "Installing ClamAV" true || {
            show_error "Failed to install ClamAV" "Check package manager and try again"
            return 1
        }
    fi
     # Check ClamAV version
    execute_task "clamscan --version" "ClamAV Version" false

    # Create necessary directories with proper permissions
    local clamav_dirs=(
        "/var/log/clamav"
        "/var/lib/clamav"
        "/run/clamav"
        "/var/lib/clamav/quarantine"  # Added quarantine directory
    )

    for dir in "${clamav_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
             execute_task "mkdir -p $dir" "Creating $dir" true || {
                show_error "Failed to create directory $dir" "Check permissions and try again"
                return 1
            }
        fi
        execute_task "chown -R clamav:clamav $dir" "Setting ownership for $dir" true
        execute_task "chmod -R 750 $dir" "Setting permissions for $dir" true # More secure permissions
    done

    # Stop services before update, check if services exist
    local services=("clamav-freshclam" "clamav-daemon")
    for service in "${services[@]}"; do
      if command_exists systemctl && systemctl is-active --quiet "$service" ; then
            execute_task "systemctl stop $service" "Stopping $service" true || {
                show_warning "Failed to stop $service" "Service may be in use"
            }
      fi
    done

    # Update virus definitions with proper error handling and timeout
    show_info "Updating virus definitions (this may take a while)..."
    local freshclam_log="/var/log/clamav/freshclam.log"
     touch "$freshclam_log" && chown clamav:clamav "$freshclam_log"

    (timeout 300 freshclam --verbose --stdout) 2>&1 | \
    while IFS= read -r line; do
      if [[ "$line" == *"ERROR"* ]]; then
        show_error "Update Error" "$line"
      elif [[ "$line" == *"WARNING"* ]]; then
        show_warning "Update Warning" "$line"
      elif [[ "$line" == *"Database updated"* ]]; then
        show_success "Database Update" "$line"
      fi
    done

     # Start scanning with proper error handling and progress monitoring
    show_info "Starting malware scan..."
    local scan_log="/var/log/clamav/scan.log"
    local quarantine_dir="/var/lib/clamav/quarantine"

     # Clear previous scan log
    echo "" > "$scan_log"

 # Start scan with detailed options, and more specific exclusions
    (timeout 1800 clamscan \
        --recursive \
        --log="$scan_log" \
        --move="$quarantine_dir" \
        --cross-fs=no \
        --detect-pua \
        --scan-archive \
        --max-filesize=100M \
        --max-scansize=400M \
        --exclude-dir="^/sys" \
        --exclude-dir="^/proc" \
        --exclude-dir="^/dev" \
        --exclude-dir="^/run" \
        --exclude-dir="^/tmp" \
        --exclude-dir="^/var/tmp" \
        --exclude-dir="^/var/run" \
        --exclude-dir="^/var/lock" \
        --exclude-dir="^/home/[^/]*/\.gvfs" \
        --exclude-dir="^/home/[^/]*/\.cache" \
        --exclude-dir="^/run/user/[0-9]*/gvfs" \
        --exclude-dir="^/run/user/[0-9]*/doc" \
                --exclude-dir="^/var/lib/docker" \
        --stdout \
        /home) 2>&1 | \
        while IFS= read -r line; do
            if [[ "$line" == *"FOUND"* ]]; then
                show_warning "Threat Found" "$line"
            elif [[ "$line" == *"ERROR"* ]]; then
                show_error "Scan Error" "$line"
            elif [[ "$line" == *"Scanning"* ]]; then
                show_info "Progress" "$line" # Show some progress
            fi
        done

     scan_status=${PIPESTATUS[0]}

    # Process scan results with detailed reporting
    if [[ -f "$scan_log" ]]; then
        local infected=$(grep -c "FOUND" "$scan_log")
        local errors=$(grep -c "ERROR" "$scan_log")
        local scanned=$(grep -c "Scanned files:" "$scan_log")

        case $scan_status in
            0)
                show_success "Scan completed successfully" "No threats detected"
                show_guidance "Scan Summary" "success" \
                    "Files scanned: $scanned" \
                    "Clean system detected" \
                    "Schedule regular scans"
                ;;
            1)
                show_warning "Threats detected!" "$infected malicious files found"
                 show_guidance "Malware Found" "warning" \
                    "Quarantined files: $quarantine_dir" \
                    "Scan log: $scan_log" \
                    "Review quarantined files" \
                    "Consider full system scan"
                ;;
            124)
                show_error "Scan timed out" "Scan exceeded 30-minute limit"
                 show_guidance "Timeout Recovery" "error" \
                    "Reduce scan scope" \
                    "Check system resources" \
                    "Try scanning specific directories"
                ;;
            *)
                show_error "Scan failed" "Exit code: $scan_status"
                show_guidance "Scan Failure" "error" \
                    "Check scan log: $scan_log" \
                    "Verify ClamAV installation" \
                    "Check system resources"
                ;;
        esac

        # Report scan statistics
        if [[ $errors -gt 0 ]]; then
            show_warning "Scan encountered errors" "$errors errors found"
        fi
    else
      show_error "Scan log not found" "The scan may have failed to complete"
    fi

    # Restart services
    for service in "${services[@]}"; do
      if command_exists systemctl && systemctl is-active --quiet "$service" ; then
            execute_task "systemctl start $service" "Starting $service" true || {
               show_error "Failed to start $service" "Check service status"
            }
      fi
    done
}
security_hardening() {
    printf "\n${CYAN}${BOLD}Hardening System...${RESET}\n"
    execute_task "ufw status" "Firewall Status" true
    execute_task "ufw --force enable" "Enabling Firewall" true
    execute_task "ls -la /home" "Home Directory Permissions" false
    execute_task "cat /etc/passwd" "User Accounts" false

    # Install auditd
     execute_task "apt-get install -y auditd" "Installing audit framework" true

    # Configure AIDE monitoring - Corrected to avoid duplicate rules
    local audit_rules="/etc/audit/rules.d/aide.rules"

     # Check if rules already exist before adding
    if ! grep -q  --fixed-strings  "-w /etc/aide/aide.conf -p wa -k aide_config" "$audit_rules"; then
        echo "-w /etc/aide/aide.conf -p wa -k aide_config" | tee -a "$audit_rules"
    fi

    if ! grep -q --fixed-strings  "-w /var/lib/aide/ -p wa -k aide_db" "$audit_rules"; then
         echo "-w /var/lib/aide/ -p wa -k aide_db" | tee -a "$audit_rules"
    fi

    # Apply configuration.  Restart and then reload rules.
    systemctl restart auditd && auditctl -R "$audit_rules"
}

network_security() {
    printf "\n${CYAN}${BOLD}Network Security...${RESET}\n"
    execute_task "ip addr" "Network Interfaces" false
    execute_task "netstat -tuln" "Open Ports" false
    execute_task "ss -tuln" "Socket Statistics" false
    execute_task "iptables -L" "Firewall Rules" true
}

monitor_system() {
    printf "\n${CYAN}${BOLD}System Monitoring...${RESET}\n"
    execute_task "uptime" "System Uptime" false
    execute_task "free -h" "Memory Usage" false
    execute_task "df -h" "Disk Usage" false
    execute_task "who" "Active Users" false
    execute_task "top -b -n 1" "Process List" false # Show top processes
}

analyze_logs() {
    printf "\n${CYAN}${BOLD}Analyzing System Logs...${RESET}\n"
    show_progress 2 "Preparing log analysis"

    # Check common log files
    for logfile in /var/log/syslog /var/log/messages /var/log/auth.log; do
        if [[ -f "$logfile" ]]; then
            execute_task "tail -n 20 $logfile" "Recent logs from $logfile" true
        fi
    done

    # Show recent logins without -n flag
    safe_execute "who" "Active Users" "Done" 5  # Added success_msg and timeout
    safe_execute "last | head" "Recent Logins" "Done" 5 # Added success_msg and timeout

    # Use journalctl if available, otherwise dmesg without -n
    if command_exists "journalctl"; then
        safe_execute "journalctl -n 20" "Recent System Logs" "Done" 5 # Added success_msg and timeout
    else
        safe_execute "dmesg | head" "Kernel Messages" "Done" 5 # Added success_msg and timeout
    fi
}
pentest_tools() {
    printf "\n${CYAN}${BOLD}Basic Security Checks...${RESET}\n"
    safe_execute "nmap -F localhost" "Quick Port Scan" "Nmap Scan Complete" 5  # Added success_msg and timeout
    safe_execute "netstat -tuln" "Open Ports" "Netstat Complete" 5 # Added success_msg and timeout

    # Fix listening process check
    printf "\n${CYAN}Checking for listening processes...${RESET}\n"
    if command_exists "lsof"; then
       safe_execute "lsof -i -P -n | grep LISTEN" "Listening Processes (lsof)" "Lsof Complete" 5 # Added success_msg and timeout
    elif command_exists "netstat"; then
       safe_execute "netstat -tlnp" "Listening Processes (netstat)" "Netstat Complete" 5 # Added success_msg and timeout
    elif command_exists "ss"; then
        safe_execute "ss -tlnp" "Listening Processes (ss)" "SS Complete" 5  # Added success_msg and timeout
    else
        printf "${YELLOW}No suitable command found to check listening processes${RESET}\n"
    fi
}

check_web_security() {
    printf "\n${CYAN}${BOLD}Web Security Check...${RESET}\n"
    show_progress 1 "Initializing security checks"

    # Test localhost connectivity first
    if ping -c 1 -W 1 localhost >/dev/null 2>&1; then
        show_task_status "Local connectivity" "OK" "$GREEN"

        # Try different ports for HTTP
        for port in 80 443 8080; do
            printf "${CYAN}Testing port $port...${RESET}\n"
            show_progress 1 "Checking port $port"

            if command_exists "nc"; then
                if nc -z localhost "$port" 2>/dev/null; then
                    show_task_status "Port $port" "Open" "$GREEN"
                    safe_execute "curl -Is --connect-timeout 2 http://localhost:$port" "HTTP Headers (Port $port)" "Headers Retrieved" 5
                else
                    show_task_status "Port $port" "Closed" "$YELLOW"
                fi
            else
               safe_execute "curl -Is --connect-timeout 2 http://localhost:$port" "HTTP Headers (Port $port)" "Headers Retrieved" 5
            fi
        done
    else
        show_task_status "Local web server" "Not Running" "$YELLOW"
    fi
}

monitor_bandwidth() {
    printf "\n${CYAN}${BOLD}Network Statistics...${RESET}\n"
    show_progress 1 "Gathering network information"

    safe_execute "ip -s link" "Interface Statistics (ip)" "IP Stats Complete" 5
    safe_execute "netstat -i" "Network Interfaces (netstat)" "Netstat Complete" 5

    # Test internet connectivity with better feedback
    printf "\n${CYAN}Testing Internet Connectivity...${RESET}\n"
    show_progress 1 "Initializing connectivity test"

    local dns_servers=("8.8.8.8" "1.1.1.1" "208.67.222.222")
    local success=false

    for dns in "${dns_servers[@]}"; do
        printf "Testing connection to $dns...\n"
        show_progress 1 "Checking $dns"
        if ping -c 1 -W 2 "$dns" >/dev/null 2>&1; then
            show_task_status "Connection to $dns" "Success" "$GREEN"
            success=true
            break  # Exit loop on first success
        else
            show_task_status "Connection to $dns" "Failed" "$YELLOW"
        fi
    done

    if ! $success; then
        show_task_status "Internet Connectivity" "No Connection" "$RED"
    fi
}

check_containers() {
     printf "\n${CYAN}${BOLD}Container Check...${RESET}\n"
    if command_exists "docker"; then # Changed to directly check for 'docker'
        safe_execute "docker --version" "Docker Version" "Version Displayed" 5 # Added success_msg and timeout
        safe_execute "docker ps" "Running Containers" "Containers Listed" 5 # Added success_msg and timeout
        safe_execute "docker images" "Available Images" "Images Listed" 5 # Added success_msg and timeout
    elif command_exists "podman"; then # Added check for podman as fallback
        safe_execute "podman --version" "Podman Version" "Version Displayed" 5 # Added success_msg and timeout
        safe_execute "podman ps" "Running Containers" "Containers Listed" 5 # Added success_msg and timeout
        safe_execute "podman images" "Available Images" "Images Listed" 5 # Added success_msg and timeout
    else
        printf "${YELLOW}No container runtime found (tried: docker, podman)${RESET}\n"
    fi
}

wireless_security() {
     printf "\n${CYAN}${BOLD}Wireless Information...${RESET}\n"

    # Check for wireless interfaces with better detection
    local has_wireless=false

    if command_exists "iwconfig"; then
        # Filter only wireless interfaces
        local wireless_info=$(iwconfig 2>&1 | grep -v "no wireless extensions")
        if [[ -n "$wireless_info" ]]; then
            printf "${GREEN}Found wireless interfaces:${RESET}\n"
            echo "$wireless_info"
            has_wireless=true
        fi
    elif command_exists "iw"; then
        if iw dev | grep -q "Interface"; then
            safe_execute "iw dev" "Wireless Interfaces (iw)" "Interfaces Listed" 5
             has_wireless=true
        fi
    fi

    if ! $has_wireless; then
        printf "${YELLOW}No wireless interfaces detected${RESET}\n"
    else
        # Only run these if we found wireless interfaces
        if command_exists "nmcli"; then
            safe_execute "nmcli dev wifi list" "Available Networks (nmcli)" "Networks Listed" 5
        fi
        safe_execute "rfkill list wifi" "Wireless Status (rfkill)" "Status Displayed" 5
    fi

    # Show all network interfaces for reference
    printf "\n${CYAN}All Network Interfaces:${RESET}\n"
    if command_exists "ip"; then # Prioritize 'ip' command
        safe_execute "ip link show" "Network Interfaces (ip)" "Interfaces Displayed" 5
    elif command_exists "ifconfig"; then # Fallback to 'ifconfig' if 'ip' is not found
        safe_execute "ifconfig" "Network Interfaces (ifconfig)" "Interfaces Displayed" 5
    else
         printf "${YELLOW}No command found to list network interfaces (tried: ip, ifconfig)${RESET}\n"
    fi
}

backup_system() {
    printf "\n${CYAN}${BOLD}System Backup Info...${RESET}\n"
    local backup_dir="/var/backups"
    if [[ -d "$backup_dir" ]]; then
        execute_task "ls -la $backup_dir" "Existing Backups" true
        execute_task "df -h $backup_dir" "Backup Space" false
    else
        printf "${YELLOW}Backup directory $backup_dir does not exist${RESET}\n"
         execute_task "mkdir -p $backup_dir" "Creating Backup Directory" true
    fi
}

generate_report() {
    printf "\n${CYAN}${BOLD}Generating Security Report...${RESET}\n"
    local report_dir="/var/log/security_report"
    local date_str=$(date +%Y%m%d_%H%M%S)
    local report_file="$report_dir/security_report_$date_str.txt"

    # Ensure directory exists
    if [[ ! -d "$report_dir" ]]; then
        execute_task "mkdir -p $report_dir" "Creating Report Directory" true
    fi

    # Generate report with error handling
    {
        echo "=== Security Report ==="
        echo "Generated on: $(date)"
        echo ""

        echo "=== System Information ==="
        if command_exists "uname"; then
            uname -a
        else
            echo "System information not available"
        fi
        echo ""

        echo "=== Disk Usage ==="
        if command_exists "df"; then
            df -h
        else
            echo "Disk usage information not available"
        fi
        echo ""

        echo "=== Memory Usage ==="
        if command_exists "free"; then
            free -h
        else
            echo "Memory usage information not available"
        fi
        echo ""

        echo "=== Network Interfaces ==="
        if command_exists "ip"; then
            ip addr
        elif command_exists "ifconfig"; then
            ifconfig
        else
            echo "Network interface information not available"
        fi
        echo ""

        echo "=== Listening Ports ==="
       if command_exists "netstat"; then
            netstat -tuln
        elif command_exists "ss"; then
            ss -tuln
        else
            echo "Port information not available"
        fi
        echo ""

        echo "=== System Updates ==="
        if command_exists "apt-get"; then
            apt-get -s upgrade  # Simulate an upgrade
        else
            echo "System update information not available"
        fi
        echo ""

    } > "$report_file" 2>/dev/null  # Redirect errors to /dev/null

    if [[ -f "$report_file" ]]; then
        printf "${GREEN}Report generated: $report_file${RESET}\n"
        execute_task "cat $report_file" "Report Contents" false
    else
        printf "${RED}Failed to generate report${RESET}\n"
    fi
}

secure_ssh() {
    printf "\n${CYAN}${BOLD}Securing SSH...${RESET}\n"

    # Check if SSH server is installed
    if ! command_exists "sshd"; then
        show_warning "OpenSSH Server not found" "Installing..."
        execute_task "apt-get install -y openssh-server" "Installing OpenSSH Server" true || {
            show_error "Failed to install OpenSSH Server" "Check package manager and try again"
            return 1
        }
    fi

    # Create backup directory
    local backup_dir="/etc/ssh/backup"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/sshd_config.$timestamp"

    execute_task "mkdir -p $backup_dir" "Creating backup directory" true || {
      show_error "Failed to create backup directory" "Check permissions and try again"
      return 1
    }

    # Backup current configuration
    if [[ -f "/etc/ssh/sshd_config" ]]; then
        execute_task "cp /etc/ssh/sshd_config $backup_file" "Backing up SSH config" true || {
            show_error "Failed to backup SSH config" "Check file permissions"
            return 1
        }
        show_success "Configuration backed up" "Location: $backup_file"
    fi
     # Display current configuration
    execute_task "cat /etc/ssh/sshd_config" "Current SSH Config" false

    # Apply security hardening
    local config_file="/etc/ssh/sshd_config"
    local temp_config="$(mktemp)"

    # Create secure configuration
    cat > "$temp_config" << EOL
# Secure SSH Configuration (Generated $(date))
Port 22
Protocol 2
PermitRootLogin no
MaxAuthTries 3
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
UsePAM yes
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitUserEnvironment no
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 30
StrictModes yes
IgnoreRhosts yes
HostbasedAuthentication no
LogLevel VERBOSE
EOL

      # Apply new configuration
    execute_task "mv $temp_config $config_file" "Applying secure configuration" true || {
      show_error "Failed to apply new configuration" "Check file permissions"
      return 1;
    }

    # Set correct permissions
     execute_task "chmod 600 $config_file" "Setting secure permissions" true

     # Verify configuration syntax
     execute_task "sshd -t" "Verifying configuration" true || {
        show_error "Invalid SSH configuration" "Restoring backup..."
        execute_task "cp $backup_file $config_file" "Restoring previous config" true
         return 1
    }
     # Restart SSH service with proper error handling
    local ssh_service="ssh"
    if command_exists "systemctl"; then
       if systemctl is-active --quiet "$ssh_service"; then
            execute_task "systemctl restart $ssh_service" "Restarting SSH service" true || {
                show_error "Failed to restart SSH service" "Check service status"
                return 1
            }
        else
            execute_task "systemctl start $ssh_service" "Starting SSH service" true  || {
                show_error "Failed to start SSH service" "Check service status"
                return 1
            }
        fi
       # Verify service status
        if systemctl is-active --quiet "$ssh_service"; then
            show_success "SSH hardening complete" "Service is running with secure configuration"
            show_guidance "SSH Security" "success" \
                "Use key-based authentication" \
                "Regularly monitor auth.log" \
                "Keep system updated" \
                "Backup location: $backup_file"

        else
            show_error "SSH service failed to start" "Check system logs for details"
            return 1
         fi

    else
        show_error "System service manager not found" "Cannot manage SSH service"
        return 1
    fi
}

# Function to handle tool installation
install_security_tool() {
    local tool="$1"
    local package="$2"

    if ! command_exists "$tool"; then
        printf "${YELLOW}Installing $tool...${RESET}\n"
        if execute_task "apt-get install -y $package" "Installing $tool" true; then
            show_task_status "$tool Installation" "Success" "$GREEN"
            return 0  # Return 0 on success
        else
            show_task_status "$tool Installation" "Failed" "$RED"
            return 1  # Return 1 on failure
        fi
    fi
    return 0 # Tool already exists
}
# Function to provide actionable guidance
show_security_guidance() {
    local tool="$1"
    local status="$2"
    local details="$3"

    printf "\n${CYAN}=== Guidance for $tool Results ===${RESET}\n"
    case "$tool" in
        "RKHunter")
            if [[ "$status" = "clean" ]]; then
                printf "${GREEN}[OK] System appears clean of rootkits${RESET}\n"
                printf "Recommended actions:\n"
                printf "1. Schedule regular scans: Add to crontab\n"
                printf "2. Keep RKHunter updated: Run 'rkhunter --update' weekly\n"
                printf "3. Monitor /var/log/rkhunter.log for changes\n"
            else
                printf "${YELLOW}[FAIL] Potential issues detected${RESET}\n"
                printf "Required actions:\n"
                printf "1. Investigate suspicious files: rkhunter --list\n"
                printf "2. Check false positives: rkhunter --config-check\n"
                printf "3. Update properties if safe: rkhunter --propupd\n"
                printf "4. For each warning:\n"
                printf "   - Verify file integrity: sha256sum <file>\n"
                printf "   - Check process origins: ps aux | grep <suspicious-process>\n"
                printf "   - Review recent changes: find / -mtime -7 -type f\n"
            fi
            ;;
        "ChkRootkit")
            if [[ "$status" = "clean" ]]; then
                printf "${GREEN}[OK] No rootkits detected${RESET}\n"
                printf "Recommended actions:\n"
                printf "1. Schedule regular scans\n"
                printf "2. Keep system updated: apt update && apt upgrade\n"
                printf "3. Monitor system logs regularly\n"
            else
                printf "${YELLOW}[FAIL] Suspicious activity detected${RESET}\n"
                printf "Required actions:\n"
                printf "1. Check running processes: ps aux\n"
                printf "2. Verify system binaries: debsums -c\n"
                printf "3. Scan with additional tools: tiger, aide\n"
                printf "4. Check network connections: netstat -tupln\n"
            fi
            ;;
          "AIDE")
            if [ "$status" = "clean" ]; then
                printf "${GREEN}[OK] File integrity check passed${RESET}\n"
                printf "Recommended actions:\n"
                printf "1. Backup the AIDE database\n"
                printf "2. Schedule weekly integrity checks\n"
            else
                printf "${RED}[FAIL] File integrity violations detected${RESET}\n"
                printf "Required actions:\n"
                printf "1. Review changed files: aide --check\n"
                printf "2. Verify changes are authorized\n"
                printf "3. Update database if changes are valid: aide --update\n"
            fi
            ;;
        "Tiger")
            if [ "$status" = "clean" ]; then
                printf "${GREEN}[OK] Security audit passed${RESET}\n"
                printf "Recommended actions:\n"
                printf "1. Review full report in /var/log/tiger/\n"
                printf "2. Schedule periodic audits\n"
            else
                printf "${YELLOW}[FAIL] Security issues found${RESET}\n"
                printf "Required actions:\n"
                printf "1. Review tiger report: less /var/log/tiger/security.report.*\n"
                printf "2. Fix identified vulnerabilities\n"
                printf "3. Document any accepted risks\n"
            fi
            ;;
        "Lynis")
            if [ "$status" = "clean" ]; then
                printf "${GREEN}[OK] System hardening check passed${RESET}\n"
                printf "Recommended actions:\n"
                printf "1. Review full report: /var/log/lynis.log\n"
                printf "2. Implement suggested improvements\n"
                printf "3. Schedule regular audits\n"
            else
                printf "${YELLOW}[FAIL] Hardening improvements needed${RESET}\n"
                printf "Required actions:\n"
                printf "1. Review warnings: less /var/log/lynis.log\n"
                printf "2. Check hardening index score\n"
                printf "3. Implement critical suggestions first\n"
                printf "4. Document exceptions\n"
            fi
            ;;
    esac

    if [[ -n "$details" ]]; then
        printf "\n${CYAN}Additional Details:${RESET}\n"
        echo "$details"
    fi
}

perform_security_scan() {
    show_header "Comprehensive System Security Audit"

    # Install required tools.  AIDE is now handled below.
    show_section "Security Tool Verification"
    local tools=(
        "rkhunter:rkhunter"
        "chkrootkit:chkrootkit"
        "tiger:tiger"
        "lynis:lynis"
        "aide:aide-common" # Corrected package name for aide
    )

    for tool in "${tools[@]}"; do
        IFS=':' read -r name package <<< "$tool"
        if ! command_exists "$name"; then
            show_warning "$name not found" "Installing..."
            if install_security_tool "$name" "$package"; then
                show_success "$name installed successfully"
            else
                show_error "Failed to install $name" "Check package manager and try again"
            fi
        else
            show_success "$name is available" "Ready for security scan"
        fi
         printf "\n${DARK_GRAY}+%${BOX_WIDTH}s+${RESET}\n" "" | tr ' ' "${PROGRESS_BAR_EMPTY}" # Use BOX_WIDTH

    done

    # Initialize AIDE if needed - Corrected and simplified
    show_section "File Integrity Setup"
    if command_exists "aide"; then
        if [[ ! -f "/var/lib/aide/aide.db.gz" ]]; then  # Corrected check for compressed DB
            show_info "Initializing AIDE..."
            execute_task "aide --init" "Initializing AIDE Database" true
            # Move the new database into place.
            execute_task "mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz" "Activating AIDE Database" true

            show_success "AIDE initialized successfully" "Database and configuration are ready"
        else
            show_success "AIDE database exists" "Using existing database"
        fi
    else
        # AIDE should have been installed above, but this is a safety check.
        show_error "AIDE not found after installation attempt!" "Critical error"
        return 1
    fi

    # Run RKHunter check with timeout
    show_section "Rootkit Detection"
    local scan_log=$(mktemp)

    # Run rootkit check with 5 minute timeout, capture PID *immediately*.
    timeout 300 perform_rootkit_check > "$scan_log" 2>&1 &
    local scan_pid=$!  # Capture the PID *immediately*.

    show_spinner "$scan_pid" "Performing rootkit detection" # Corrected: Use show_spinner
    wait "$scan_pid"

    if [[ $? -eq 124 ]]; then
        show_error "Rootkit scan timed out" "Process took too long and was terminated"
        cat "$scan_log" >> "/var/log/security_scan_errors.log" # Log the output
        rm -f "$scan_log"
        return 1
    elif [[ $? -ne 0 ]]; then  # General error check after wait
        local error_msg=$(tail -n 5 "$scan_log")
        show_error "Rootkit scan failed" "$error_msg"
         cat "$scan_log" >> "/var/log/security_scan_errors.log" # Log the output
        rm -f "$scan_log"
        return 1
    fi
    rm -f "$scan_log" # Cleanup the temporary log


    # Run AIDE check
    show_section "File Integrity Verification"
    if command_exists "aide"; then
        show_info "Checking file integrity..."
        local aide_log=$(mktemp)

        # Run AIDE check with progress and timeout, capture PID *immediately*
        timeout 300 aide --check > "$aide_log" 2>&1 &
        local aide_pid=$! # Capture PID *immediately*
        show_spinner "$aide_pid" "Verifying system files"  # Corrected: Use show_spinner.
        wait "$aide_pid"

        if [[ $? -eq 124 ]]; then
            show_error "AIDE check timed out" "Process took too long and was terminated"
            return 1  # Exit on timeout
        elif [[ $? -ne 0 ]]; then
             show_error "AIDE check failed" "Check /var/log/aide/aide.log"
              return 1 #exit on failure
        fi

        if [[ -f "$aide_log" ]]; then
            local changes=$(grep -c "changed" "$aide_log")
            local added=$(grep -c "added" "$aide_log")
            local removed=$(grep -c "removed" "$aide_log")

            show_section "File Changes Detected"
            show_result "Modified Files" "$changes" "$([[ "$changes" = "0" ]] && echo "$GREEN" || echo "$YELLOW")"
            show_result "Added Files" "$added" "$([[ "$added" = "0" ]] && echo "$GREEN" || echo "$YELLOW")"
            show_result "Removed Files" "$removed" "$([[ "$removed" = "0" ]] && echo "$GREEN" || echo "$RED")"

            if [[ "$changes" != "0" ]] || [[ "$added" != "0" ]] || [[ "$removed" != "0" ]]; then
                show_guidance "File Integrity Issues" "warning" \
                    "Review changes: aide --check" \
                    "Verify authorized changes" \
                    "Update database if needed (and changes are legitimate): aide --update; mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz" \
                    "Check for suspicious modifications"
            else
                show_guidance "File Integrity Status" "success" \
                    "System files are unmodified" \
                    "Continue regular monitoring" \
                    "Schedule periodic checks"
            fi
        fi
        rm -f "$aide_log" # Clean up the temporary log
    fi
    # Run Tiger audit with timeout and error handling
    show_section "System Security Audit"
    if command_exists "tiger"; then
        local audit_log=$(mktemp)

        # Run Tiger with 5 minute timeout, capture PID immediately.
        timeout 300 tiger > "$audit_log" 2>&1 &
        local tiger_pid=$! # Capture the PID *immediately*.
         show_spinner "$tiger_pid" "Performing system security audit" # Correct use of show_spinner
        wait "$tiger_pid"

        if [[ $? -eq 124 ]]; then
             show_error "Security audit timed out" "Process took too long and was terminated"
              cat "$audit_log" >> "/var/log/security_scan_errors.log" # Log the output
             rm -f "$audit_log"
             return 1
        elif [[ $? -ne 0 ]] ; then  # General error check
            local error_msg=$(tail -n 5 "$audit_log")
            show_error "Security audit failed" "$error_msg"
            cat "$audit_log" >> "/var/log/security_scan_errors.log"
            rm -f "$audit_log"
            return 1
        fi

        show_info "Running Tiger security audit..."
        local tiger_log=$(mktemp)

      # Run Tiger with progress, capture PID immediately.
        timeout 300 tiger > "$tiger_log" 2>&1 &
        local tiger_pid=$!  # Capture PID *immediately*.
        show_spinner "$tiger_pid" "Performing security audit" # Corrected: Use show_spinner
        wait "$tiger_pid"

        if [[ $? -eq 124 ]]; then
            show_error "Tiger audit timed out" "Process took too long and was terminated"
            return 1  # Exit on timeout
        elif [[ $? -ne 0 ]] ; then
            show_error "Tiger Audit failed" "Check Logs"
            return 1
        fi

        if [[ -f "$tiger_log" ]]; then
            show_section "Security Audit Findings"
            local warnings=$(grep -c "Security Warning" "$tiger_log")
            local notices=$(grep -c "Security Notice" "$tiger_log")

            show_result "Security Warnings" "$warnings" "$([[ "$warnings" = "0" ]] && echo "$GREEN" || echo "$RED")"
            show_result "Security Notices" "$notices" "$([[ "$notices" = "0" ]] && echo "$GREEN" || echo "$YELLOW")"

            if [[ "$warnings" != "0" ]] || [[ "$notices" != "0" ]]; then
                show_guidance "Security Issues" "warning" \
                    "Check /var/log/tiger for full report" \
                    "Review all security warnings" \
                    "Address critical issues first" \
                    "Document any accepted risks"

                # Show critical findings
                if [[ "$warnings" != "0" ]]; then
                    printf "\n${RED}Critical Security Warnings:${RESET}\n"
                    grep "Security Warning" "$tiger_log" | while IFS= read -r line; do
                        printf "  ${RED}• %s${RESET}\n" "$line"
                    done
                fi
            else
                show_guidance "Security Status" "success" \
                    "No security issues found" \
                    "Continue regular audits" \
                    "Maintain security baseline"
            fi
                fi
         rm -f "$tiger_log" # Clean up temp log
    fi  # <--- This is the line that was already present.  Include this line.

    # Run Lynis audit
    show_section "System Hardening Check"
    if command_exists "lynis"; then
        show_info "Running Lynis security audit..."
        local lynis_log=$(mktemp)

        # Run Lynis with progress and timeout, capture PID immediately
        timeout 300 lynis audit system --quick > "$lynis_log" 2>&1 &
        local lynis_pid=$! # Capture PID *immediately*
        show_spinner "$lynis_pid" "Analyzing system security" # Corrected: Use show_spinner.
        wait "$lynis_pid"

        if [[ $? -eq 124 ]]; then
            show_error "Lynis audit timed out" "Process took too long and was terminated"
            return 1
        elif [[ $? -ne 0 ]]; then # General error check
            show_error "Lynis Audit Failed" "Check Logs"
            return 1
        fi

        if [[ -f "$lynis_log" ]]; then
            show_section "Hardening Results"
            local warnings=$(grep -c "warning:" "$lynis_log") # Corrected grep
            local suggestions=$(grep -c "suggestion:" "$lynis_log") # Corrected grep

            show_result "Security Warnings" "$warnings" "$([[ "$warnings" = "0" ]] && echo "$GREEN" || echo "$YELLOW")"
            show_result "Improvement Suggestions" "$suggestions" "$CYAN"

            # Extract hardening index
            local hardening_index=$(grep "Hardening index" "$lynis_log" | awk '{print $NF}')
            if [[ -n "$hardening_index" ]]; then
                show_result "Hardening Index" "$hardening_index" \
                    "$([[ "${hardening_index%.*}" -ge 90 ]] && echo "$GREEN" || \
                      [[ "${hardening_index%.*}" -ge 75 ]] && echo "$YELLOW" || echo "$RED")"
            fi

            if [[ "$warnings" != "0" ]]; then
                show_guidance "Security Improvements" "warning" \
                    "Review /var/log/lynis.log for details" \
                    "Address warnings by priority" \
                    "Implement suggested improvements" \
                    "Document exceptions"

                # Show top warnings (up to 5)
                printf "\n${YELLOW}Top Security Warnings:${RESET}\n"
                grep "warning:" "$lynis_log" | head -n 5 | while IFS= read -r line; do
                    printf "  ${YELLOW}• %s${RESET}\n" "${line#*warning: }"  # Corrected string manipulation
                done
            else
                show_guidance "System Hardening" "success" \
                    "System meets security baseline" \
                    "Continue monitoring" \
                    "Schedule regular audits"
            fi
        fi
        rm -f "$lynis_log" # Clean up temp log
    fi

    show_header "Security Audit Complete"
    show_info "Review the findings above and take recommended actions"
    show_info "Consider implementing automated security checks"
    printf "\n${YELLOW}Note: Some warnings may be expected in Kali Linux due to its nature as a penetration testing distribution.${RESET}\n"
}


check_vm_shared_folders() {
    if mount | grep -q 'type vboxsf'; then
        show_warning "VM Shared Folders Detected" "Ensure /etc/aide is NOT in shared folder"
    fi
}

# Removed validate_aide_paths, as it was causing problems and the paths
# should be correctly handled by the AIDE installation itself.  If paths *are*
# incorrect, it points to a deeper system issue, not a script problem.

# Removed PS4 and functrace for production.

# Kali Linux paths - Using defaults from aide.conf is more robust.
# declare -r AIDE_CONF="/etc/aide/aide.conf"
# declare -r AIDE_DB_DIR="/var/lib/aide"
# declare -r AIDE_USER="kali" # Not used

# Main execution
main() {
    # Check if running as root
    if [[ "$(id -u)" != "0" ]]; then
        printf "${RED}This script must be run as root. Please use sudo.${RESET}\n" 1>&2 # To stderr
        exit 1
    fi

    hide_cursor
    display_banner

    # Install dependencies first
    install_dependencies

    # Check for VM shared folders
    check_vm_shared_folders

    while true; do
        show_menu
        case $choice in
            1) perform_security_scan ;;
            2) update_system ;;
            3) clean_system ;;
            4) malware_scan ;;
            5) security_hardening ;;
            6) network_security ;;
            7) backup_system ;;
            8) monitor_system ;;
            9) analyze_logs ;;
            10) secure_ssh ;;
            11) pentest_tools ;;
            12) check_web_security ;;
            13) monitor_bandwidth ;;
            14) check_containers ;;
            15) wireless_security ;;
            16) generate_report ;;
            0)
                clear
                printf "${CYAN}${BOLD}Thank you for using Kali Security Toolkit!${RESET}\n"
                printf "${GREEN}System secured and maintained.${RESET}\n"
                show_cursor
                exit 0
                ;;
            *)  # Handle invalid options gracefully.
                printf "${RED}Invalid option!${RESET}\n"
                sleep 1
                # The loop will continue and re-display the menu.
                ;;
        esac

        if [[ "$choice" != "0" ]]; then
            printf "\n${CYAN}Press ENTER to return to menu...${RESET}"
            read -r  # Wait for Enter key press.
            clear  # Clear the screen before redisplaying the menu.
        fi
    done
}

# Start script
main
