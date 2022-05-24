#!/usr/bin/zsh
sudo cp /home/ubuntu/dev/deep_vocab_backend/deepvocab.service /etc/systemd/system/deepvocab.service
sudo systemctl daemon-reload
sudo systemctl enable deepvocab
sudo systemctl restart deepvocab