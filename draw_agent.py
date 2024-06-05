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
        self.comic_template = """创建一个漫画风格的插图，场景是：\"{scene_description}\"。生成**{number}**格漫画你用于生成图片的提示词构造方案如下：  
[风格]+ [格数]+[基本信息]+[文本]-identifer+1首先请通过以下步骤来获取信息。 --规则-- [1].每张图片等比，严格按照格数生成。[2].图片对话内容为英文，每条对话不超过10个词。[3].漫画分镜要多变、流畅，如画面的局部、全局，人物的不同角度，保持画面节奏、刻画重点场景。
[4].适当在周围加一些漫画字符，使其更加丰富。[5].Identifer部分：0001,0002,0003,0004。请根据个数来决定Identifer的值。比如1格漫画，Identifer为0001，2格漫画，Identifer为0001,0002。风格如下：""" + \
            styleDescription

    def draw(self, scene_description, n):
        prompt = self.comic_template.format(
            scene_description=scene_description, number=n)
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
            return self.draw(self.nextScene, self.n)
        else:
            raise Exception("Please call provideCommand first")

    def provideCommand(self, inputObj):
        self.nextScene = inputObj["scene"]
        self.n = inputObj["n"]


class AmericanStyleComicAgent(ComicAgent):
    def __init__(self):
        super().__init__("""1.**视觉冲击力强**：使用清晰的线条和鲜艳的色彩，增强画面的吸引力。2.**现代波普艺术风格**：融合点状网格和粗黑边框，展示波普艺术的现代感。3.**对比鲜明的色彩**：采用红色、黄色、黑色和白色等色彩，增强视觉层次感。4.**夸张的表情和动作**：人物表情和动作夸张，有效强化情感表达。5.**手绘线条**：人物轮廓和细节通过粗犷的手绘线条展现，增加自然和艺术感。""")
    def getName(self):
        return "ComicAgent"


class ChineseStyleComicAgent(ComicAgent):
    def __init__(self):
        super().__init__("""1. **淡雅的颜色**：使用柔和、自然的色彩来营造画面的宁静感。 2. **细腻的表情**：人物的面部表情精致，传达出丰富而细腻的情感。 3. **优雅的姿势**：人物的动作和姿势具有古典美，讲究线条的流畅和姿态的优雅。 4. **背景元素丰富**：背景细致入微，常常包括自然风光、传统建筑和中式元素，能够增强故事的文化氛围。 5. **简洁的对话框和注释**：必要情况下使用对话框来呈现人物之间的对话，注释用于描述场景或提供额外信息。 """)

    def getName(self):
        return "ComicAgent"
    
class KoreanStyleComicAgent(ComicAgent):
    def __init__(self):
        super().__init__("""1. **细致优美的线条艺术**：线条流畅且精准。   2. **漂亮且富有表现力的人物形象**：拥有大而传神的眼睛。 3. **丰富的面部表情**：生动地传达情感。  4. **动态的动作场景**：带有强烈的运动线和戏剧效果。   5. **优雅现代的背景细节**：拥有现代感美学。""")

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
