from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent


def generate_comics(style, shortStory, n):
    # Initialize the StoryWritingAgent
    story_agent = StoryWritingAgent()

    # Provide command to StoryWritingAgent to generate n stories
    story_agent.provideCommand(
        {"description": f"[topic]:{shortStory}，[number_of_comics]：{n}"})
    long_story = story_agent.work()

    print("stories generated done.")
    print("Stories", long_story)
    # Split the long story into n individual stories
    stories = long_story['output'].split('<eos>')[:n]
    if len(stories) < n:
        raise ValueError("Not enough stories generated.")
    print("Stories", stories)

    # Initialize the appropriate comic agent based on the style
    if style.lower() == 'chinese':
        comic_agent = ChineseStyleComicAgent()
    elif style.lower() == 'american':
        comic_agent = AmericanStyleComicAgent()
    else:
        print("Invalid style. Please choose 'chinese' or 'american")
        raise ValueError(
            "Invalid style. Please choose 'chinese' or 'american'.")

    # Create comics and collect the URLs
    comic_urls = []
    for story in stories:
        comic_agent.provideCommand({"scene": story.strip()})
        print("provided command")
        url = comic_agent.work()
        print("url", url)
        comic_urls.append(url)
        print(f"Comic generated: {url}")

    return comic_urls
