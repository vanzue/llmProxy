from agents import ConfuciousChatAgent, LuoXiangChatAgent, SuperIntelligentAgent

def chatroom(topic):
    confucius_agent = ConfuciousChatAgent()
    luoxiang_agent = LuoXiangChatAgent()
    super_intelligent_agent = SuperIntelligentAgent()

    agents = [confucius_agent, luoxiang_agent, super_intelligent_agent]
    
    # Initialize the conversation with the topic
    for agent in agents:
        agent.appendUserMessage(topic)

    for round in range(5):
        for _, agent in enumerate(agents):
            output = agent.work()
            response = output["output"]
            print(f"Round {round + 1}, {agent.getName()}: {response}")

            # Append the response to all agents' message lists
            for other_agent in agents:
                if other_agent != agent:
                    other_agent.appendUserMessage(response)

if __name__ == "__main__":
    topic = "在现代生活中，个人的努力似乎没有什么价值。大家都是社会的牺牲品。"
    chatroom(topic)