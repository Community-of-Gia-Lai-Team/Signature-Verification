FROM ubuntu:latest
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3.8
RUN ln -s /usr/bin/pip3 /usr/bin/pip && \
    ln -s /usr/bin/python3.8 /usr/bin/python
RUN apt-get install -y python3-pip python3-dev build-essential hdf5-tools libgl1 libgtk2.0-dev
COPY . /app
RUN pip3 install -r requirements.txt
EXPOSE 8080
CMD ["python3", "api.py"]