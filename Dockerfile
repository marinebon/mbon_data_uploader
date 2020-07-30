FROM python:3.7

# RUN apt-get update
# RUN apt-get -y upgrade

# RUN apt-get install -y python3.6 python3.6-pip

COPY . /opt/mbon_data_uploader

# === install dependencies ==================================================
WORKDIR /opt/mbon_data_uploader
RUN pip install -r requirements.txt

# IPFS (for postgis worldview_image db)
WORKDIR /opt/go-ipfs
RUN wget https://dist.ipfs.io/go-ipfs/v0.6.0/go-ipfs_v0.6.0_linux-amd64.tar.gz
RUN tar xvfz go-ipfs_v0.6.0_linux-amd64.tar.gz
WORKDIR /opt/go-ipfs/go-ipfs
RUN ./install.sh
RUN ipfs init
# ===========================================================================

# startup the production app
WORKDIR /opt/mbon_data_uploader
ENTRYPOINT ["waitress-serve", "--port=5000", "--call", "mbon_data_uploader:create_app"]

# # OR startup the dev app
# RUN export FLASK_APP=mbon_data_uploader
# RUN export FLASK_ENV=development
# ENTRYPOINT ["flask", "run"]
