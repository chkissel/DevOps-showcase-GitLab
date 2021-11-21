#!/bin/bash

apt-get update

# Install docker
curl -sSL https://get.docker.com/ | sh

# Install docker-compose
apt  install docker-compose

# Make directories for saving images
mkdir backend_data

# Create ssh key for digital ocean
ssh-keygen -t ecdsa




