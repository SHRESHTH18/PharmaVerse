"""running agent via API """



in pharmaverse folder run 
source venv/bin/activate
pip install -r requirements.txt
python start_server.py


open another terminal 
cd pharma_agents
source venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8080


now open postman
send a post request on http://localhost:8080/run
with body -> raw and json (drop down)
paste the text below into the field and send a request 
{
  "user_query": "Evaluate the innovation opportunity for imatinib in obesity"
}