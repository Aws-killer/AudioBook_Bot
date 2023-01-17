FROM python:latest
WORKDIR /usr/src/nginx
COPY . .
RUN apt-get update
RUN apt install -y aria2
RUN python3 -m pip install -r requirements.txt 
CMD aria2c --dir="./Downloads"  -x 4  -j 30  --seed-time=0  -m 0  --bt-stop-timeout=1000  --enable-rpc --rpc-listen-all --check-certificate=false --rpc-listen-port=8070 & python3 -m Bot
EXPOSE 8070
