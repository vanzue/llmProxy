
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider, InteractiveBrowserCredential
from dotenv import load_dotenv
from agent_prompt import confuciusAgentPrompt, luoXiangAgentPrompt, superIntelligentAgentPrompt, storytellingAgentPrompt
from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def provideCommand(self, inputObj):
        pass

    @abstractmethod
    def getName(self):
        pass


class ChatClientAgent(Agent):
    def __init__(self):
        self.messages = []

    def appendSystemMessage(self, message):
        self.messages.append({"role": "assistant", "content": message})

    def appendUserMessage(self, message):
        self.messages.append({"role": "user", "content": message})

    def getMessages(self):
        return self.messages

    @abstractmethod
    def talk(self):
        pass

# this agent is used for chat with Azure OpenAI.


class AzureOpenAIClientChatAgent(ChatClientAgent):
    def __init__(self, system_prompt):
        load_dotenv()

        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        deployment = os.environ["CHAT_COMPLETIONS_DEPLOYMENT_NAME"]

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2024-02-01",
        )

        self.model = deployment
        self.messages = system_prompt

    def talk(self):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        response = completion.choices[0].message.content
        self.appendSystemMessage(response)
        return response

    # a universal entry point all agents. if particular interested in
    # chat functionality, call talk is enough.
    @abstractmethod
    def work(self):
        pass


class ConfuciousChatAgent(AzureOpenAIClientChatAgent):
    def __init__(self):
        super().__init__(confuciusAgentPrompt)

    def work(self):
        try:
            output = self.talk()
            return {"output": output}
        except Exception as e:
            return {"output": "A oo... Confucious went to sleep..."}

    def getName(self):
        return "Confucious"


class LuoXiangChatAgent(AzureOpenAIClientChatAgent):
    def __init__(self):
        super().__init__(luoXiangAgentPrompt)

    def work(self):
        try:
            output = self.talk()
            return {"output": output}
        except Exception as e:
            return {"output": "A oo... Luoxiang went to lunch..."}

    def getName(self):
        return "Luo Xiang"


class SuperIntelligentAgent(AzureOpenAIClientChatAgent):
    def __init__(self):
        super().__init__(superIntelligentAgentPrompt)

    def work(self):
        try:
            output = self.talk()
            return {"output": output}
        except Exception as e:
            return {"output": "A oo... SuperIntelligent don't want to talk..."}

    def getName(self):
        return "Super Intelligent Agent"


class StoryWritingAgent(AzureOpenAIClientChatAgent):
    def __init__(self):
        super().__init__(storytellingAgentPrompt)

    def work(self):
        try:
            output = self.talk()
            return {"output": output}
        except Exception as e:
            return {"output": "A oo... Storytelling agent is on vacation..."}

    def getName(self):
        return "Storytelling Agent"

    def provideCommand(self, inputObj):
        self.messages.append(
            {"role": "user", "content": inputObj["description"]})


if __name__ == "__main__":
    agent = StoryWritingAgent()
    agent.provideCommand({"description": "主题：小区居民楼电动车严禁上楼，创作几幅漫画：4"})
    print(agent.work())
