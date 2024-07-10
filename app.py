import base64
import json
import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import logging

from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, CharacterDrawer, ChineseStyleComicAgent, getStyle
from image_storage_util import compress_and_upload, upload_jpg_to_blob
from multi_modal_query import DescribeCharacter
from storyToComics import generate_comics
import uuid
from threading import Thread
from table_access import CollectionDataAccess, JobStatusDataAccess, SessionDataAccess, UserDataAccess, get_openid_by_session, get_session_by_openid, getUserProfile
import secrets

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


# create a new character comic
# ret:
#   @compressed_url: the compressed url of the comic
#   @url: the url of the comic
#   @character: the character description
#   @style: the style description
#   @seed: the seed used to generate the comic
@app.route('/image/new/comic', methods=['POST'])
# @authenticate
# Authenticate with user session key, for now ignore.
def buildComicProfile():
    try:
        data = request.json
        session_token = data['session_token']
        if not session_token:
            return jsonify({'message': 'Missing session token'}), 400

        photo_url = data['photo_url']
        if not photo_url:
            return jsonify({'message': 'Missing photo url'}), 400

        # we should use sessoin token to obtain the
        openid = get_openid_by_session(session_token)
        character = DescribeCharacter(photo_url)
        style_description = getStyle('warm')
        comic_agent = CharacterDrawer(style_description)
        seed_number = secrets.randbelow(2**32)
        seed_string = str(seed_number)

        url = comic_agent.drawPortrait(character, seed_string)
        compressed_url = compress_and_upload(url)

        return jsonify({
            'compressed_url': compressed_url,
            'url': url,
            'character': character,
            'style': style_description,
            'seed': seed_string,
        })

    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


@app.route('/image/determine', methods=['POST'])
def determineComicMetaData():
    try:
        data = request.json
        session_token = data['session_token']
        if not session_token:
            return jsonify({'message': 'Missing session token'}), 400

        openid = get_openid_by_session(session_token)
        if not openid:
            return jsonify({'message': 'Invalid session token'}), 400

        with UserDataAccess() as data_access:
            data_access.upsert(openid, openid, True, data['character'],
                               data['seed'], data['style'])

        return jsonify({'message': 'Comic meta data updated successfully'})
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


# Check this api to determine whether user is going to go through
# profile setup process.
@app.route('/image/status', methods=['POST'])
def CheckUserStatus():
    try:
        data = request.json
        # if user has session_token, then it means he has onboarded the system,
        # while he could quit the profile set up progress, so user profile could be
        # not complete.
        session_token = data['session_token']
        if not session_token:
            return jsonify({'message': 'Missing session token'}), 400

        openid = get_openid_by_session(session_token)
        if not openid:
            return jsonify({'message': 'Invalid session token'}), 400

        with UserDataAccess() as data_access:
            user = data_access.get(openid, openid)
        return jsonify(user)
    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


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
        # we should store the description and style here also the seed, so that next time,
        # it will be easier to generate the similar comics once again.
        return jsonify([compressed_url, url])

    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


@app.route('/image/character/story', methods=['POST'])
def createCharacterComic():
    try:
        data = request.json
        description = data['description']
        style = data['style']
        story = data['story']
        seed = data['seed']
        style_description = getStyle(style)
        comic_agent = CharacterDrawer(style_description)
        url = comic_agent.drawSeed(story, description, seed)
        compressed_url = compress_and_upload(url)
        return jsonify({
            "compressed_url": compressed_url,
            "url": url
        })

    except Exception as e:
        print("error when generating comics:", e.message)
        return jsonify({'message': 'Error generating comics', 'details': str(e)}), 500


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
        open_id = response_data.get('openid')
        existing_session = get_session_by_openid(open_id)
        if existing_session:
            return jsonify({'session_token': existing_session})
        new_session = new_session()
        return jsonify({
            'session_token': new_session
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image/upload', methods=['POST'])
def upload():
    data = request.json
    content = data.get('content')

    try:
        data = base64.b64decode(content)
        url = upload_jpg_to_blob(data)
        return url

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List all collections of a user
# @param session_token: user session token


@app.route('/collection/list/<session_token>', methods=['GET'])
def listCollection(session_token):
    openid = get_openid_by_session(session_token)

    try:
        with CollectionDataAccess() as data_access:
            collections = data_access.getCollections(openid)
            return jsonify(collections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a comic to a collection
# @param session_token: user session token
# @param collection_name: collection name
# @param compressed_url: compressed image url
# @param url: original image url


@app.route('/collection/add', methods=['POST'])
def addToCollection():
    data = request.json()
    session_token = data.get('session_token')
    collection_name = data.get('collection_name')
    compressed_url = data.get('compressed_url')
    url = data.get('url')

    openid = get_openid_by_session(session_token)

    try:
        with CollectionDataAccess() as data_access:
            data_access.addComicToCollection(
                openid, collection_name, compressed_url, url)
            return jsonify({
                'result': True
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# param @session_token: user session token
# param @collection_name: collection name
# param @compressed_urls: compressed image url list [json list]
# param @urls: original image url list              [json list]


@app.route('/collection/update', methods=['POST'])
def updateComicInCollection():
    data = request.json()
    session_token = data.get('session_token')
    collection_name = data.get('collection_name')
    compressed_url = data.get('compressed_urls')
    url = data.get('urls')

    openid = get_openid_by_session(session_token)

    try:
        with CollectionDataAccess() as data_access:
            data_access.addComicToCollection(
                openid, collection_name, compressed_url, url)
            return jsonify({
                'result': True
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=PORT)
