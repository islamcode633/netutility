#!/bin/sh

# Working functionality of the script:
#   The simply script get info about Switch
#   INFO: CPU/Eth interfaces/mountpoints/hostname/disk space/ and etc...
#


print_first() {
    # System and CPU information

    uname -a
    echo ""
    echo \[ CPU \] && cat /proc/cpuinfo
}


exec_cmds() {
    # Execute commands to collect switch information with output to stdout 
    # every 10 seconds

    for cmd in "$@"; do
        echo "Command: [ $cmd ]"
        echo "-- Data block: --"
            $cmd
        echo -e "-- End --\n"
        sleep 10
    done
}



case "$1" in
    '-h'|'--help')
        help='Go to the Linux command shell on the switch and \
    make the file executable and after run ./get_hwinfo_switch.sh'
        eval "echo $help ; exit 1"
        ;;
    *)
        print_first
        exec_cmds 'df -h' 'free' 'fdisk -l' \
            'lsusb' 'blkid' 'mount' \
            'ip a' 'route' \
            'id' 'hostname' 'env' \
            'lsmod' 'lsof' \
            'ps'
        ;;
esac
