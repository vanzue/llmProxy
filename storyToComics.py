from agents import StoryWritingAgent
from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent

def generate_comics(style, shortStory, n):
    try:
        # Initialize the StoryWritingAgent
        story_agent = StoryWritingAgent()

        # Provide command to StoryWritingAgent to generate n stories
        story_agent.provideCommand({"description": f"主题：{shortStory}，创作几幅漫画：{n}"})
        long_story = story_agent.work()

        print("stories generated done.")
        print("Stories", long_story);
        # Split the long story into n individual stories
        stories = long_story['output'].split('\n\n')[:n]
        print("Stories", stories);

        # Initialize the appropriate comic agent based on the style
        if style.lower() == 'chinese':
            comic_agent = ChineseStyleComicAgent()
        elif style.lower() == 'american':
            comic_agent = AmericanStyleComicAgent()
        else:
            print("Invalid style. Please choose 'chinese' or 'american");
            raise ValueError(
                "Invalid style. Please choose 'chinese' or 'american'.")

        # Create comics and collect the URLs
        comic_urls = []
        for story in stories:
            comic_agent.provideCommand({"scene": story})
            print("provided command")
            url = comic_agent.work()
            print("url", url)
            comic_urls.append(url)
            print(f"Comic generated: {url}")
    except Exception as e:
        print(f"Error: {e.message}")
        comic_urls = []

    return comic_urls
