from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',     # Accessible from other devices in the network
        port=8000,          # Custom port instead of default 5000
        debug=True,         # Enables debug mode with auto-reload
        threaded=True       # Allows handling multiple requests at once
    )
