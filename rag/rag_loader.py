#!/usr/bin/env python
# coding: utf-8

import os
from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders import YoutubeAudioLoader

class RAGLoader:
    """Handles document loading for RAG"""
    
    def __init__(self, source_dir: str = "data/sources", temp_dir: str = "data/temp"):
        """
        Initialize RAG loader
        Args:
            source_dir: Directory containing source files
            temp_dir: Directory for temporary files
        """
        self.source_dir = source_dir
        self.temp_dir = temp_dir
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF document"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
                
            print(f"Loading PDF from: {file_path}")  # Debug log
            
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            print(f"Loaded {len(documents)} pages from PDF")  # Debug log
            
            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = file_path
                doc.metadata["source_type"] = "PDF"
                
            return documents
        except Exception as e:
            print(f"Error loading PDF: {e}")  # Debug log
            return []
            
    def load_youtube(self, url: str) -> List[Document]:
        """Load YouTube content"""
        try:
            print(f"Loading YouTube content from: {url}")  # Debug log
            
            # Clean up the URL to get video ID
            if "youtu.be" in url:
                video_id = url.split("/")[-1].split("?")[0]
                url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"Processed YouTube URL: {url}")  # Debug log
            
            # Create temp directory if it doesn't exist
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Initialize loaders
            audio_loader = YoutubeAudioLoader([url], self.temp_dir)
            whisper_parser = OpenAIWhisperParser()
            loader = GenericLoader(audio_loader, whisper_parser)
            
            # Load and parse content
            print("Downloading and transcribing YouTube content...")  # Debug log
            documents = loader.load()
            
            if not documents:
                print("Warning: No content extracted from YouTube video")
                return []
                
            # Add metadata
            for doc in documents:
                doc.metadata["source"] = url
                doc.metadata["source_type"] = "YouTube"
                print(f"Added document with content length: {len(doc.page_content)}")  # Debug log
                
            print(f"Successfully loaded YouTube content: {len(documents)} documents")  # Debug log
            return documents
        
        except Exception as e:
            print(f"Error loading YouTube content: {e}")  # Debug log
            import traceback
            traceback.print_exc()  # Print full error trace
            return []
            
    def load_url(self, url: str) -> List[Document]:
        """Load URL content"""
        try:
            loader = WebBaseLoader(url)
            return loader.load()
        except Exception as e:
            print(f"Error loading URL: {e}")
            return []
            
    def read_source_file(self, file_path: str) -> Optional[str]:
        """Read content from source file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")
                
            with open(file_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading source file: {e}")
            return None
            
    def load_from_sources(self, sources: List[Dict[str, str]]) -> List[Document]:
        """
        Load documents from multiple sources
        Args:
            sources: List of source configurations
        Returns:
            List[Document]: Loaded documents
        """
        documents = []
        
        for source in sources:
            source_type = list(source.keys())[0]
            source_path = source[source_type]
            
            try:
                print(f"Loading {source_type} from: {source_path}")  # Debug log
                
                if source_type == "PDF":
                    docs = self.load_pdf(source_path)
                elif source_type == "YouTube":
                    url = self.read_source_file(source_path)
                    if url:
                        docs = self.load_youtube(url)
                    else:
                        continue
                elif source_type == "URL":
                    url = self.read_source_file(source_path)
                    if url:
                        docs = self.load_url(url)
                    else:
                        continue
                else:
                    print(f"Unsupported source type: {source_type}")
                    continue
                
                if docs:
                    documents.extend(docs)
                    print(f"Successfully loaded {len(docs)} documents from {source_type}")  # Debug log
                else:
                    print(f"No documents loaded from {source_path}")
                
            except Exception as e:
                print(f"Error loading {source_type} from {source_path}: {e}")
                continue
                
        return documents
    
    def load_documents(self, sources: Optional[List[Dict[str, str]]] = None) -> List[Document]:
        """
        Load all documents
        Args:
            sources: Optional source configurations
        Returns:
            List[Document]: All loaded documents
        """
        if sources is None:
            # Scan sources directory for all files
            sources = []
            for filename in os.listdir(self.source_dir):
                file_path = os.path.join(self.source_dir, filename)
                if filename.endswith('.pdf'):
                    sources.append({"PDF": file_path})
                elif filename.endswith('.txt'):
                    if 'youtube' in filename.lower():
                        sources.append({"YouTube": file_path})
                    else:
                        sources.append({"URL": file_path})
                        
            print(f"Found {len(sources)} source files in {self.source_dir}")  # Debug log
            
        return self.load_from_sources(sources)
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")