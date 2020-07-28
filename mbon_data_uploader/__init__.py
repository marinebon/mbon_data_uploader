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

# =======================================================================
# === File upload targets. Comment out any routes you aren't using.
# =======================================================================
from mbon_data_uploader.handle_csv_file import handle_csv_file
from mbon_data_uploader.handle_worldview_image import handle_worldview_image
# =======================================================================


def create_app(test_config=None):

    UPLOAD_FOLDER = tempfile.gettempdir()

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    logging.basicConfig(filename='mbon_data_uploader.log', level=logging.INFO)
    UPLOAD_ROUTES = []

    # =======================================================================
    # === File upload targets. Comment out any routes you aren't using.
    # =======================================================================
    UPLOAD_ROUTES.append("sat_image_extraction")
    @app.route('/submit/sat_image_extraction', methods=['GET', 'POST'])
    def sat_image_extraction():
        return get_form_and_post_upload(
            request,
            allowed_extensions={'csv'},
            file_handler=handle_csv_file,
            template="sat_image_extraction.html"
        )

    UPLOAD_ROUTES.append("worldview_image")
    @app.route('/submit/worldview_image', methods=['GET', 'POST'])
    def worldview_image():
        return get_form_and_post_upload(
            request,
            allowed_extensions={'tif'},
            file_handler=handle_worldview_image,
            template="worldview_image.html"
        )
    # =======================================================================

    @app.route('/', methods=['GET'])
    def welcome_page():
        """
        Welcome page shows basic explaination and list of submission routes.
        """
        return render_template(
            "welcome_page.html", UPLOAD_ROUTES=UPLOAD_ROUTES
        )

    def allowed_file(filename, allowed_extensions):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @app.route('/upload_success', methods=['GET'])
    def upload_success():
        return '''
        <!doctype html>
        <title>File Uploaded</title>
        <h1>Your file has been uploaded</h1>
        '''

    def check_for_file(request):
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        return request.files['file']

    def validate_and_handle_file(allowed_extensions, file_handler):
        # if user does not select file, browser also
        # submit an empty part without filename
        file = check_for_file(request)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(
            file.filename, allowed_extensions
        ):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_handler(filepath, request.form)
            return redirect(
                url_for('upload_success', filename=filename)
            )

    def get_form_and_post_upload(
        request, allowed_extensions, file_handler, template
    ):
        if request.method == "POST":
            return validate_and_handle_file(
                allowed_extensions=allowed_extensions,
                file_handler=file_handler
            )
        else:  # method == GET
            assert request.method == 'GET'
            return render_template(f"submit/{template}")

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
