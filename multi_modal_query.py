import os
from abc import abstractmethod
import base64
from openai import AzureOpenAI
from agents import ChatClientAgent
from dotenv import load_dotenv

load_dotenv()


# run query with an base64 encoded image.

def DescribeCharacter(image):
    client = AzureOpenAI(
        azure_endpoint=os.getenv('AZURE_SOUTH_CENTRAL_US_ENDPOINT'),
        api_key=os.getenv('AZURE_SOUTH_CENTRAL_US_KEY'),
        api_version="2024-02-01"
    )

    url = image

    def is_url(string):
        return string.startswith(('http://', 'https://'))

    if not is_url(image):
        url = f"data:image/jpeg;base64,{image}"

    result = client.chat.completions.create(
        model="gpt4o",
        messages=[
            {
              "role": "user",
              "content": [
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": url
                      }
                  },
                  {
                      "type": "text",
                      "text": "Describe the character in the image, do not describe background, do describe hair cut, hair color, eye, nose, mouth, shape of face, clothes, only use keyword, use comma to separate characteristics."
                  }
              ]
            },
        ]
    )

    return result.choices[0].message.content


if __name__ == "__main__":
    with open("./self2.jpg", "rb") as image:
        image_base64_encoded = base64.b64encode(image.read())
        print(DescribeCharacter(image_base64_encoded))
