#!/bin/bash
# Make new instance based on NVIDIA tensorflow image, A100, ~150G hard drive
# [considering making this a preemptible instance if workflow is <= 24h long - per Fengchen’s advice]
#  make instance from this template:
# https://console.cloud.google.com/marketplace/product/click-to-deploy-images/deeplearning

# Machine type
# n1-highmem-8 (8 vCPUs, 52 GB memory)
# Use V100 GPU (1 of them)

# start

# some housekeeping:
# cribbed from here:
#https://github.com/AnacletoLAB/ensmallen_graph/blob/transitivity/setup/setup.sh

cd

###########################################################
# Setup Rust nightly
###########################################################
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > $HOME/rustup.sh
chmod +x /$HOME/rustup.sh
$HOME/rustup.sh --default-host x86_64-unknown-linux-gnu --default-toolchain nightly --profile default -y
echo "source $HOME/.cargo/env" >> $HOME/.bashrc
rm $HOME/rustup.sh

# load for current shell
source $HOME/.bashrc
source $HOME/.cargo/env

# Need this later
pip3 install silence_tensorflow

# Install ensmallen and embiggen:
rm -fr ensmallen_graph
git clone https://github.com/AnacletoLAB/ensmallen_graph.git
cd ensmallen_graph
git checkout develop
cargo install maturin
cd ./bindings/python; maturin develop --release

# Then for embiggen:
cd
rm -fr embiggen
git clone https://github.com/monarch-initiative/embiggen.git
cd embiggen
git checkout develop
pip install . -U --user

# Install monarch-embedding
cd
git clone https://github.com/Knowledge-Graph-Hub/monarch-embedding.git

# Note: for now we are logging in as user ‘jenkins’ but running the script as user
# ‘jtr4v’, because that seems to be the only way to get this gcloud instance to
# actually use the GPUs, owing to a CUDA driver problem of some kind.

sudo python3 -m pip install awscli==1.18.105
sudo python3 -m pip install botocore==1.17.28
sudo pip3 install s3cmd boto3

echo "setting up aws credentials:"
aws configure # enter access key and secret key
