#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import load_dotenv, find_dotenv
import openai

def init_environment():
    """Initialize environment variables"""
    # Load environment variables
    _ = load_dotenv(find_dotenv())
    
    # Get OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment")
        
    # Set for both openai and langchain
    os.environ['OPENAI_API_KEY'] = api_key
    openai.api_key = api_key
    
    return api_key