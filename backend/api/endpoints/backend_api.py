from flask import Blueprint, request

backend_api = Blueprint('media', __name__, url_prefix='/backend')

@backend_api.route('/get_image', methods=['GET', 'POST'])
def get_image():
    imagefile = request.files.get('media')
    return f"Got {imagefile.filename}"


