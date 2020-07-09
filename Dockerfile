FROM python:3.7

# RUN apt-get update
# RUN apt-get -y upgrade

# RUN apt-get install -y python3.6 python3.6-pip

COPY . /opt/mbon_data_uploader

# === install dependencies
WORKDIR /opt/mbon_data_uploader
RUN pip install -r requirements.txt

# startup the production app
ENTRYPOINT ["waitress-serve", "--port=5000", "--call", "mbon_data_uploader:create_app"]

# # OR startup the dev app
# RUN export FLASK_APP=mbon_data_uploader
# RUN export FLASK_ENV=development
# ENTRYPOINT ["flask", "run"]
