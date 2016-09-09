#install git and base repositories
apt-add-repository universe
apt-add-repository multiverse
apt-get update

#install essentials
apt-get install git vlc build-essential checkinstall curl libssl-dev tightvncserver python-pip python-dev python-imaging-tk libvlc-dev libvlc5

#install vlc and node
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash
source ~/.bashrc
source /home/ubuntu/.bashrc
nvm install 4.4.3

#install dtrx -- few of us prefer this package, not required
wget http://brettcsmith.org/2007/dtrx/dtrx-7.1.tar.gz
tar -xvf dtrx-7.1.tar.gz 
cd dtrx-7.1
python setup.py install --prefix=/usr/local
cd ..
rm -rf dtrx-7.1
rm dtrx-7.1.tar.gz

#VNC config
mkdir -p /etc/lightdm/lightdm.conf.d
cp vnc_config /etc/lightdm/lightdm.conf.d/vnc.conf

#disable usb 3.0 autosuspend
echo "Disabling usb autosuspend..."
echo -1 > /sys/module/usbcore/parameters/autosuspend

#enable usb 3.0
echo "Enabling usb 3.0..."
python enableUSB.py | grep usb_port_owner_info=

#install arduino ide
echo "Downloading Arduino IDE"
wget https://downloads.arduino.cc/arduino-1.6.9-linuxarm.tar.xz
echo "extracting tarball..."
tar -xf arduino-1.6.9-linuxarm.tar.xz -C /etc/
/etc/arduino-1.6.9/install.sh
ln -s /etc/arduino-1.6.9/arduino /usr/bin/arduino
rm arduino-1.6.9-linuxarm.tar.xz
source ~/.bashrc

#performance mode
echo "Enabling Performance mode.."
cp startup_config /etc/rc.local
chmod +x /etc/rc.local
/etc/rc.local

#pip, and other dependencies
pip install numpy
pip install matplotlib

#don't prompt on shutdown
gsettings set com.canonical.indicator.session suppress-logout-restart-shutdown true

