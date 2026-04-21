#!/bin/bash -eu

# Working functionality of the script:
#   Connect via SSH without verifying the key on the host
#


function usage {
    echo -e 'Run the script with the required params username password IPSwitch\nExample:
    sudo bash ssh_conn.sh bibo 12345678 127.0.0.1\n'
    echo -e 'Run the script without the specified params results in connecting the admin password 192.168.127.253'
    echo -e 'Example:
    sudo bash ssh_conn.sh'

    exit 1
}


function package_is_installed {
    # Checking the installed sshpass package

    if [[ -n $(printf "%s\n" "$(awk '{print $2}' <(dpkg -l | grep -i sshpass))") ]]; then
        return 0
    fi
    return 1
}


function init_ssh_connect() {
    # Establishing a SSH session

    local user=${1:-admin}
    local password=${2:-password}
    local ipSwitch=${3:-192.168.127.253}

    echo "-----------------------------"
    echo "| Connecting to remote host |"
    echo "-----------------------------"
    sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$user"@"$ipSwitch"
}


[[ "$1" == '-h' || "$1" == '--help' ]] && usage

if ! $(package_is_installed); then
    apt install sshpass
fi

init_ssh_connect "$1" "$2" "$3"
