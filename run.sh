#!/usr/bin/zsh
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate web
/usr/bin/authbind --deep /home/ubuntu/miniconda3/envs/web/bin/gunicorn -w 1 -k eventlet -b 0.0.0.0:5000 'wsgi:app' --certfile=/etc/letsencrypt/live/kokecacao.me/fullchain.pem --keyfile=/etc/letsencrypt/live/kokecacao.me/privkey.pem --log-level debug
