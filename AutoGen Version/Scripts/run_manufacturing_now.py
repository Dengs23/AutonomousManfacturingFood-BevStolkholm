#!/usr/bin/env python3
import asyncio
import json
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Set your OpenAI API key here
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"  # <-- REPLACE WITH YOUR KEY

# Create model client
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Create Alert Agent
alert_agent = AssistantAgent(
    name="alert_agent",
    system_message="""You are an Alert Detection Agent for a Food & Beverage manufacturing system.
Monitor 17 sensors in real-time and detect anomalies.
Thresholds: Vibration > 0.7 = RED, Temperature > 28°C = YELLOW, Pressure > 1.1 bar = YELLOW, Vision defect > 0.2 = ORANGE.
Flag anomalies with severity levels.""",
    model_client=model_client,
)

# Create Analyzer Agent
analyzer_agent = AssistantAgent(
    name="analyzer_agent",
    system_message="""You are a Root Cause Analyzer Agent.
Investigate alerts to determine: 1) Root cause, 2) Failure probability, 3) Production impact.
Common causes: bearing wear, lubrication deficiency, misalignment, electrical fluctuation.""",
    model_client=model_client,
)

# Create Production Agent
production_agent = AssistantAgent(
    name="production_agent",
    system_message="""You are a Production Line Manager Agent.
Provide immediate action plans: line speed adjustments, temperature control, pressure regulation, 
quality check frequency, vibration dampening. Maintain production with minimal disruption.""",
    model_client=model_client,
)

# Create Optimum Agent
optimum_agent = AssistantAgent(
    name="optimum_agent",
    system_message="""You are an Optimization Solution Agent.
Provide long-term solutions: maintenance scheduling, equipment upgrades, process improvements,
predictive maintenance, ROI calculations, spare parts planning. Include timelines and benefits.""",
    model_client=model_client,
)

# Create the team
team = RoundRobinGroupChat([alert_agent, analyzer_agent, production_agent, optimum_agent])

# Run the team
async def main():
    await Console(team.run_stream(
        task="ALERT: Temperature sensor #12 showing 5°C deviation in fermentation tank! Investigate root cause, adjust production, and provide optimization solution."
    ))

if __name__ == "__main__":
    asyncio.run(main())
