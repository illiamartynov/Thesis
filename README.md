1. Install dependencies
```
pip install -r requirements.txt
```
 2. Set environment variables

Create a .env file in the project root:
```
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
TG_SESSION=your_exported_session_string
```

Run the Flask server
```
python app.py
```
The app will start at:
```
http://127.0.0.1:5000
```
