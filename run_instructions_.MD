# PharmaVerse - Run Instructions

## Step-1:
Create a `.env` file in the project root:

`env

GROQ_API_KEY=your_groq_api_key_here


## Step 2: Start the Mock API & Backend Server (Port 8000)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python start_server.py

## Step 3: Start the Master Agent API (Port 8080)
- open a new terminal in root folder and execute the following commands
cd pharma_agents
source venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8080


## Step 4: Run the Frontend Application
- open a new terminal in root folder and execute the following commands
cd website
open index.html

 

