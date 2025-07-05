"""
RAG Agent Example using LangChain

This example demonstrates how to create a RAG (Retrieval-Augmented Generation) agent
using the AgentHub SDK with LangChain integration.
"""

import os
from typing import Dict, Any, List
from agenthub import AgentBuilder, publish_agent

# Optional: LangChain imports (install with: pip install langchain chromadb openai)
try:
    from langchain.document_loaders import DirectoryLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available. Install with: pip install agenthub-sdk[langchain]")

class RAGAgent:
    """RAG Agent implementation using LangChain"""
    
    def __init__(self, documents_path: str):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for RAG agent")
            
        self.documents_path = documents_path
        self.vectorstore = None
        self.qa_chain = None
        self.setup_rag()
    
    def setup_rag(self):
        """Setup the RAG pipeline"""
        # Load documents
        loader = DirectoryLoader(
            self.documents_path, 
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_documents(
            texts, 
            embeddings,
            persist_directory="./chroma_db"
        )
        
        # Create QA chain
        llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            ),
            return_source_documents=True
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a query and return answer with sources"""
        if not self.qa_chain:
            raise ValueError("RAG system not initialized")
            
        result = self.qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "sources": [doc.metadata.get("source", "") 
                       for doc in result["source_documents"]],
            "confidence": self.calculate_confidence(result)
        }
    
    def calculate_confidence(self, result) -> float:
        """Simple confidence calculation based on source relevance"""
        return min(len(result["source_documents"]) * 0.25, 1.0)


def create_rag_agent():
    """Create a RAG agent using AgentHub"""
    
    # Create agent builder
    agent = AgentBuilder("research-assistant")
    
    # Initialize RAG system (with fallback if LangChain not available)
    if LANGCHAIN_AVAILABLE:
        # Use real RAG system
        knowledge_base_path = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
        if not os.path.exists(knowledge_base_path):
            os.makedirs(knowledge_base_path)
            # Create sample document
            with open(os.path.join(knowledge_base_path, "sample.txt"), "w") as f:
                f.write("This is a sample document for the RAG agent.")
        
        rag_system = RAGAgent(knowledge_base_path)
    else:
        # Fallback implementation
        rag_system = None
    
    @agent.endpoint("/query", description="Answer questions using document knowledge")
    def handle_query(request):
        """Handle query requests"""
        question = request.json.get("question")
        if not question:
            return {"error": "Question is required"}
        
        if rag_system:
            try:
                result = rag_system.query(question)
                return result
            except Exception as e:
                return {"error": f"RAG query failed: {str(e)}"}
        else:
            # Fallback response
            return {
                "answer": f"I would search for information about: {question}",
                "sources": [],
                "confidence": 0.5,
                "note": "LangChain not available - this is a fallback response"
            }
    
    @agent.endpoint("/upload", description="Upload documents to knowledge base")
    def upload_documents(request):
        """Handle document uploads to knowledge base"""
        # In a real implementation, this would handle file uploads
        # For now, return a placeholder response
        return {
            "status": "success", 
            "message": "Document upload endpoint (implementation needed)",
            "note": "This endpoint would handle file uploads in a real implementation"
        }
    
    @agent.endpoint("/search", description="Search documents")
    def search_documents(request):
        """Search for relevant documents"""
        query = request.json.get("query", "")
        
        if rag_system and rag_system.vectorstore:
            try:
                # Perform similarity search
                docs = rag_system.vectorstore.similarity_search(query, k=5)
                results = []
                for doc in docs:
                    results.append({
                        "content": doc.page_content[:200] + "...",
                        "source": doc.metadata.get("source", "unknown"),
                        "relevance": 0.8  # Placeholder
                    })
                return {"results": results}
            except Exception as e:
                return {"error": f"Search failed: {str(e)}"}
        else:
            return {
                "results": [],
                "note": "Vector store not available"
            }
    
    @agent.endpoint("/stats", method="GET", description="Get knowledge base statistics")
    def get_stats(request):
        """Get statistics about the knowledge base"""
        return {
            "total_documents": 1,  # Placeholder
            "total_chunks": 10,    # Placeholder
            "last_updated": "2024-01-01",
            "status": "active"
        }
    
    # Set agent metadata
    agent.set_metadata({
        "name": "Research Assistant",
        "description": "AI agent that answers questions using your documents",
        "version": "1.0.0",
        "category": "research",
        "tags": ["research", "rag", "qa", "documents"],
        "pricing": {
            "type": "per_request",
            "price": 0.05
        },
        "author": "AgentHub Team",
        "license": "MIT"
    })
    
    return agent

if __name__ == "__main__":
    # Create the agent
    agent = create_rag_agent()
    
    # Option 1: Serve locally for development
    from agenthub.server import serve_agent
    print("Starting RAG Agent server...")
    print("Available endpoints:")
    for endpoint in agent.get_endpoints():
        print(f"  - {endpoint}: {agent.get_endpoints()[endpoint]['description']}")
    
    serve_agent(agent, host="localhost", port=8000, reload=True)
    
    # Option 2: Publish to AgentHub (uncomment to use)
    # publish_agent(agent, api_key=os.getenv("AGENTHUB_API_KEY"))