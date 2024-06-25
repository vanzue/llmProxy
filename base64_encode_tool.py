import base64
from io import BytesIO
from PIL import Image
import requests

image = Image.open('./self2.jpg')
new_width = image.width // 2
new_height = image.height // 2
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
img_byte_arr = BytesIO()
resized_image.save(img_byte_arr, format='JPEG')
encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

url = "http://100.64.251.11:5000/image/reference"
response = requests.post(
    url, json={'ref': encoded_img, 'style': 'warm', 'story': 'A man walking on the street at night.'})
print(response.content)
