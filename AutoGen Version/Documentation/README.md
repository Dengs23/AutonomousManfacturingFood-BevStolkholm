# 🏭 AutoGen Manufacturing System

## Food & Beverage Production Line Multi-Agent System

### 📁 Structure
- **/Agents** - Agent definitions and bridge files
- **/Configs** - JSON configurations for agents and teams
- **/Scripts** - Main execution scripts
- **/Deployment** - Deployment and setup scripts
- **/Documentation** - Guides and documentation

### 🤖 Agents
- `alert_agent` - Sensor monitoring and anomaly detection
- `analyzer_agent` - Root cause analysis
- `production_agent` - Immediate action plans
- `optimum_agent` - Long-term optimization

### 🚀 Quick Start
```bash
# Setup
python3.12 -m venv autogen_env
source autogen_env/bin/activate
pip install pyautogen==0.2.35 autogenstudio

# Run
python Scripts/run_manufacturing_now.py
