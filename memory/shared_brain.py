"""
🧬 GENESIS HIVE MIND
Author: Sharan Kumar Reddy Sutrapu
Website: https://sharansutrapu.com/
LinkedIn: https://www.linkedin.com/in/sharan-kumar-reddy-sutrapu-34b50519b/
GitHub: https://github.com/sharansutrapu
Medium: https://medium.com/@sutrapusharan

🧠 GENESIS SHARED BRAIN — The Collective Memory
Local ChromaDB vector store for reasoning strategies.

When a model successfully answers a prompt, its "Reflection" on HOW
it arrived at the answer (search terms, logic paths, key facts) is
saved here. Future models query this DB before answering new questions
to learn from previous successes.

Usage:
    from memory.shared_brain import SharedBrain

    brain = SharedBrain()
    brain.save_strategy(query, answer, reflection, model_name)
    past = brain.recall_strategies("new question", top_k=3)
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


COLLECTION_NAME = "genesis_strategies"
DEFAULT_DB_PATH = Path(__file__).parent / "chromadb_data"


class SharedBrain:
    """
    🧠 SHARED BRAIN — Strategy Vector Database

    Stores and retrieves reasoning strategies using ChromaDB.
    Enables cross-session and cross-model learning.
    """

    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir or DEFAULT_DB_PATH
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create the strategies collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Genesis Hive Mind reasoning strategies"},
        )

    def save_strategy(
        self,
        query: str,
        answer: str,
        reflection: str,
        model_name: str,
    ) -> str:
        """
        Save a reasoning strategy to the knowledge base.

        Args:
            query: The original user question.
            answer: The consensus answer produced.
            reflection: The model's reflection on HOW the answer was found
                        (search terms used, logic chain, key evidence).
            model_name: Which model produced this reflection.

        Returns:
            The ID of the stored strategy.
        """
        doc_id = f"strat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # The document text is the reflection — this is what gets embedded
        # for semantic similarity search.
        self.collection.add(
            ids=[doc_id],
            documents=[reflection],
            metadatas=[
                {
                    "query": query,
                    "answer": answer[:500],  # Truncate long answers for metadata
                    "model": model_name,
                    "timestamp": datetime.now().isoformat(),
                }
            ],
        )

        return doc_id

    def recall_strategies(
        self, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant past strategies for a new query.

        Args:
            query: The new question to find relevant strategies for.
            top_k: Number of strategies to return.

        Returns:
            List of dicts with keys: reflection, query, answer, model, distance.
        """
        if self.collection.count() == 0:
            return []

        # Clamp top_k to actual collection size
        effective_k = min(top_k, self.collection.count())

        results = self.collection.query(
            query_texts=[query],
            n_results=effective_k,
        )

        strategies = []
        for i in range(len(results["ids"][0])):
            strategies.append(
                {
                    "id": results["ids"][0][i],
                    "reflection": results["documents"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                    "query": results["metadatas"][0][i].get("query", ""),
                    "answer": results["metadatas"][0][i].get("answer", ""),
                    "model": results["metadatas"][0][i].get("model", ""),
                    "timestamp": results["metadatas"][0][i].get("timestamp", ""),
                }
            )

        return strategies

    def ingest_directory(self, directory_path: str):
        import os
        from rich.console import Console
        console = Console()
        
        path = os.path.expanduser(directory_path)
        if not os.path.exists(path):
            console.print(f"❌ Directory not found: {path}", style="red")
            return "Directory not found."
            
        # Expanded list of supported extensions for DevOps engineering
        supported_exts = [
            '.py', '.tf', '.tfvars', '.hcl', '.yaml', '.yml', 
            '.json', '.md', '.sh', '.env', '.ini', '.conf', '.txt'
        ]
        documents = []
        metadatas = []
        ids = []
        
        console.print(f"📂 Scanning directory: {path}", style="cyan")
        
        for root, _, files in os.walk(path):
            # Skip hidden directories like .git or .terraform
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in supported_exts):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Basic chunking: treat the whole file as a chunk if small, or split it
                            chunk_size = 4000
                            for i in range(0, len(content), chunk_size):
                                chunk = content[i:i+chunk_size]
                                documents.append(chunk)
                                metadatas.append({"source": file_path, "type": "codebase"})
                                ids.append(f"{file_path}_chunk_{i}")
                    except Exception as e:
                        continue
                        
        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            msg = f"✅ Successfully ingested {len(documents)} code chunks from {path} into Shared Brain."
            console.print(msg, style="green")
            return msg
        else:
            return "No supported code files found."

    def query_codebase(self, query: str, top_k: int = 5) -> str:
        if self.collection.count() == 0:
            return "No codebase ingested."

        # Query ChromaDB specifically for codebase chunks
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
            where={"type": "codebase"}
        )
        
        if not results["documents"] or not results["documents"][0]:
            return "No relevant code found."
            
        context = ""
        for i, doc in enumerate(results["documents"][0]):
            source = results["metadatas"][0][i].get("source", "Unknown File")
            context += f"\n--- File: {source} ---\n{doc}\n"
            
        return context

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the shared brain."""
        count = self.collection.count()
        return {
            "total_strategies": count,
            "collection": COLLECTION_NAME,
            "persist_dir": str(self.persist_dir),
        }

    def clear(self):
        """⚠️ Delete all strategies. Use with caution."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Genesis Hive Mind reasoning strategies"},
        )


# Quick self-test
if __name__ == "__main__":
    print("🧠 Testing Shared Brain...")
    brain = SharedBrain(persist_dir=Path("/tmp/genesis_brain_test"))

    # Save
    doc_id = brain.save_strategy(
        query="What is the capital of France?",
        answer="Paris is the capital of France.",
        reflection="I used general knowledge. The capital of France is Paris. "
                   "No web search was needed for this common-knowledge question.",
        model_name="test_model",
    )
    print(f"✅ Saved strategy: {doc_id}")

    # Recall
    results = brain.recall_strategies("capital city of Germany", top_k=2)
    print(f"✅ Recalled {len(results)} strategies")
    for r in results:
        print(f"   [{r['model']}] {r['reflection'][:80]}...")

    # Stats
    print(f"📊 Stats: {brain.get_stats()}")
    print("🎉 Shared Brain operational!")
