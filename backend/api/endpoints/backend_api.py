from flask import Blueprint

backend_api = Blueprint('media', __name__, url_prefix='/backend')

@backend_api.route('/get_image', methods=['GET'])
def get_image():
    return "hello world"