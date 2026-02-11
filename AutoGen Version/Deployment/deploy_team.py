import asyncio
import json
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # REPLACE THIS

# Load team configuration
with open('manufacturing_agents.json', 'r') as f:
    team_config = json.load(f)

print("🍺 DEPLOYING Food & Beverage Manufacturing Team...")
print("="*50)
print(f"🤖 Agents: {', '.join([a['name'] for a in team_config['agents']])}")
print(f"📋 Workflow: {team_config['workflows'][0]['description']}")
print(f"🎯 Model: GPT-4o Mini")
print("="*50)

# Configure LLM
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0.1
        }
    ]
}

# Create agents
agents = {}
for agent_config in team_config['agents']:
    agent = AssistantAgent(
        name=agent_config['name'],
        system_message=agent_config['config']['system_message'],
        llm_config=llm_config
    )
    agents[agent_config['name']] = agent
    print(f"✅ Created: {agent_config['name']}")

# Create user proxy
user_proxy = UserProxyAgent(
    name="ManufacturingEngineer",
    human_input_mode="TERMINATE",
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", "")
)

# Create group chat
workflow = team_config['workflows'][0]
agent_list = [agents[name] for name in workflow['agents']]

group_chat = GroupChat(
    agents=[user_proxy] + agent_list,
    messages=[],
    max_round=workflow['max_turns']
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

# Run the team
task = "ALERT: Temperature sensor #12 showing 5°C deviation in fermentation tank. Investigate root cause, adjust production, and provide optimization solution."
user_proxy.initiate_chat(manager, message=task)
