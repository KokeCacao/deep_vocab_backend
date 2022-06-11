#!/usr/bin/zsh

read -p "Do you have conda installed? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    which conda
else
    echo "Please install conda first."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

read -p "Have you added conda-forge " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    conda config --add channels conda-forge && onda config --set channel_priority flexible && echo "Please start a new shell and run the script again."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

read -p "Are you currently in deepvocab environment? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    conda deactivate
fi

conda remove --name deepvocab --all

conda create --name deepvocab python=3.10.4 -c conda-forge -y && \
conda activate deepvocab && \
conda list

conda install "flask>=2.1.2" eventlet flask-graphql flask-testing aniso8601 "PyJWT=2.0.1" graphql-relay graphene pandas tqdm python-dotenv && \
pip install flask-graphql-auth graphene-file-upload && \
conda install -c conda-forge flask-sqlalchemy

conda activate web

read -p "Do you want me to set up service? Choose no if you are not on Linux system. " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo cp /home/ubuntu/dev/deep_vocab_backend/deepvocab.service /etc/systemd/system/deepvocab.service && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable deepvocab && \
    sudo systemctl restart deepvocab
fi

echo "You are good to go. Please make sure to create a `.env` file following the installation instruction before running."
exit 0