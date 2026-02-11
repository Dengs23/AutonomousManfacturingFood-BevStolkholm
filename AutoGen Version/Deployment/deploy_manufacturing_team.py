# deploy_manufacturing_team.py - CORRECTED VERSION
import asyncio
import json
import os
from autogenstudio import TeamManager

# Load your team configuration
with open('manufacturing_agents.json', 'r') as f:
    team_config = json.load(f)

print("🍺 DEPLOYING Food & Beverage Manufacturing Team...")
print("="*50)
print(f"🤖 Agents: {', '.join([a['name'] for a in team_config['agents']])}")
print(f"📋 Workflow: {team_config['workflows'][0]['description']}")
print(f"🎯 Model: GPT-4o Mini")
print("="*50)

async def deploy_manufacturing_system():
    # Initialize manager
    manager = TeamManager()
    
    # TRY THESE DIFFERENT METHODS (one should work):
    
    # Method 1: create_team (most common)
    team = manager.create_team(team_config)
    
    # OR Method 2: add_team
    # team = manager.add_team(team_config)
    
    # OR Method 3: from_config
    # team = TeamManager.from_config(team_config)
    
    # Execute your manufacturing task
    result = await team.run(
        task="ALERT: Temperature sensor #12 showing 5°C deviation in fermentation tank. Investigate root cause, adjust production, and provide optimization solution.",
        user_id="manufacturing_engineer",
        session_id="production_shift_1"
    )
    
    print("\n✅ Manufacturing System Execution Complete!")
    return result

# Run the deployment
if __name__ == "__main__":
    result = asyncio.run(deploy_manufacturing_system())
    print(result)
    
    
    
