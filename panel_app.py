#!/usr/bin/env python
# coding: utf-8

import panel as pn
import param
from rag import RAGService
from utils.env_manager import init_environment
import os

class RAGChatBot(param.Parameterized):
    chat_history = param.List([])
    answer = param.String("")
    db_query = param.String("")
    db_response = param.List([])
    
    def __init__(self, **params):
        super(RAGChatBot, self).__init__(**params)
        self.panels = []
        
        # Initialize RAG service
        init_environment()
        self.rag_service = RAGService()
        if not self.rag_service.initialize():
            raise RuntimeError("Failed to initialize RAG service")
    
    def convchain(self, query):
        """Process a query and update chat"""
        if not query:
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        
        result = self.rag_service.get_answer(query)
        answer = result.get('answer', result.get('result', 'No answer found'))
        sources = [doc.metadata.get("source", "") for doc in result.get("source_documents", [])]
        
        # Update chat history
        self.chat_history.extend([(query, answer, sources)])
        
        # Update UI panels
        self.panels.extend([
            pn.Row('User:', pn.pane.Markdown(query, width=600)),
            pn.Row('Assistant:', pn.pane.Markdown(answer, width=600))
        ])
        
        return pn.WidgetBox(*self.panels, scroll=True)
    
    def clear_history(self, event=None):
        """Clear chat history"""
        self.chat_history = []
        self.panels = []
        self.rag_service.clear_memory()
        
    def handle_file_upload(self, event):
        """Handle PDF file upload"""
        if not event.new:
            return pn.Row(pn.pane.Markdown("❌ No file selected"))
            
        try:
            # Create sources directory if it doesn't exist
            os.makedirs("data/sources", exist_ok=True)
            
            # Get original filename from the event
            filename = event.filename if hasattr(event, 'filename') else 'uploaded.pdf'
            
            # Save uploaded file to sources directory
            file_path = os.path.join("data/sources", filename)
            with open(file_path, "wb") as f:
                if isinstance(event.new, bytes):
                    f.write(event.new)
                else:
                    f.write(event.new.read())
                
            print(f"Saved file to: {file_path}")  # Debug log
            
            # Add file to sources
            sources = [{"PDF": file_path}]
            
            # Reinitialize RAG service with new document
            if not self.rag_service.initialize(load_documents=True):
                raise RuntimeError("Failed to reinitialize RAG service")
                
            return pn.Row(pn.pane.Markdown(f"✅ Successfully loaded: {filename}"))
        except Exception as e:
            error_msg = f"❌ Error loading file: {str(e)}"
            print(error_msg)  # Debug log
            return pn.Row(pn.pane.Markdown(error_msg))

    def handle_url_input(self, url: str, source_type: str, event=None) -> pn.Row:
        """Handle URL input"""
        if not url:
            return pn.Row(pn.pane.Markdown("❌ Please enter a URL"))
            
        try:
            # Create sources directory if it doesn't exist
            os.makedirs("data/sources", exist_ok=True)
            
            # Create unique filename
            filename = f"{source_type}-{abs(hash(url))}.txt"
            file_path = os.path.join("data/sources", filename)
            
            # Save URL to file
            with open(file_path, "w") as f:
                f.write(url)
                
            print(f"Saved URL to: {file_path}")  # Debug log
            
            # Load documents immediately to verify URL works
            if source_type.upper() == "YOUTUBE":
                test_docs = self.rag_service.loader.load_youtube(url)
                if not test_docs:
                    raise ValueError("Failed to load YouTube content")
            
            # Reinitialize RAG service with new source
            if not self.rag_service.initialize(load_documents=True):
                raise RuntimeError("Failed to reinitialize RAG service")
                
            return pn.Row(pn.pane.Markdown(f"✅ Successfully added {source_type} content from: {url}"))
        except Exception as e:
            error_msg = f"❌ Error adding {source_type} content: {str(e)}"
            print(error_msg)  # Debug log
            return pn.Row(pn.pane.Markdown(error_msg))

def create_dashboard():
    """Create the Panel dashboard"""
    cb = RAGChatBot()
    
    # Create input widgets
    text_input = pn.widgets.TextInput(placeholder='Enter text here…')
    button_clear = pn.widgets.Button(name="Clear History", button_type='warning')
    button_clear.on_click(cb.clear_history)
    
    # File upload widgets with feedback
    file_input = pn.widgets.FileInput(accept='.pdf')
    file_status = pn.pane.Markdown("")
    
    def update_file_status(event):
        status = cb.handle_file_upload(event)
        if isinstance(status, pn.Row):
            file_status.object = status[0].object
    
    file_input.param.watch(update_file_status, 'value')
    
    # URL input widgets with feedback
    youtube_input = pn.widgets.TextInput(placeholder='Enter YouTube URL...')
    youtube_status = pn.pane.Markdown("")
    youtube_button = pn.widgets.Button(name="Add YouTube", button_type='primary')
    
    def update_youtube_status(event):
        if not youtube_input.value:
            youtube_status.object = "❌ Please enter a URL"
            return
            
        status = cb.handle_url_input(youtube_input.value, 'YouTube')
        if isinstance(status, pn.Row):
            youtube_status.object = status[0].object
            youtube_input.value = ""  # Clear input after successful addition
    
    youtube_button.on_click(update_youtube_status)
    
    # Web URL input
    url_input = pn.widgets.TextInput(placeholder='Enter webpage URL...')
    url_status = pn.pane.Markdown("")
    url_button = pn.widgets.Button(name="Add Webpage", button_type='primary')
    
    def update_url_status(event):
        if not url_input.value:
            url_status.object = "❌ Please enter a URL"
            return
            
        status = cb.handle_url_input(url_input.value, 'URL')
        if isinstance(status, pn.Row):
            url_status.object = status[0].object
            url_input.value = ""
    
    url_button.on_click(update_url_status)
    
    # Bind conversation to input
    conversation = pn.bind(cb.convchain, text_input)
    
    # Create dashboard layout with tabs
    chat_tab = pn.Column(
        pn.Row(text_input),
        pn.layout.Divider(),
        pn.panel(conversation, loading_indicator=True, height=400),
        pn.layout.Divider(),
        pn.Row(button_clear)
    )
    
    sources_tab = pn.Column(
        pn.Row(pn.pane.Markdown('## Add PDF Document')),
        pn.Row(file_input),
        pn.Row(file_status),
        pn.layout.Divider(),
        pn.Row(pn.pane.Markdown('## Add YouTube Video')),
        pn.Row(youtube_input, youtube_button),
        pn.Row(youtube_status),
        pn.layout.Divider(),
        pn.Row(pn.pane.Markdown('## Add Webpage')),
        pn.Row(url_input, url_button),
        pn.Row(url_status)
    )
    
    # Create main dashboard
    dashboard = pn.Column(
        pn.Row(pn.pane.Markdown('# RAG Chat System')),
        pn.Tabs(
            ('Chat', chat_tab),
            ('Add Sources', sources_tab)
        )
    )
    
    return dashboard

def main():
    """Main entry point"""
    pn.extension()
    dashboard = create_dashboard()
    dashboard.show()

if __name__ == "__main__":
    main() 