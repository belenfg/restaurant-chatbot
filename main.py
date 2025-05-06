#!/usr/bin/env python3
# Main entry point for Restaurant Chatbot

import os
import sys

def main():
    """
    Main entry point for the restaurant chatbot.
    This function handles dependency verification and launches the chatbot.
    """
    # Check if the required files exist
    required_files = ["advanced_gpt_chatbot.py"]
    original_file = None

    if os.path.exists("restaurant_chatbot.py"):
        original_file = "restaurant_chatbot.py"
        required_files.append("restaurant_chatbot.py")
    else:
        print("Error: Could not find restaurant_chatbot.py")
        print("Make sure these files are in the same directory.")
        sys.exit(1)

    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: Required file {file} not found.")
            print("Make sure all the necessary files are in the same directory.")
            sys.exit(1)

    print(f"Found all required files: {', '.join(required_files)}")
    print(f"Using {original_file} for core restaurant data")

    # Import the run function from advanced_gpt_chatbot
    try:
        from advanced_gpt_chatbot import run_chatbot_cli
        run_chatbot_cli()
    except ImportError:
        print("Error importing the chatbot. Make sure all dependencies are installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()