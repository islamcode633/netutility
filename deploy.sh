#!/usr/bin/env bash


USER=$(whoami)
declare -r WORK_DIR="/home/$USER/autotest"
declare -r REPO_URL="ssh://git@gitlab.dolomant.local:2202/gashimov/autotest.git"


function usage {
    echo "Run script in user dir -> /home/$USER/"
    echo " with one of the arguments $0 [ run | start ]"
    echo 'WARNING: To avoid conflicts, dirs names should not contain <autotest>'
    exit 0
}

function deployment {
    git clone "$REPO_URL" || {
        echo 'Error cloning remote repository !'
        exit 1
    }
    sudo apt update
    sudo apt install sshpass bridge-utils \
                    curl openssl snmp lldpd \
                    nmap jq python3.11-venv -y || { exit 2 ; }
    python3 -m venv "$WORK_DIR"
}

function manage {
    [ ! -d "$WORK_DIR" ] && deployment && exit 0

    echo "Dir [ autotest ] has already been created !"
    echo "Do you want to delete it and repeat the deployment process? (y/yes)"
    read -r
    [[ "$REPLY" == 'y' || "$REPLY" == 'yes' ]] && {
        rm -rf "$WORK_DIR"
        deployment && echo "Done!"
    }
}

function run {
    case "$1" in
        'h' | 'help' | '-h' | '--help') usage ;;
        'run' | 'start') manage ;;
    esac
}

run "$1"
