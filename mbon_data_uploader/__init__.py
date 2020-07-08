import os
import tempfile

from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

from mbon_data_uploader.handle_csv_file import handle_csv_file


def create_app(test_config=None):

    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_EXTENSIONS = {'csv'}

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
            assert request.method == 'GET'
            return render_template("file_submission.html")

    return app
