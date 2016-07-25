#script will install node and dependencies

apt-get install vlc
apt-get install build-essential checkinstall
apt-get install libssl-dev
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash

echo 'Close your terminal and Reopen it... then run: nvm install 4.4.3'
