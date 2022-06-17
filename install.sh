#!/usr/bin/bash
cd "$(dirname "$0")"

read -p "Do you have conda installed? (y/N) " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Your conda path is: " && which conda
    eval "$(conda shell.bash hook)" && conda --help
else
    echo "Please install conda first."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

read -p "Have you added conda-forge? If not I will add it for you and set priority to flexible. (Y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    conda config --add channels conda-forge && conda config --set channel_priority flexible && echo "Please start a new shell and run the script again."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

read -p "Are you currently in deepvocab environment? If so I will deactivate it. (y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    conda deactivate
fi

read -p "Should I remove deepvocab environment and do a clean installation? (y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    conda remove --name deepvocab --all
fi

read -p "I will create a new deepvocab environment using conda create? (y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    conda create --name deepvocab python=3.9 -c conda-forge
fi

conda activate deepvocab && \
conda list

read -p "I will install dependencies using conda and pip. Proceed? (y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    conda install "flask>=2.1.2" flask-graphql flask-testing aniso8601 "PyJWT=2.0.1" graphql-relay graphene pandas tqdm python-dotenv && \
    pip install flask-graphql-auth graphene-file-upload && \
    conda install -c conda-forge flask-sqlalchemy && \
    pip install "gunicorn==20.1.0" "eventlet==0.33.1" setuptools six greenlet dnspython
fi

read -p "Since eventlet==0.33.1 is not compatible (https://github.com/eventlet/eventlet/issues/733) with python 3.10, so we need to install a dev version of eventlet. Can I do that?" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    pip install https://github.com/eventlet/eventlet/archive/master.zip
fi

read -p "Do you want me to set up service? Choose no if you are not on Linux system or you are not running a server. (y/N)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo cp ./deepvocab.service /etc/systemd/system/deepvocab.service && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable deepvocab && \
    sudo systemctl restart deepvocab
fi

echo "You are good to go. Please make sure to create a .env file following the installation instruction before running."
exit 0