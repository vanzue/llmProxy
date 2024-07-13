import requests
import os
from azure.storage.blob import BlobServiceClient
import uuid
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

container_name = "comics"
connection_string = os.environ['AZURE_IMAGE_STORAGE_ACCOUNT_CONNECTION_STRING']


def upload_to_blob(local_file_name, upload_file_path):
    # Connection string obtained from the Azure portal
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string)

    # Get a client for the blob
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=local_file_name)

    # Upload the file
    with open(upload_file_path + local_file_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url


def upload_jpg_to_blob(data):
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string)
    uuid_string = str(uuid.uuid4())[:16] + '.jpg'
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=uuid_string)
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url


def compress_and_upload(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        resized_image = image.resize(
            (image.width//2, image.height//2), Image.LANCZOS)
        buffer = BytesIO()
        resized_image.save(buffer, format="JPEG", quality=50)
        buffer.seek(0)
        return upload_jpg_to_blob(buffer)
    else:
        raise Exception(
            f"Failed to retrieve image. Status code: {response.status_code}")


def copy_and_upload(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        return upload_jpg_to_blob(buffer)
    else:
        raise Exception(
            f"Failed to retrieve image. Status code: {response.status_code}")


if __name__ == "__main__":
    print(copy_and_upload(
        "https://dalleprodsec.blob.core.windows.net/private/images/d48235ba-75b4-4ab3-adb0-14f2d21a4f18/generated_00.png?se=2024-07-14T13%3A18%3A36Z&sig=PD2o7nompi8nQH6tIoaGcQrY5DndeHqQfmMG%2B0OQnhg%3D&ske=2024-07-20T08%3A04%3A01Z&skoid=e52d5ed7-0657-4f62-bc12-7e5dbb260a96&sks=b&skt=2024-07-13T08%3A04%3A01Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"))
