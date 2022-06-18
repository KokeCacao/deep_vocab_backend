#!/usr/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh && \
conda activate deepvocab && \
/home/ubuntu/miniconda3/envs/deepvocab/bin/gunicorn --workers 1 --threads 8 --log-level debug --worker-class eventlet --bind unix:/home/ubuntu/dev/deep_vocab_backend/deepvocab.sock wsgi:app