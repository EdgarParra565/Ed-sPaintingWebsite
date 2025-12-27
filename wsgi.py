from waitress import serve
from app import app

if __name__ == '__main__':
    serve(
        app,
        host='0.0.0.0',
        port=10000,
        threads=8,
        channel_timeout=60,
        cleanup_interval=10,
        asyncore_use_poll=True
    )