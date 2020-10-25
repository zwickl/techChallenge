#!/bin/bash

#starting with fresh medium3 Ubuntu Atmosphere instance

#no apt ipackage for microk8s, but there is a snap
snap install microk8s --classic
#sudo snap install kubectl --classic
#think that snap version of this may be causing problems, use apt below
#sudo snap install docker --classic
#don't think this is neededdd
#sudo snap install nats-server

#virtualbox needed to create minikube VMa
#this may requirte manually clicking to accept liscence 
sudo apt --assume-yes install virtualbox virtualbox-ext-pack
sudo apt --assume-yes install docker.io

curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
chmod +x kubectl
sudo cp kubectl /usr/local/bin/

#minikube install instruct mostly from
#https://phoenixnap.com/kb/install-minikube-on-ubuntu
MKBIN=minikube-linux-amd64
wget https://storage.googleapis.com/minikube/releases/latest/$MKBIN
sudo cp $MKBIN /usr/local/bin/minikube
sudo chmod 755 /usr/local/bin/minikube
minikube start docker-env

#set docker to use image registry within minikube VM, instead if on master node
#this is surely not optimal, and best way would be to set up a proper local docker registry 
#or use a remote public repo
eval $(minikube -p minikube docker-env)

#get necessary docker images
sudo docker pull python

