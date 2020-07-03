import os
import subprocess
import tempfile

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


def create_app(test_config=None):

    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_EXTENSIONS = {'csv'}

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def handle_file(filepath):
        """
        Pushes data from file into influxdb
        """
        assert ".csv" in filepath
        subprocess.run([
            "export_csv_to_influx",
            "--csv", filepath,
            "--dbname", "fwc_coral_disease",
            "--measurement", "user_custom_timeseries",  # TODO: set this to something less generic
            "--field_columns", "mean,climatology,anomaly",
            "--force_insert_even_csv_no_update", "True",
            "--server", "tylar-pc:8086"  # TODO: update this for prod
            "--time_column", "Time"
        ])

    @app.route('/upload_success', methods=['GET'])
    def upload_success():
        return '''
        <!doctype html>
        <title>File Uploaded</title>
        <h1>Your file has been uploaded</h1>
        '''

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                handle_file(filepath)
                return redirect(url_for('upload_success',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

    return app
