import json
import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import logging

from agents import StoryWritingAgent
from azure_openai import AzureOpenAIClientSingleton
from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent
from storyToComics import generate_comics

load_dotenv()

app = Flask(__name__)

PORT = int(os.getenv('PORT', 5000))
SERVICE_KEY = os.getenv('SERVICE_KEY')

AZURE_ENDPOINT_DALLE = os.getenv('AZURE_ENDPOINT_DALLE')
DEPLOYMENT_MODEL_DALLE = "Dalle3"
API_VERSION_DALLE = "2024-02-01"
AZURE_API_KEY_DALLE = os.getenv('AZURE_API_KEY_DALLE')

AZURE_ENDPOINT_GPT35 = os.getenv('AZURE_ENDPOINT_GPT35')
DEPLOYMENT_MODEL_GPT35 = "35turbojapan"
API_VERSION_GPT35 = "2024-02-15-preview"
AZURE_API_KEY_GPT35 = os.getenv('AZURE_API_KEY_GPT35')

AZURE_ENDPOINT_GPT4 = os.getenv('AZURE_ENDPOINT_GPT4')
AZURE_API_KEY_GPT4 = os.getenv('AZURE_API_KEY_GPT4')

DALLE_ENDPOINT = f"{AZURE_ENDPOINT_DALLE}/openai/deployments/{DEPLOYMENT_MODEL_DALLE}/images/generations?api-version={API_VERSION_DALLE}"
GPT35_ENDPOINT = f"{AZURE_ENDPOINT_GPT35}/openai/deployments/{DEPLOYMENT_MODEL_GPT35}/chat/completions?api-version={API_VERSION_GPT35}"

with app.app_context():
    endpoint = os.getenv('AZURE_SWEDEN_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_SWEDEN_OPENAI_KEY')
    AzureOpenAIClientSingleton(api_key = api_key, endpoint = endpoint)

def authenticate(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != SERVICE_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})


@app.route('/dalle', methods=['POST'])
@authenticate
def dalle():
    try:
        response = requests.post(DALLE_ENDPOINT, json=request.json, headers={
            'api-key': AZURE_API_KEY_DALLE,
            'Content-Type': 'application/json'
        })
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'message': 'Error communicating with DALL-E service', 'details': str(e)}), 500


@app.route('/gpt35', methods=['POST'])
@authenticate
def gpt35():
    try:
        response = requests.post(GPT35_ENDPOINT, json=request.json, headers={
            'api-key': AZURE_API_KEY_GPT35,
            'Content-Type': 'application/json'
        })
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'message': 'Error communicating with GPT35 service', 'details': str(e)}), 500


@app.route('/generate/scenes', methods=['POST'])
@authenticate
def generate_scenes():
    try:
        deployment_model = "kaigpt4"
        api_version = "2024-02-15-preview"
        endpoint = f"{AZURE_ENDPOINT_GPT4}/openai/deployments/{deployment_model}/chat/completions?api-version={api_version}"

        chat_result = requests.post(endpoint, json=request.json, headers={
            'api-key': AZURE_API_KEY_GPT4,
            'Content-Type': 'application/json'
        })
        stories = chat_result.json().get(
            'choices')[0].get('message').get('content')
        clean_json_string = stories.replace(
            "```json\n", "").replace("\n```", "").strip()
        scenes = json.loads(clean_json_string)
        return jsonify(scenes)
    except requests.RequestException as e:
        return jsonify({'message': 'Error communicating with GPT4 service', 'details': str(e)}), 500
    except ValueError as e:
        return jsonify({'message': 'Error parsing response', 'details': str(e)}), 500


@app.route('/generate/comics', methods=['POST'])
@authenticate
def generate_comics_endpoint():
    try:
        print("generating comics.")
        data = request.json
        style = data['style']
        shortStory = data['shortStory']
        n = data['n']
        print(f"Style: {style}, Short Story: {shortStory}, n: {n}")
        comics = generate_comics(style, shortStory, n)
        print('Comics generated successfully')
        return jsonify(comics)
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500

@app.route('/generate/stories', methods=['POST'])
@authenticate
def generate_stories_endpoint():
    try:
        print("generating comics.")
        data = request.json
        shortStory = data['shortStory']
        n = data['n']
        story_agent = StoryWritingAgent()

        # Provide command to StoryWritingAgent to generate n stories
        story_agent.provideCommand({"description": f"主题：{shortStory}，创作几幅漫画：{n}"})
        long_story = story_agent.work()

        print("stories generated done.")
        print("Stories", long_story);
        # Split the long story into n individual stories
        stories = long_story['output'].split('\n\n')[:n]
        print("Stories", stories);
        return jsonify(stories)
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating stories', 'details': str(e)}), 500

@app.route('/generate/single_comic', methods=['POST'])
@authenticate
def generate_comic_endpoint():
    try:
        data = request.json
        story = data['story']
        style = data['style']
        if style!='american' and style!='chinese':
            raise ValueError('Invalid style. Please choose "american" or "chinese"')
        
        comic_agent = AmericanStyleComicAgent() if style=='american' else ChineseStyleComicAgent()

        # Provide command to StoryWritingAgent to generate n stories
        comic_agent.provideCommand({"scene": story})
        url = comic_agent.work()
        return url
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=PORT)
