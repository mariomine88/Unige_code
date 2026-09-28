#!/bin/bash

apt update -y
apt upgrade -y
echo "Europe/Madrid" >/etc/timezone
ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime
apt install -y tzdata 
dpkg-reconfigure --frontend noninteractive tzdata

apt install -y build-essential ca-certificates apt-utils
apt install -y nfs-common
