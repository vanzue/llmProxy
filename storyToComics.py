from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent
import requests
from io import BytesIO


def generate_comics(style, shortStory, n):
    # Initialize the StoryWritingAgent
    story_agent = StoryWritingAgent()

    # Provide command to StoryWritingAgent to generate n stories
    story_agent.provideCommand({"description": f"主题：{shortStory}，创作几幅漫画：{n}"})
    long_story = story_agent.work()

    print("stories generated done.")
    # Split the long story into n individual stories
    stories = long_story['output'].split('\n\n')[:n]

    # Initialize the appropriate comic agent based on the style
    if style.lower() == 'chinese':
        comic_agent = ChineseStyleComicAgent()
    elif style.lower() == 'american':
        comic_agent = AmericanStyleComicAgent()
    else:
        raise ValueError(
            "Invalid style. Please choose 'chinese' or 'american'.")

    # Create comics and collect the URLs
    comic_urls = []
    for story in stories:
        comic_agent.provideCommand({"scene": story})
        url = comic_agent.work()
        comic_urls.append(url)
        print(f"Comic generated: {url}")

    return comic_urls
