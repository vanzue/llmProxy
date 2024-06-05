from draw_agent import AmericanStyleComicAgent, ChineseStyleComicAgent, KoreanStyleComicAgent

def generate_comics(style, shortStory, n):
    if style.lower() == 'chinese':
        comic_agent = ChineseStyleComicAgent()
    elif style.lower() == 'american':
        comic_agent = AmericanStyleComicAgent()
    else:
        comic_agent = KoreanStyleComicAgent()

    comic_urls = []
    comic_agent.provideCommand({"scene": shortStory.strip(), "n":n})
    print("provided command")
    url = comic_agent.work()
    print("url", url)
    comic_urls.append(url)
    print(f"Comic generated: {url}")

    return url
