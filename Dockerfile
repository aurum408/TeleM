FROM dorowu/ubuntu-desktop-lxde-vnc
RUN apt-get update
RUN apt-get install -y google-chrome-stable
RUN add-apt-repository ppa:gnome-terminator
RUN apt-get update
RUN apt-get install terminator
