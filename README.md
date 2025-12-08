# PharmaVerse
# hello
# To run mock API 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn mock_api:app --host 0.0.0.0 --port 8000 --reload