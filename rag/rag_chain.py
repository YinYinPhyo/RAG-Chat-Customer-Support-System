#!/usr/bin/env python
# coding: utf-8

from typing import Dict, Any
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

class RAGChain:
    """Manages RAG chains"""
    
    def __init__(self, vectorstore, model_name: str = "gpt-3.5-turbo"):
        """Initialize RAG chain"""
        if not vectorstore:
            raise ValueError("Vector store cannot be None")
            
        self.vectorstore = vectorstore
        
        # Initialize OpenAI
        from utils.env_manager import init_environment
        init_environment()  # Ensure API key is loaded
        
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )
        
    def get_qa_prompt(self) -> PromptTemplate:
        """Get QA prompt template"""
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Use three sentences maximum. Keep the answer as concise as possible. 
        Always say "thanks for asking!" at the end of the answer.

        {context}

        Question: {question}
        Helpful Answer:"""
        
        return PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )
        
    def create_qa_chain(self) -> RetrievalQA:
        """Create RetrievalQA chain"""
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": self.get_qa_prompt()},
            return_source_documents=True
        )
        
    def create_conversational_chain(self) -> ConversationalRetrievalChain:
        """Create ConversationalRetrievalChain"""
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            return_source_documents=True,
            output_key="answer"
        ) 