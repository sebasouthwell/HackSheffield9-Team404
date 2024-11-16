from flask import Flask, Blueprint
from api.endpoints import backend_api 


# Define the main API Blueprint without static and template folders
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register each endpoint Blueprint(endpoint we create)
api_bp.register_blueprint(backend_api.backend_api)
    
def create_app():
    # Correct the path for static_folder
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)