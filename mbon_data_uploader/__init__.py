"""
Contains the web application factory.
"""
import logging
import os
import tempfile
import traceback

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
from flask import url_for

from mbon_data_uploader.handle_csv_file import handle_csv_file


def create_app(test_config=None):

    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_EXTENSIONS = {'csv'}

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    logging.basicConfig(filename='mbon_data_uploader.log', level=logging.INFO)

    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            logging.info("POST")
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
                handle_csv_file(filepath, request.form)
                return redirect(url_for('upload_success',
                                        filename=filename))
        else:  # method == GET
            logging.info("GET")
            assert request.method == 'GET'
            return render_template("file_submission.html")

    @app.errorhandler(500)
    def handle_http_exception(error):
        stacktrace = traceback.format_exc()
        error_dict = {
            'code': error.code,
            'description': error.description,
            'stack_trace': stacktrace
        }
        dir(error)
        # if isinstance(error, subprocess.CalledProcessError):
        if "subprocess.CalledProcessError" in stacktrace:
            error_dict['return_code'] = error.original_exception.returncode
            error_dict['output'] = error.original_exception.output
            error_dict['stdout'] = error.original_exception.stdout
            error_dict['stderr'] = error.original_exception.stderr
            return render_template(
                "error_subprocess.html", error_dict=error_dict
            )  # , 500
        else:
            return render_template(
                "error.html", error_dict=error_dict
            )  # , 500

    return app
