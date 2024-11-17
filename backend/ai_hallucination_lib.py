from langchain_databricks import ChatDatabricks, DatabricksEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from openai import OpenAI
from PIL import Image
from io import BytesIO
import os, math, requests

max_x = 160
max_y = 128

dalle_2_size = 256
dalle_3_size = 1024

max_val = 4096/2

def loadDotEnv():
    with open("./.env", "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

class DataBricksManager:
    def __init__(self):
        self.chat_model = model = ChatDatabricks(
                endpoint="databricks-meta-llama-3-1-70b-instruct",
                temperature=0.1,
                max_tokens=250,
        )
        self.embeddings = DatabricksEmbeddings(endpoint="databricks-bge-large-en")
        self.prompt = ChatPromptTemplate.from_template(
        """You are a chatbot designed to create stable diffusion  (image generation) prompts given the following.
            Context: {context}
            Prompt: {prompt}

            !Only return the prompt to use nothing else!
            The image itself will have a 3d perspective that will allow for fake depth perception and observation of the image from different angles.
        """)
        self.chain = self.prompt | self.chat_model
    

class DallEHandler:
    def __init__(self,stable_prompt: str,  x_replace_prop: float, y_replace_prop: float, last_image = None):
        self.openai = OpenAI()
        self.x_replace_prop = 0.2
        self.y_replace_prop = 0.2
        self.stable_prompt = stable_prompt
        self.last_image = last_image

    def png_bytes(path:str, scale:float, compress_level:int=9) -> bytes:
        #image setup
        img = Image.open(path)
        img = img.resize(size=(int(img.width*scale), int(img.height*scale)))

        with BytesIO() as buff:
            #save png file to buff
            img.save(buff, format="PNG", compress_level=compress_level)
            
            #get bytes
            buff.seek(0) 
            out = buff.read()
            
        return out #return bytes
    

    def img_bytes(self,im : Image, scale:float) -> bytes:
        #image setup
        img = im.resize(size=(int(im.width*scale), int(im.height*scale)))

        with BytesIO() as buff:
            #save png file to buff
            img.save(buff, format="PNG")
            
            #get bytes
            buff.seek(0) 
            out = buff.read()
            
        return out

    def generate_new_image(self):
        response = self.openai.images.generate(
            model = 'dall-e-3',
            prompt = self.stable_prompt,
            size=f"{dalle_3_size}x{dalle_3_size}",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        self.last_image = self.get_image(image_url)
        self.last_image = self.last_image.resize((max_x, max_y))
        return self.last_image
    

    def get_image(self, image_url):
        return Image.open(requests.get(image_url, stream=True).raw)
    


    # So we take an image of size nxm
    # We create an identical image, and copy the original image onto the new image at the offset (x,y)
    def map_onto_blank(self, original_image,x,y):
        # So we'll do some math to work out ratio between paste_x and paste_y
        x = x/2
        y = y/2
        paste_y = round(max_y * self.y_replace_prop * (y/max_val))
        paste_x = round(max_x * self.x_replace_prop * (x/max_val))
        blank_image = Image.new("RGBA", (max_x, max_y), (0, 0, 0, 0)) 
        blank_image = self.pasteImage(blank_image, original_image, paste_x, paste_y)
        blank_image.save("blank_image.png")
        return blank_image
    

    def pasteImage(self, original_image, paste_image, x, y):
        # This function pastes the paste_image onto the original_image at the x, y offset
        # It will go through the paste_image pixel by pixel and paste it onto the original_image
        # It will just ignore any pixels that are out of bounds
        x = -x
        y = -y
        max_i = min(paste_image.width, original_image.width - x)
        max_j = min(paste_image.height, original_image.height - y)
        print(f"Max i: {max_i}, Max j: {max_j}")
        print(f"X: {x}, Y: {y}")
        for i in range(0, max_i):
            for j in range(0, max_j):
                if 0 <= x + i < original_image.width and 0 <= y + j < original_image.height:
                    original_image.putpixel((x + i, y + j), paste_image.getpixel((i, j)))

        return original_image
    
    def generate_new_region(self, original_image, x,y):
        region_image = self.map_onto_blank(original_image, x,y)
        # We'll scale the image to gpt_size x gpt_size
        region_image = region_image.resize((dalle_2_size, dalle_2_size))
        response = self.openai.images.edit(
            model = 'dall-e-2',
            image = self.img_bytes(region_image,1),
            mask = self.img_bytes(region_image,1),
            prompt = self.stable_prompt,
            n = 1,
            size = f"{dalle_2_size}x{dalle_2_size}",
        )
        self.last_image = self.get_image(response.data[0].url)
        self.last_image = self.last_image.resize((max_x, max_y))
        return self.last_image
    
    def save_image(self, output_path):
        self.last_image.save(output_path)
    
    def image_to_vasd_format(self, image, image_path: str):
        with open(image_path, 'wb') as f:
            for pixel in image.getdata():
                r, g, b, _ = pixel
                f.write(bytes([r, g, b]))
                