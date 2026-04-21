#!/usr/bin/env bash
set -eu


URL=https://download.docker.com/linux/debian/dists/bookworm/pool/stable/amd64
CONTAINERD=containerd.io_2.1.5-1~debian.12~bookworm_amd64.deb
DOCKER_CE=docker-ce_29.0.2-1~debian.12~bookworm_amd64.deb
DOCKER_CE_CLI=docker-ce-cli_29.0.2-1~debian.12~bookworm_amd64.deb
DOCKER_BUILDX_PLUGIN=docker-buildx-plugin_0.30.0-1~debian.12~bookworm_amd64.deb
DOCKER_COMPOSE_PLUGIN=docker-compose-plugin_2.40.3-1~debian.12~bookworm_amd64.deb

# prerequisites for instsall docker engine
function check_firewall {
    #
    if sudo systemctl status ufw firewalld 2>/dev/null; then
        sudo systemctl stop ufw firewalld
    fi
    echo "Firewall: Off"
}

function check_conflict_pcks {
    # check installed bin pck via dpkg <---
    echo "Conflicting packages Not found !"
    sudo rm -rf /var/lib/docker/* && echo "Cleaned all images in /var/lib/docker/ !"
}

function download_docker_deb_pcks {
    #
    for deb_pck in "$URL/$CONTAINERD" "$URL/$DOCKER_CE" "$URL/$DOCKER_CE_CLI" \
                    "$URL/$DOCKER_BUILDX_PLUGIN" "$URL/$DOCKER_COMPOSE_PLUGIN"
    do
        wget "$deb_pck"
    done
    return $?
}

function install_docker_deb_pcks {
    # 
    sudo dpkg -i "$CONTAINERD" "$DOCKER_CE" \
            "$DOCKER_CE_CLI" "$DOCKER_BUILDX_PLUGIN" \
            "$DOCKER_COMPOSE_PLUGIN"
}

function start_docker_service {
    #
    if sudo systemctl status docker &>/dev/null; then
        echo "dockerd started !"
        return
    fi
    sudo systemctl start docker && sudo docker run hello-world
}


#check_firewall
#check_conflict_pcks
#download_docker_deb_pcks && install_docker_deb_pcks

#rm -rf docker-*.deb* containerd.io*.deb*

# add user to docker group
#sudo usermod -a -G docker "$(whoami)"

start_docker_service
