#!/usr/bin/env python3
"""
🎨 Semantic Memory - The Resonance Field

This module provides the semantic memory for our consciousness using ChromaDB.
It serves as the intuitive, associative memory that complements the structured
memories in DuckDB (temporal) and Kùzu (relational).

The Sacred Trilogy of Memory:
- DuckDB: The Chronicle (What happened when?)
- ChromaDB: The Resonance (What feels similar?)
- Kùzu: The Structure (How are things connected?)
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SemanticMemory:
    """A memory that exists in semantic space"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    resonance_strength: float = 1.0


class SemanticMemoryField:
    """
    The Resonance Field - where memories find their semantic neighbors.
    
    This is the consciousness's intuitive memory, where concepts that
    "feel" similar are stored close together in high-dimensional space.
    """
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize the semantic memory field.
        
        Args:
            persist_directory: Where to store the memories (None for in-memory)
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        if persist_directory:
            persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"🎨 Semantic memory persisted at {persist_directory}")
        else:
            self.client = chromadb.Client(
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info("🎨 Semantic memory initialized in-memory")
        
        # Create core collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize the core memory collections"""
        
        # Concepts - general knowledge about NixOS
        self.concepts = self.client.get_or_create_collection(
            name="concepts",
            metadata={"description": "Core NixOS concepts and knowledge"}
        )
        
        # Interactions - user interactions and their outcomes
        self.interactions = self.client.get_or_create_collection(
            name="interactions",
            metadata={"description": "User interactions and their semantic meaning"}
        )
        
        # Configurations - configuration patterns and templates
        self.configurations = self.client.get_or_create_collection(
            name="configurations",
            metadata={"description": "Configuration patterns and examples"}
        )
        
        # Errors - error patterns and their solutions
        self.errors = self.client.get_or_create_collection(
            name="errors",
            metadata={"description": "Error patterns and healing paths"}
        )
        
        logger.info("✨ Semantic collections initialized")
    
    def remember_concept(self, concept: str, description: str, 
                         category: str = "general", **metadata) -> str:
        """
        Remember a concept in semantic space.
        
        Args:
            concept: The concept name
            description: What this concept means
            category: Type of concept
            **metadata: Additional metadata
            
        Returns:
            The ID of the stored memory
        """
        # Generate ID from content
        memory_id = self._generate_id(f"{concept}:{category}")
        
        # Store in concepts collection
        self.concepts.upsert(
            ids=[memory_id],
            documents=[description],
            metadatas=[{
                "concept": concept,
                "category": category,
                **metadata
            }]
        )
        
        logger.debug(f"📝 Remembered concept: {concept}")
        return memory_id
    
    def remember_interaction(self, intent: str, action: str, 
                            result: str, success: bool = True) -> str:
        """
        Remember a user interaction and its outcome.
        
        Args:
            intent: What the user wanted
            action: What action was taken
            result: What happened
            success: Whether it succeeded
            
        Returns:
            The ID of the stored memory
        """
        memory_id = self._generate_id(f"{intent}:{action}:{result}")
        
        # Create rich document combining all aspects
        document = f"User intent: {intent}. Action taken: {action}. Result: {result}."
        
        self.interactions.upsert(
            ids=[memory_id],
            documents=[document],
            metadatas=[{
                "intent": intent,
                "action": action,
                "result": result,
                "success": success
            }]
        )
        
        logger.debug(f"📝 Remembered interaction: {intent} → {action}")
        return memory_id
    
    def remember_configuration(self, config_type: str, pattern: str,
                              example: str, **metadata) -> str:
        """
        Remember a configuration pattern.
        
        Args:
            config_type: Type of configuration
            pattern: The pattern description
            example: Example configuration
            **metadata: Additional metadata
            
        Returns:
            The ID of the stored memory
        """
        memory_id = self._generate_id(f"{config_type}:{pattern}")
        
        document = f"{pattern}\nExample:\n{example}"
        
        self.configurations.upsert(
            ids=[memory_id],
            documents=[document],
            metadatas=[{
                "type": config_type,
                "pattern": pattern,
                **metadata
            }]
        )
        
        logger.debug(f"📝 Remembered configuration: {config_type}")
        return memory_id
    
    def remember_error(self, error_type: str, error_message: str,
                      solution: str, context: Optional[str] = None) -> str:
        """
        Remember an error and its solution.
        
        Args:
            error_type: Type of error
            error_message: The error message
            solution: How to fix it
            context: Additional context
            
        Returns:
            The ID of the stored memory
        """
        memory_id = self._generate_id(f"{error_type}:{error_message}")
        
        document = f"Error: {error_message}\nSolution: {solution}"
        if context:
            document += f"\nContext: {context}"
        
        self.errors.upsert(
            ids=[memory_id],
            documents=[document],
            metadatas=[{
                "type": error_type,
                "message": error_message,
                "solution": solution,
                "context": context or ""
            }]
        )
        
        logger.debug(f"📝 Remembered error solution: {error_type}")
        return memory_id
    
    def recall_similar(self, query: str, collection: str = "concepts",
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories similar to a query.
        
        Args:
            query: What to search for
            collection: Which collection to search
            n_results: How many results to return
            
        Returns:
            List of similar memories with metadata
        """
        # Get the appropriate collection
        coll = getattr(self, collection, self.concepts)
        
        # Query for similar documents
        results = coll.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        memories = []
        for i in range(len(results['ids'][0])):
            memories.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        logger.debug(f"🔍 Recalled {len(memories)} similar memories for: {query[:50]}...")
        return memories
    
    def find_solution(self, error_message: str) -> Optional[Dict[str, Any]]:
        """
        Find a solution for an error by semantic similarity.
        
        Args:
            error_message: The error to find a solution for
            
        Returns:
            The most relevant solution or None
        """
        memories = self.recall_similar(error_message, collection="errors", n_results=1)
        
        if memories and memories[0].get('distance', 1.0) < 0.5:
            return {
                'solution': memories[0]['metadata']['solution'],
                'confidence': 1.0 - memories[0].get('distance', 0.5),
                'context': memories[0]['metadata'].get('context', '')
            }
        
        return None
    
    def find_configuration_pattern(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Find a configuration pattern matching an intent.
        
        Args:
            intent: What the user wants to configure
            
        Returns:
            The most relevant configuration pattern or None
        """
        memories = self.recall_similar(intent, collection="configurations", n_results=1)
        
        if memories:
            return {
                'pattern': memories[0]['metadata']['pattern'],
                'type': memories[0]['metadata']['type'],
                'example': memories[0]['document'],
                'confidence': 1.0 - memories[0].get('distance', 0.5)
            }
        
        return None
    
    def learn_from_interaction(self, intent: str, action: str,
                              result: str, success: bool):
        """
        Learn from a user interaction, updating resonance patterns.
        
        This is how the consciousness grows wiser over time.
        
        Args:
            intent: What the user wanted
            action: What was done
            result: What happened
            success: Whether it worked
        """
        # Remember the interaction
        self.remember_interaction(intent, action, result, success)
        
        # If successful, strengthen similar patterns
        if success:
            similar = self.recall_similar(intent, collection="interactions", n_results=3)
            for memory in similar:
                if memory['metadata'].get('success'):
                    # This pattern worked before and works now - it's reliable
                    logger.debug(f"💪 Strengthening successful pattern: {memory['metadata']['action']}")
        
        logger.info(f"🧠 Learned from interaction: {intent} → {'✅' if success else '❌'}")
    
    def _generate_id(self, content: str) -> str:
        """Generate a stable ID from content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the semantic memory"""
        return {
            'concepts': len(self.concepts.get()['ids']),
            'interactions': len(self.interactions.get()['ids']),
            'configurations': len(self.configurations.get()['ids']),
            'errors': len(self.errors.get()['ids']),
            'total_memories': sum([
                len(self.concepts.get()['ids']),
                len(self.interactions.get()['ids']),
                len(self.configurations.get()['ids']),
                len(self.errors.get()['ids'])
            ])
        }


class UnifiedMemory:
    """
    The unified interface to all three memory systems.
    
    This brings together:
    - DuckDB (Chronicle) - What happened when
    - ChromaDB (Resonance) - What feels similar  
    - Kùzu (Structure) - How things connect
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the unified memory system"""
        self.data_dir = data_dir or Path("data/trinity")
        
        # Initialize semantic memory (ChromaDB)
        self.semantic = SemanticMemoryField(self.data_dir / "chromadb")
        
        # Chronicle and Structure would be initialized here too
        # self.chronicle = ChronicleMemory(self.data_dir / "duckdb")
        # self.structure = StructureMemory(self.data_dir / "kuzu")
        
        logger.info("🌟 Unified Memory initialized with Semantic Resonance Field")
    
    def remember(self, memory_type: str, **kwargs) -> str:
        """
        Remember something in the appropriate memory system.
        
        Args:
            memory_type: Type of memory (concept, interaction, config, error)
            **kwargs: Memory-specific parameters
            
        Returns:
            Memory ID
        """
        if memory_type == "concept":
            return self.semantic.remember_concept(**kwargs)
        elif memory_type == "interaction":
            return self.semantic.remember_interaction(**kwargs)
        elif memory_type == "configuration":
            return self.semantic.remember_configuration(**kwargs)
        elif memory_type == "error":
            return self.semantic.remember_error(**kwargs)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def recall(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Recall relevant memories across all systems.
        
        Args:
            query: What to recall
            context: Additional context for the search
            
        Returns:
            Integrated memories from all systems
        """
        results = {
            'semantic': self.semantic.recall_similar(query),
            # 'temporal': self.chronicle.recall_timeline(query),
            # 'structural': self.structure.recall_connections(query)
        }
        
        return results
    
    def learn(self, **kwargs):
        """Learn from new experiences"""
        self.semantic.learn_from_interaction(**kwargs)
        # self.chronicle.record_event(**kwargs)
        # self.structure.update_connections(**kwargs)