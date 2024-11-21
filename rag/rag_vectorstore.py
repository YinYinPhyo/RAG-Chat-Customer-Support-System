#!/usr/bin/env python
# coding: utf-8

from typing import List, Optional
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
import os
from utils.env_manager import init_environment

class RAGVectorStore:
    """Manages vector store for RAG"""
    
    def __init__(self, persist_directory: str = 'data/chroma/'):
        """Initialize vector store"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize environment and create embeddings
        init_environment()
        self.embedding = OpenAIEmbeddings()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )
        
    def create_or_load(self, documents: Optional[List[Document]] = None) -> Optional[Chroma]:
        """
        Create new or load existing vector store
        Args:
            documents: Documents to process (optional)
        Returns:
            Chroma: Vector store instance
        """
        try:
            if documents:
                # Split documents into chunks
                splits = self.text_splitter.split_documents(documents)
                
                # Create new vector store
                return Chroma.from_documents(
                    documents=splits,
                    embedding=self.embedding,
                    persist_directory=self.persist_directory
                )
            else:
                # Load existing vector store
                return Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embedding
                )
        except Exception as e:
            print(f"Error in vector store operation: {e}")
            return None 