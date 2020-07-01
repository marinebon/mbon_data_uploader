# based on code from
# https://www.google.com/search?client=firefox-b-1-d&sxsrf=ALeKk01rDxvso1gCGvfOIM3N23NWVU8WTQ%3A1593623338248&ei=KsP8Xq_VDoac_Qa4qJ-YCA&q=%22flask-uploads%22+tutorial&oq=%22flask-uploads%22+tutorial&gs_lcp=CgZwc3ktYWIQAzIECCMQJzoECAAQR1DsLVjWP2CoQWgAcAF4AIAB-AKIAdcMkgEHMC4yLjEuM5gBAKABAaoBB2d3cy13aXo&sclient=psy-ab&ved=0ahUKEwivku3HxazqAhUGTt8KHTjUB4MQ4dUDCAs&uact=5#kpvalbx=_RcP8Xq_yL8S1ggeX9pyYCg26

from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, DATA

UPLOADED_TIMESERIES_DEST = '/tmp/timeseries'
DEBUG = True

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(__name__)

    uploaded = UploadSet('timeseries', DATA)
    configure_uploads(app, uploaded)

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            return filename
        return render_template('upload.html')
    return app
