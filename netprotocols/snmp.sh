#!/usr/bin/bash -eu
# Only use in Test case: SNMP


SWITCH_IP="192.168.127.253"
BASE_COMMAND="snmpwalk -v 3 -a MD5 -A testpassword -e 123456789B -E 123456789B -l authPriv \
            -u testuser -x DES -X testpassword $SWITCH_IP"
# find fields SNMPv2-MIB
$BASE_COMMAND "SNMPv2"
# set field  SNMPv2-MIB::sysContact.0.
$BASE_COMMAND "SNMPv2-MIB::sysContact.0 s teststring"
# read previous step field
$BASE_COMMAND "SNMPv2-MIB::sysContact.0"
