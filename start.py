#!/usr/bin/env python
# coding: utf-8

from utils.env_manager import init_environment
from panel_app import main

def start():
    """Start the application"""
    try:
        # Initialize environment
        init_environment()
        
        # Start Panel interface
        main()
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(start()) 