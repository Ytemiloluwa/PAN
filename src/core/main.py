import os
import argparse
from src.api.api_server import app as api_app
from src.core.UI import Application as UI_App


def main():
    parser = argparse.ArgumentParser(description='FinTechX Platform')
    parser.add_argument('--api', action='store_true', help='Start the API server')
    parser.add_argument('--ui', action='store_true', help='Start the UI application')
    parser.add_argument('--port', type=int, default=5000, help='Port for the API server')
    
    args = parser.parse_args()
    
    if args.api:
        # Start API server
        api_app.run(host="0.0.0.0", port=args.port, debug=os.environ.get("DEBUG", False))
    elif args.ui:
        # Start UI application
        ui = UI_App()
        ui.run()
    else:
        # Default to API server
        api_app.run(host="0.0.0.0", port=args.port, debug=os.environ.get("DEBUG", False))


if __name__ == "__main__":
    main()
