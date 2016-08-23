#!/usr/bin/env bash

set -e  # exit on error

base_dir=$(dirname $(realpath "$0"))

install() {
    echo "installing..."
    ln -s "$base_dir/opt/spaceapi" "/opt/spaceapi"
    ln -s "$base_dir/etc/systemd/system/spaceapi.service" "/etc/systemd/system/spaceapi.service"
    virtualenv "/opt/spaceapi/venv"
    "/opt/spaceapi/venv/bin/python" "/opt/spaceapi/venv/bin/pip" install -r "$base_dir/requirements.txt"
    echo "done"
    echo "start|stop service:   'systemctl start|stop spaceapi'"
    echo "show log:             'journalctl -u spaceapi'"
}

uninstall() {
    echo "uninstalling..."
    systemctl stop spaceapi
    rm -rf "/opt/spaceapi"
    rm -f "/etc/systemd/system/spaceapi.service"
    echo "done"
}

if [ "$1" == "" ]; then
    install
elif [ "$1" == "remove" ]; then
    uninstall
else
    echo "Usage:"
    echo "install.sh"
    echo "    create symlinks"
    echo "install.sh remove"
    echo "    delete symlinks"
fi
