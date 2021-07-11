FROM dorowu/ubuntu-desktop-lxde-vnc
RUN apt-get -y update
RUN apt-get install -y apt-utils google-chrome-stable xdotool
RUN apt -y update
RUN apt install -y terminator git
RUN cd /root && git clone https://github.com/aurum408/TeleM.git && cp TeleM/save_page_as .
