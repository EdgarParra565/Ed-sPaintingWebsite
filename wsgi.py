from app import app
from waitress import serve

if __name__ == "__main__":
    # Waitress will serve your app on port 5000 (or any port you prefer)
    serve(app, host="0.0.0.0", port=5000)
