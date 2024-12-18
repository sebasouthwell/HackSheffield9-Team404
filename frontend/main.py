import streamlit as st
import requests

url = 'http://localhost:5000'

# Title of the app
st.title('Simple Streamlit App')


st.write()
gen_choice = st.radio("How do you want to generate your image? Text or Base Image?", ["Text", "Image"])

if gen_choice == "Text":
    prompt = st.text_input("prompt?")

elif gen_choice == "Image":
    images = {"Image 1": "images/base_image_1.png", "Image 2": "images/base_image_2.jpg", "Image 3": "images/base_image_3.jpg"}
    cols = st.columns(len(images))

    for index, col in enumerate(cols):
        with col:
            key = list(images.keys())[index]
            value = images[key]
            st.image(value, caption=key, width=200)

    # Choose base image
    choice = st.radio("What image do you want to choose as a base?", list(images.keys()))

    st.write("Or choose your own image below")

    uploaded_file = st.file_uploader("Choose a file")
   
send_button = st.button("Send image button", type="primary")

if send_button:
    headers = {'Content-type': 'application/json; image/*'}

    if gen_choice == "Text":
        get_image_url = f"{url}/prompt_text"
        prompt_body = {"prompt": prompt }
        requests.post(get_image_url, json=prompt_body)

    elif gen_choice == "Image":

        if uploaded_file is not None:
            files = {'media': uploaded_file}
        else:
            files = {'media': open(images[choice], 'rb')}
        
        get_image_url = f"{url}/prompt_text"
        prompt_body = {"prompt": "A picture of nature" }
        requests.post(get_image_url, json=prompt_body)

        get_image_url = f"{url}/prompt_image"
        requests.post(get_image_url, files=files)

st.write("Image Generated Below")

ready = False

if ready:
    # Show output
    print("Ready")
else:
    placeholder = st.image("images/placeholder.png", caption="Placeholder Image", width=500)

