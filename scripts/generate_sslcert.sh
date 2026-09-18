#!/usr/bin/bash -eu


function generate_sslcert {
    # Checking SSL certificate support on the host
    local IP='192.168.127.253:443'

    echo -e "Supported SSL certificates:"
    sleep 5 # else test crashing
    for cipher in $(openssl ciphers 'ALL:eNULL' | sed -e 's/:/ /g'); do
        awk '{print $3}' <(openssl s_client -cipher "$cipher" -connect "$IP" 2>/dev/null | grep -i 'cipher    :')
    done
}

# successfully log in to the host and open HTTPS port 443
generate_sslcert
