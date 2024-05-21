from abc import ABC, abstractmethod

from openai import AzureOpenAI
from agents import Agent
import requests
from PIL import Image
from io import BytesIO
import os

class DrawAgent(Agent, ABC):
    @abstractmethod
    def draw(self, prompt):
        pass


class AzureOpenAIDalleDrawAgent(DrawAgent):
    def __init__(self):
        self.deploymentName = "Dalle3"

    def draw(self):
        # Implement the draw method for AzureOpenAIDalleDrawAgent
        pass


class ComicAgent(AzureOpenAIDalleDrawAgent):
    def __init__(self, styleDescription):
        super().__init__()
        self.comic_template = """创建一个漫画风格的插图，场景是：{scene_description}。插图应该忠实绘画出场景里发生的事情。插图的风格如下:""" + \
            styleDescription

    def draw(self, scene_description):
        prompt = self.comic_template.format(
            scene_description=scene_description)
        client = AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_SWEDEN_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_SWEDEN_OPENAI_KEY'),
            api_version="2024-02-01")
        result = client.images.generate(
            model=self.deploymentName,  # the name of your DALL-E 3 deployment
            prompt=prompt,
            n=1
        )

        return result.data[0].url

    def work(self):
        if self.nextScene:
            return self.draw(self.nextScene)
        else:
            raise Exception("Please call provideCommand first")

    def provideCommand(self, inputObj):
        self.nextScene = inputObj["scene"]


class AmericanStyleComicAgent(ComicAgent):
    def __init__(self):
        super().__init__("""
                         典型的美式漫画风格，包括以下特点：
1. **鲜艳的颜色**：使用饱和度高的色彩来增强视觉冲击力。
2. **夸张的表情**：人物的面部表情非常生动，以传达强烈的情感。
3. **动态姿势**：人物的动作和姿势具有强烈的动感，往往采用夸张的透视和角度。
4. **细节丰富的背景**：背景元素丰富且具有深度，能够补充和增强前景的故事情节。
5. **对话框和字幕**：必要情况下使用对话框来呈现人物之间的对话，字幕用于描述场景或提供额外信息。

确保插图具有明显的线条和清晰的轮廓，展现出美式漫画的经典风格。""")

    def getName(self):
        return "ComicAgent"


class ChineseStyleComicAgent(ComicAgent):
    def __init__(self):
        super().__init__("""
                         典型的中式漫画风格，包括以下特点：
1. **淡雅的颜色**：使用柔和、自然的色彩来营造画面的宁静感。
2. **细腻的表情**：人物的面部表情精致，传达出丰富而细腻的情感。
3. **优雅的姿势**：人物的动作和姿势具有古典美，讲究线条的流畅和姿态的优雅。
4. **背景元素丰富**：背景细致入微，常常包括自然风光、传统建筑和中式元素，能够增强故事的文化氛围。
5. **简洁的对话框和注释**：必要情况下使用对话框来呈现人物之间的对话，注释用于描述场景或提供额外信息。

确保插图具有柔和的线条和清晰的轮廓，展现出中式漫画的独特风格。""")

    def getName(self):
        return "ComicAgent"


if __name__ == "__main__":
    agent = ChineseStyleComicAgent()
    agent.provideCommand(
        {"scene": "一只皮卡丘在和葫芦娃里的蛇精打架，场景在一个森林里"})
    url = agent.work()

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save("./downloaded_image.png")
