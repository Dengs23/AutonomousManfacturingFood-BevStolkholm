#!/usr/bin/env python3
"""
AutoGen Studio Manufacturing Team - Terminal Execution Script
Run your automotive manufacturing agents directly from terminal
"""

import autogen
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Configuration
class ManufacturingSystem:
    def __init__(self, api_key=None, model="gpt-4"):
        """Initialize the manufacturing multi-agent system"""
        
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable")
            sys.exit(1)
        
        # LLM Configuration
        self.llm_config = {
            "config_list": [
                {
                    "model": model,
                    "api_key": self.api_key,
                    "temperature": 0.7,
                    "timeout": 120,
                }
            ],
        }
        
        # Create output directory
        self.output_dir = Path("manufacturing_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize agents
        self.agents = {}
        self.setup_agents()
        
    def setup_agents(self):
        """Create your manufacturing agents from the screenshot"""
        print("🤖 Setting up manufacturing agents...")
        
        # 1. ALERT AGENT - Monitoring and alerts
        self.agents["alert"] = autogen.AssistantAgent(
            name="AlertAgent",
            system_message="""You are the Alert Agent for an automotive manufacturing system.
            Responsibilities:
            - Monitor production metrics in real-time
            - Detect anomalies and bottlenecks
            - Generate alerts for quality issues
            - Flag maintenance requirements
            - Report safety concerns
            
            Always start your response with [ALERT] and include severity level.
            """,
            llm_config=self.llm_config,
        )
        
        # 2. ANALYZER AGENT - Data analysis
        self.agents["analyzer"] = autogen.AssistantAgent(
            name="AnalyzerAgent",
            system_message="""You are the Analyzer Agent for automotive manufacturing.
            Responsibilities:
            - Analyze production efficiency data
            - Identify patterns in quality control
            - Calculate OEE (Overall Equipment Effectiveness)
            - Perform root cause analysis
            - Generate performance reports
            
            Always start your response with [ANALYSIS] and include data-driven insights.
            """,
            llm_config=self.llm_config,
        )
        
        # 3. PRODUCTION AGENT - Workflow management
        self.agents["production"] = autogen.AssistantAgent(
            name="ProductionAgent",
            system_message="""You are the Production Agent managing manufacturing workflows.
            Responsibilities:
            - Optimize production schedules
            - Manage assembly line balance
            - Coordinate material flow
            - Implement process improvements
            - Reduce cycle times
            
            Always start your response with [PRODUCTION] and include actionable steps.
            """,
            llm_config=self.llm_config,
        )
        
        # 4. OPTIMUM AGENT - Optimization
        self.agents["optimum"] = autogen.AssistantAgent(
            name="OptimumAgent",
            system_message="""You are the Optimum Agent finding optimal manufacturing solutions.
            Responsibilities:
            - Calculate optimal machine parameters
            - Minimize waste and downtime
            - Maximize throughput
            - Optimize resource allocation
            - Recommend efficiency improvements
            
            Always start your response with [OPTIMUM] and include numerical targets.
            """,
            llm_config=self.llm_config,
        )
        
        # User proxy for execution
        self.user_proxy = autogen.UserProxyAgent(
            name="ManufacturingEngineer",
            human_input_mode="TERMINATE",  # Will ask for input at end
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
            code_execution_config={
                "work_dir": "manufacturing_output",
                "use_docker": False,
            },
            system_message="""You are the Manufacturing Engineer coordinating the team.
            Review agent outputs and make final decisions.""",
        )
        
        print("✅ Agents initialized successfully")
        
    def create_team(self, workflow_type="round_robin"):
        """Create the manufacturing team with specified workflow"""
        
        agent_list = list(self.agents.values())
        
        if workflow_type == "sequential":
            # Sequential workflow
            print("🔄 Using Sequential workflow")
            return self._create_sequential_workflow()
            
        elif workflow_type == "round_robin":
            # Round robin group chat (from your screenshot)
            print("🔄 Using Round Robin group chat")
            group_chat = autogen.GroupChat(
                agents=[self.user_proxy] + agent_list,
                messages=[],
                max_round=25,
                speaker_selection_method="round_robin",
            )
            
            return autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config,
                name="ManufacturingTeamManager"
            )
            
        else:
            # Hierarchical with manager
            print("🔄 Using Hierarchical workflow")
            group_chat = autogen.GroupChat(
                agents=[self.user_proxy] + agent_list,
                messages=[],
                max_round=30,
                speaker_selection_method="auto",
            )
            
            return autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config,
                name="ManufacturingTeamManager"
            )
    
    def _create_sequential_workflow(self):
        """Create sequential task chain"""
        async def run_sequence(task):
            result = task
            for agent_name, agent in self.agents.items():
                print(f"\n⚙️ Running {agent_name} agent...")
                response = await agent.a_generate_reply(
                    messages=[{"content": result, "role": "user"}]
                )
                result = response
            return result
        return run_sequence
    
    def run_manufacturing_task(self, task, workflow="round_robin"):
        """Execute the manufacturing task"""
        
        print("\n" + "="*60)
        print("🏭 AUTOMOTIVE MANUFACTURING SYSTEM TEAM")
        print("="*60)
        print(f"📋 Task: {task}")
        print(f"👥 Agents: Alert, Analyzer, Production, Optimum")
        print(f"⚙️ Workflow: {workflow}")
        print("="*60 + "\n")
        
        # Create team manager
        manager = self.create_team(workflow)
        
        # Save task to file
        task_file = self.output_dir / f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(task_file, 'w') as f:
            f.write(task)
        
        # Execute the chat
        try:
            self.user_proxy.initiate_chat(
                manager,
                message=task,
                clear_history=True,
            )
            
            # Save conversation
            self._save_conversation()
            
        except KeyboardInterrupt:
            print("\n⚠️ Execution interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _save_conversation(self):
        """Save chat history to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"conversation_{timestamp}.json"
        
        # Collect all messages
        messages = []
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'chat_messages'):
                messages.extend(agent.chat_messages)
        
        with open(filename, 'w') as f:
            json.dump(messages, f, indent=2, default=str)
        
        print(f"\n💾 Conversation saved to: {filename}")

def print_banner():
    """Print cool banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║     🏭 AUTOGEN STUDIO - MANUFACTURING TEAM EXECUTOR     ║
    ║         Automotive Multi-Agent System v1.0              ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main terminal execution function"""
    print_banner()
    
    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("🔑 Enter your OpenAI API key: ").strip()
    
    # Initialize system
    mfg_system = ManufacturingSystem(api_key=api_key)
    
    # Pre-defined manufacturing tasks from your domain
    manufacturing_tasks = [
        "1. 🚨 Alert: Monitor production line for anomalies in engine assembly",
        "2. 📊 Analyze: Review last 24h production data and identify bottlenecks",
        "3. ⚙️ Optimize: Reduce cycle time on door assembly line by 15%",
        "4. 🔧 Production: Schedule maintenance for robotic welding stations",
        "5. 🎯 Quality: Reduce defect rate in paint shop by 10%",
        "6. 💰 Cost: Optimize material usage in chassis production",
        "7. ⚡ Efficiency: Improve OEE score from 75% to 85%",
        "8. 📈 Custom: Enter your own manufacturing task"
    ]
    
    # Show menu
    print("\n📋 SELECT MANUFACTURING TASK:")
    print("-" * 40)
    for task in manufacturing_tasks:
        print(f"  {task}")
    
    try:
        choice = input("\n🎯 Enter task number (1-8): ").strip()
        
        if choice == "8":
            task = input("📝 Describe your manufacturing task: ").strip()
        else:
            task = manufacturing_tasks[int(choice)-1].split(". ", 1)[1]
        
        # Select workflow
        print("\n⚙️ SELECT WORKFLOW TYPE:")
        print("  1. Round Robin (Team discussion)")
        print("  2. Sequential (Step by step)")
        print("  3. Hierarchical (Manager-led)")
        
        workflow_choice = input("🎯 Enter workflow (1-3) [default: 1]: ").strip() or "1"
        
        workflow_map = {"1": "round_robin", "2": "sequential", "3": "hierarchical"}
        workflow = workflow_map.get(workflow_choice, "round_robin")
        
        # Execute
        mfg_system.run_manufacturing_task(task, workflow)
        
        print("\n✅ Manufacturing optimization complete!")
        print(f"📁 Check '{mfg_system.output_dir}' for output files")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
