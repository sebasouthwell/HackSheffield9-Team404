# Create a flask app and define the routes

from flask import Flask, request
from ai_hallucination_lib import *
loadDotEnv()

databricksHandler = DataBricksManager()
dalleHandler = DallEHandler("", 0.4, 0.4, None)

app = Flask(__name__) 

# Set new prompt, and base image
@app.route('/prompt_text', methods=['POST'])
def get_prompt_text():

    prompt = request.json['prompt']
    print(prompt)
    if prompt is not None:
        dalleHandler.stable_prompt = prompt
    
    return "OK"

@app.route('/prompt_image', methods=['POST'])
def get_prompt_image():
    image_file = request.files.get('media')
    print(image_file)
    if image_file is not None:
        dalleHandler.last_image = image_file
    
    return "OK"

# Get Image as VASD format
@app.route('/image', methods=['GET'])
def get_image():
    x = request.args.get('x')
    y = request.args.get('y')
    original_image_file =  Image.open("output.png", stream=True).raw
    new_image_file = dalleHandler.generate_new_region(original_image_file, x, y)
    dalleHandler.image_to_vasd_format(image=new_image_file, image_path="output_vasd")
    with open("output_vasd", "r") as f:
        output = f.read()

    return output

if __name__ == "__main__":
    app.run(debug=True) 