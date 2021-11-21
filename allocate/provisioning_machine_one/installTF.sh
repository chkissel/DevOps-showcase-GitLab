#!/bin/bash

# Install unzip
sudo apt-get install unzip

# Install in /tmp
cd /tmp

# Download latest version of the terraform (substituting newer version number if needed)
wget https://releases.hashicorp.com/terraform/0.12.19/terraform_0.12.19_linux_amd64.zip

# Extract the downloaded file archive
unzip terraform_0.12.19_linux_amd64.zip

# Move the executable into a directory searched for executables
sudo mv terraform /usr/local/bin/

# Run it
terraform --version 