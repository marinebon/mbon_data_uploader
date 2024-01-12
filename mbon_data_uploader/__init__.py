"""
Contains the web application factory.
"""
import logging
import os
import tempfile
import traceback

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
from mbon_data_uploader.handle_wq_data_ws import handle_wq_data_ws
# =======================================================================

__version__ = "1.2.0"


from mbon_data_uploader.strfy_subproc_error import strfy_subproc_error


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

    UPLOAD_ROUTES.append("wq_data_ws")
    @app.route('/submit/wq_data_ws', methods=['GET', 'POST'])
    def wq_data_ws():
        return get_form_and_post_upload(
            request,
            allowed_extensions={'xlsx'},
            file_handler=handle_wq_data_ws,
            template="wq_data_ws.html"
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

    def check_for_file(request):
        # check if the post request has the file part
        if 'file' not in request.files:
            return "No file part"
        return request.files['file']

    def validate_and_handle_file(allowed_extensions, file_handler):
        # if user does not select file, browser also
        # submit an empty part without filename
        file = check_for_file(request)
        file_allowed = allowed_file(
            file.filename, allowed_extensions
        )
        if file.filename == '':
            return 'No selected file'
        elif file and file_allowed:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            output = file_handler(filepath, request.form)
            return render_template(
                "upload_success.html", 
                out=output, 
                fpath=filepath, 
                handler=file_handler,
                version=__version__,
            )
        elif file_allowed is False:
            return "File extension not allowed"
        else:
            raise ValueError("unknown proble with file")

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
        error_dict = {
            '__version__': __version__,
            'error_desc_text': strfy_subproc_error(error)
        }
        return render_template(
            "error.html", error_dict=error_dict
        ), 500

    return app
