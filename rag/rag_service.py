#!/usr/bin/env python
# coding: utf-8

from typing import Dict, Optional
from .rag_loader import RAGLoader
from .rag_vectorstore import RAGVectorStore
from .rag_chain import RAGChain

class RAGService:
    """Main service for RAG operations"""
    
    def __init__(self):
        self.loader = RAGLoader()
        self.vectorstore = RAGVectorStore()
        self.chain = None
        
    def initialize(self, load_documents: bool = True) -> bool:
        """
        Initialize the RAG service
        Args:
            load_documents: Whether to load new documents
        Returns:
            bool: Success status
        """
        try:
            if load_documents:
                print("Loading documents...")  # Debug log
                documents = self.loader.load_documents()
                if not documents:
                    print("No documents loaded")
                    return False
                    
                print(f"Creating vector store with {len(documents)} documents")  # Debug log
                vectordb = self.vectorstore.create_or_load(documents)
            else:
                print("Loading existing vector store...")  # Debug log
                vectordb = self.vectorstore.create_or_load()
                
            if not vectordb:
                print("Failed to create/load vector store")
                return False
                
            self.chain = RAGChain(vectordb)
            print("RAG service initialized successfully")  # Debug log
            return True
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            return False
            
    def get_answer(self, question: str, use_conversation: bool = True) -> Dict:
        """
        Get answer to a question
        Args:
            question: User's question
            use_conversation: Whether to use conversational chain
        """
        try:
            if use_conversation:
                chain = self.chain.create_conversational_chain()
                return chain({"question": question})
            else:
                chain = self.chain.create_qa_chain()
                return chain({"query": question})
        except Exception as e:
            print(f"Error getting answer: {e}")
            return {
                "answer": "Sorry, I encountered an error processing your question.",
                "source_documents": []
            }
            
    def clear_memory(self):
        """Clear conversation memory"""
        if self.chain:
            self.chain.memory.clear() 