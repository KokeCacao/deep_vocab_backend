#!/usr/bin/zsh

echo "You should edit last line of environment.yml to edit the path of environment you want to install"

# to add channels
conda config --add channels conda-forge
conda config --set channel_priority strict

conda env create -f environment.yml
conda activate web

sudo cp /home/ubuntu/dev/deep_vocab_backend/deepvocab.service /etc/systemd/system/deepvocab.service
sudo systemctl daemon-reload
sudo systemctl enable deepvocab
sudo systemctl restart deepvocab