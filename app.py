import json
import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import logging

from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, CharacterDrawer, ChineseStyleComicAgent, getStyle
from image_storage_util import compress_and_upload
from multi_modal_query import DescribeCharacter
from storyToComics import generate_comics
import uuid
from threading import Thread
from table_access import JobStatusDataAccess, UserDataAccess

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

APP_ID = os.getenv('WECHAT_APPID')
APP_SECRET = os.getenv('WECHAT_SECRET')

DALLE_ENDPOINT = f"{AZURE_ENDPOINT_DALLE}/openai/deployments/{DEPLOYMENT_MODEL_DALLE}/images/generations?api-version={API_VERSION_DALLE}"
GPT35_ENDPOINT = f"{AZURE_ENDPOINT_GPT35}/openai/deployments/{DEPLOYMENT_MODEL_GPT35}/chat/completions?api-version={API_VERSION_GPT35}"

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
    return jsonify({'message': 'haha'})


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


def generate_comics_task(partition_key, job_id, style, shortStory, n):
    try:
        # Simulate generate_comics function
        url = generate_comics(style, shortStory, n)
        result = json.dumps([url])
        # Update job status to Success
        with JobStatusDataAccess() as data_access:
            data_access.update(partition_key, job_id, job_id, 'Success' if url else 'Failed', "",
                               result)
    except Exception as e:
        # Update job status to Failed
        with JobStatusDataAccess() as data_access:
            data_access.update(partition_key, job_id,
                               job_id, 'Failed', '', str(e))


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
        job_id = str(uuid.uuid4())
        partition_key = "ComicsGeneration"

        # Add job entity with status Pending
        with JobStatusDataAccess() as data_access:
            data_access.add(partition_key, job_id,
                            job_id, 'Pending', '[]', '[]')

        # Run the task in a separate thread
        thread = Thread(target=generate_comics_task, args=(
            partition_key, job_id, style, shortStory, n))
        thread.start()

        # Return job ID to frontend
        return jsonify({'jobId': job_id})

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
        story_agent.provideCommand(
            {"description": f"主题：{shortStory}，创作几幅漫画：{n}"})
        long_story = story_agent.work()

        print("stories generated done.")
        print("Stories", long_story)
        # Split the long story into n individual stories
        stories = long_story['output'].split('\n\n')[:n]
        print("Stories", stories)
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
        if style != 'american' and style != 'chinese':
            raise ValueError(
                'Invalid style. Please choose "american" or "chinese"')

        comic_agent = AmericanStyleComicAgent(
        ) if style == 'american' else ChineseStyleComicAgent()

        # Provide command to StoryWritingAgent to generate n stories
        comic_agent.provideCommand({"scene": story})
        url = comic_agent.work()
        return url
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


@app.route('/job/status/<job_id>', methods=['GET'])
@authenticate
def get_job_status(job_id):
    try:
        partition_key = "ComicsGeneration"
        with JobStatusDataAccess() as data_access:
            job_status = data_access.get(partition_key, job_id)
            return jsonify(job_status)
    except Exception as e:
        print(f"Error retrieving job status for jobId {job_id}: {str(e)}")
        return jsonify({'message': 'Error retrieving job status', 'details': str(e)}), 500


@app.route('/image/describe', methods=['POST'])
@authenticate
def describe_image():
    try:
        data = request.json
        image = data['data']
        return DescribeCharacter(image)
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


# reference a image
@app.route('/image/reference', methods=['POST'])
def referenceImage():
    try:
        data = request.json
        image = data['ref']
        style = data['style']
        story = data['story']
        character = DescribeCharacter(image)
        style_description = getStyle(style)
        comic_agent = CharacterDrawer(style_description)
        url = comic_agent.draw(story, character)
        compressed_url = compress_and_upload(url)
        return jsonify([compressed_url, url])
    
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


@app.route('/image/create/character', methods=['POST'])
def createCharacterComic():
    try:
        data = request.json
        description = data['description']
        style = data['style']
        story = data['story']
        style_description = getStyle(style)
        comic_agent = CharacterDrawer(style_description)
        url = comic_agent.draw(story, description)
        compressed_url = compress_and_upload(url)
        return jsonify([compressed_url, url])
        
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500

def generate_session_token():
    return str(uuid.uuid4())

# add or update an existing user session
def save_session(session_token, openid):
    with UserDataAccess() as userDataAccess:
        try:
            existingUser = userDataAccess.get(openid, openid)
        except:
            existingUser = None
        if not existingUser:
            userDataAccess.add(openid, openid, session_token, "False", "", "", "")
            return {
                'session_token': session_token,
            }
        else:
            userDataAccess.update(openid, openid, session_token, "False", "", "", "")
            return {
                'session_token': session_token,
                'profile_done': existingUser['ProfileDone'],
                'user_description': existingUser['UserDescription'],
                'seed': existingUser['Seed'],
                'style': existingUser['Style']
            }

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    code = data.get('code')

    if not code:
        return jsonify({'error': 'missing code'}), 400

    try:
        response = requests.get('https://api.weixin.qq.com/sns/jscode2session', params={
            'appid': APP_ID,
            'secret': APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        })

        response_data = response.json()

        if 'errcode' in response_data:
            return jsonify(response_data), 400

        session_token = generate_session_token()
        user = save_session(session_token, response_data.get('openid'))
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    code = data.get('code')

    if not code:
        return jsonify({'error': 'missing code'}), 400

    try:
        response = requests.get('https://api.weixin.qq.com/sns/jscode2session', params={
            'appid': APP_ID,
            'secret': APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        })

        response_data = response.json()

        if 'errcode' in response_data:
            return jsonify(response_data), 400

        session_token = generate_session_token()
        user = save_session(session_token, response_data.get('openid'))
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host="localhost", port=PORT)
