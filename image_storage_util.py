from azure.storage.blob import BlobServiceClient
import uuid
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
import os
import requests

container_name = "comics"
connection_string = os.environ['AZURE_IMAGE_STORAGE_ACCOUNT_CONNECTION_STRING']

def upload_to_blob(local_file_name, upload_file_path):
    # Connection string obtained from the Azure portal
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a client for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    # Upload the file
    with open(upload_file_path + local_file_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url
    
def upload_jpg_to_blob(data):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    uuid_string = str(uuid.uuid4())[:16]+ '.jpg'
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=uuid_string)
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

def compress_and_upload(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        resized_image = image.resize((image.width//3, image.height//3), Image.LANCZOS)
        buffer = BytesIO()
        resized_image.save(buffer, format="JPEG", quality=50)
        buffer.seek(0)
        return upload_jpg_to_blob(buffer)
    else:
        raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")

if __name__ == "__main__":
    print(compress_and_upload("https://comicstorage.blob.core.windows.net/comics/self2.jpg"))