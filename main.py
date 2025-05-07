#!/usr/bin/env python3
import os
import sys
from advanced_gpt_chatbot import run_chatbot_cli
from dotenv import load_dotenv

def main():
    """Main entry point for the restaurant chatbot"""
    # Load environment variables
    load_dotenv()

    print("Starting The Good Table Chatbot...")
    run_chatbot_cli()

if __name__ == "__main__":
    main()
