# Smart Debugging Agent — Client App

A user-facing debugging assistant that helps developers diagnose code issues through a browser interface.

## What It Does
git clone https://github.com/USERNAME/smart-debugging-agent-client.git
cd smart-debugging-agent-client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py- Explains complex code errors
- Finds likely root causes
- Suggests fixes
- Suggests test steps
- Stores debugging history
- Works without an API key using rule-based analysis
- Improves with an OpenAI API key if added

## How to Run 

```bash
cd smart-debugging-agent-client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Optional: Add AI Reasoning

```bash
cp .env.example .env
```

Then add:

```text
OPENAI_API_KEY=your_key_here
```
