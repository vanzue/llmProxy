from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent
import requests
from PIL import Image
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


if __name__ == "__main__":
    # Example usage
    style = 'chinese'
    shortStory = '早上，一只小猫在花园里追逐一只蝴蝶。后来，它遇到了一只大狗。'
    n = 4
    comic_urls = generate_comics(style, shortStory, n)
    for i, url in enumerate(comic_urls):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.save(f"./downloaded_image{i}.png")
