import streamlit as st



# Title of the app
st.title('Simple Streamlit App')

col1, col2, col3 = st.columns(3)

# Images
with col1:
    image_1 = st.image("images/base_image_1.png", caption="Image 1", width=200)

with col2:
    image_2 = st.image("images/base_image_2.jpg", caption="Image 2", width=200)

with col3:
    image_3 = st.image("images/base_image_3.jpg", caption="Image 3", width=200)

# Choose base image
choice = st.radio("What image do you want to choose as a base?", ["Image 1", "Image 2", "Image 3"])

send_button = st.button("Send image button", type="primary")

if send_button:
    print(f"Image chosen: {choice}")
    print("Send image to api server")

st.write("Image Generated Below")

ready = False

if ready:
    # Show output
    print("Ready")
else:
    placeholder = st.image("images/placeholder.png", caption="Placeholder Image", width=500)

