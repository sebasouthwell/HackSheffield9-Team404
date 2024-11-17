# Create a flask app and define the routes

from urllib import request
from flask import Flask
from ai_hallucination_lib import *
test = DataBricksManager()


@app.route('/image', methods=['GET'])
def get_image():
    # Get query parameters
    x = request.args.get('x')
    y = request.args.get('y')

@app.route('/prompt', methods=['GET'])
def get_prompt():
    # Get query parameters
    prompt = request.args.get('prompt')
    res = test.chain.invoke(prompt)



if __name__ == '__main__':
    loadDotEnv()
    app = Flask(__name__)
    app.run(debug=True)