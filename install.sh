#!/usr/bin/bash
cd "$(dirname "$0")"

while true; do
read -p "Do you have conda installed? (y/n) " yn
case $yn in 
	[yY] )
    echo "Your conda path is: " && which conda
    eval "$(conda shell.bash hook)" && conda --help
		break;;
	[nN] )
    echo "Please install conda first."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1;; # handle exits from shell or function but don't exit interactive shell
	* ) echo "Invalid Response";;
esac
done

while true; do
read -p "Have you added conda-forge? If not I will add it for you and set priority to flexible.  (y/n) " yn
case $yn in 
	[yY] )
		break;;
	[nN] )
    conda config --add channels conda-forge && conda config --set channel_priority flexible && echo "Please start a new shell and run the script again."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1;; # handle exits from shell or function but don't exit interactive shell
	* ) echo "Invalid Response";;
esac
done

while true; do
read -p "Are you currently in deepvocab environment? If so I will deactivate it.  (y/n) " yn
case $yn in 
	[yY] )
    conda deactivate
		break;;
	[nN] )
    break;;
	* ) echo "Invalid Response";;
esac
done

while true; do
read -p "Should I remove deepvocab environment and do a clean installation? (y/n) " yn
case $yn in 
	[yY] )
    conda remove --name deepvocab --all
		break;;
	[nN] )
    break;;
	* ) echo "Invalid Response";;
esac
done

while true; do
read -p "I will create a new deepvocab environment using conda create? (y/n) " yn
case $yn in 
	[yY] )
    conda create --name deepvocab python=3.9 -c conda-forge
		break;;
	[nN] )
    break;;
	* ) echo "Invalid Response";;
esac
done

conda activate deepvocab && \
conda list && \
echo "Above is your current packages"

while true; do
read -p "I will install dependencies using conda and pip. Proceed? (y/n) " yn
case $yn in 
	[yY] )
    conda install "flask>=2.1.2" flask-graphql flask-testing aniso8601 "PyJWT=2.0.1" graphql-relay graphene pandas tqdm python-dotenv && \
    pip install flask-graphql-auth graphene-file-upload && \
    conda install -c conda-forge flask-sqlalchemy && \
    pip install "https://github.com/benoitc/gunicorn/archive/ff58e0c6da83d5520916bc4cc109a529258d76e1.zip#egg=gunicorn==20.1.0" "eventlet==0.33.1" setuptools six greenlet dnspython
    # https://github.com/benoitc/gunicorn/pull/2581#issuecomment-994809596
		break;;
	[nN] )
    break;;
	* ) echo "Invalid Response";;
esac
done

while true; do
read -p "Do you want me to set up service and SSL? Choose no if you are not on Linux system or you are not running a server. (y/n) " yn
case $yn in 
	[yY] )
    while true; do
    read -p "Do you have Nginx installed. If not, I will install it for you. (y/n) " yn
    case $yn in 
      [yY] )
        break;;
      [nN] )
        sudo apt install nginx
        break;;
      * ) echo "Invalid Response";;
    esac
    done

    sudo nginx -t && \
    sudo cp -i ./deepvocab.conf /etc/nginx/sites-available/deepvocab.conf && \
    echo "Successfully copied configuration to '/etc/nginx/sites-available/deepvocab.conf'" && \
    sudo ln -i -s /etc/nginx/sites-available/deepvocab.conf /etc/nginx/sites-enabled/ && \
    echo "Successfully linked configuration to '/etc/nginx/sites-enabled/'" && \
    sudo nginx -t && \
    sudo nginx -s reload
    
    while true; do
    read -p "Do you have certbot installed. If not, I will install it for you. (y/n) " yn
    case $yn in 
      [yY] )
        break;;
      [nN] )
        sudo apt install certbot
        break;;
      * ) echo "Invalid Response";;
    esac
    done

    echo "Your SSL ceertificate is: (please provide sudo password)" && \
    sudo certbot certificates && \
    echo "If you don't see your website on the certificate above, set up Nginx and run 'sudo certbot certonly --nginx' and select the current website"
    
    while true; do
    read -p "Should I run certbot to set up SSL for you. Choose no if you already saw your website above. (y/n) " yn
    case $yn in 
      [yY] )
        sudo certbot certonly --nginx && \
        echo "You should see your renew timer:" && \
        sudo systemctl list-timers
        break;;
      [nN] )
        break;;
      * ) echo "Invalid Response";;
    esac
    done

    while true; do
    read -p "Do you want me to setup service? I assume you have 'kokecacao-gunicorn-pre.service' service running and have 'www-data' user and group setup with correct permission. The service will launch as a child of 'kokecacao-gunicorn.service'. If you don't understand what I am talking about, please select no. (y/n) " yn
    case $yn in 
      [yY] )
        sudo cp -i ./deepvocab.service /etc/systemd/system/deepvocab.service && \
        sudo systemctl daemon-reload && \
        sudo chown -R www-data:www-data /home/ubuntu/dev/deep_vocab_backend && \
        sudo systemctl enable deepvocab && \
        sudo systemctl restart deepvocab
        break;;
      [nN] )
        break;;
      * ) echo "Invalid Response";;
    esac
    done
		break;;
	[nN] )
    break;;
	* ) echo "Invalid Response";;
esac
done

echo "You are good to go. Please make sure to create a '.env' file and get the '.csv' vocab list following the installation instruction before running. Also do not forget to do both chown www-data:www-data [path-of-database] and chown -R www-data:www-data [path-of-database-directory]"


while true; do
read -p "Check the status of deepvocab service? (y/n) " yn
case $yn in 
  [yY] )
    sudo systemctl status deepvocab
    break;;
  [nN] )
    break;;
  * ) echo "Invalid Response";;
esac
done

exit 0