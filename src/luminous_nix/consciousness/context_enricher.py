#!/usr/bin/env python3
"""
🧠 Context Enricher - Connecting AI to Data Trinity
Enriches LLM prompts with relevant context from databases before execution.

This ensures the AI makes informed decisions based on:
- Temporal patterns (what happened before)
- Semantic memory (similar concepts)
- Relational knowledge (how things connect)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextEnricher:
    """
    Enriches prompts with relevant context from Data Trinity databases.
    
    This is the bridge between stored knowledge and AI decision-making.
    """
    
    def __init__(self, trinity_store=None):
        """Initialize context enricher with Trinity Store"""
        self.store = trinity_store
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Try to get TrinityStore if not provided
        if self.store is None:
            try:
                from ..persistence.trinity_store import TrinityStore
                self.store = TrinityStore()
                self.logger.info("🔱 Connected to Data Trinity for context enrichment")
            except Exception as e:
                self.logger.warning(f"⚠️ Data Trinity not available: {e}")
                self.store = None
    
    def enrich_prompt(self, 
                      prompt: str,
                      user_id: str = 'default',
                      task_type: str = 'conversation',
                      include_history: bool = True,
                      include_similar: bool = True,
                      include_relationships: bool = True) -> str:
        """
        Enrich a prompt with relevant context from databases.
        
        Args:
            prompt: The original prompt
            user_id: User making the request
            task_type: Type of task being performed
            include_history: Include temporal history
            include_similar: Include semantically similar items
            include_relationships: Include related concepts
            
        Returns:
            Enriched prompt with context
        """
        if not self.store:
            return prompt  # No enrichment possible without store
        
        enriched_parts = [prompt]
        
        # 1. Add temporal context (what happened recently)
        if include_history and hasattr(self.store, 'temporal') and self.store.temporal:
            history_context = self._get_temporal_context(user_id)
            if history_context:
                enriched_parts.append(f"\n\n[Recent History]\n{history_context}")
        
        # 2. Add semantic context (similar past interactions)
        if include_similar and hasattr(self.store, 'semantic') and self.store.semantic:
            similar_context = self._get_semantic_context(prompt)
            if similar_context:
                enriched_parts.append(f"\n\n[Similar Past Interactions]\n{similar_context}")
        
        # 3. Add relational context (related concepts)
        if include_relationships and hasattr(self.store, 'relational') and self.store.relational:
            relational_context = self._get_relational_context(prompt)
            if relational_context:
                enriched_parts.append(f"\n\n[Related Concepts]\n{relational_context}")
        
        # 4. Add user understanding level
        user_context = self._get_user_context(user_id, task_type)
        if user_context:
            enriched_parts.append(f"\n\n[User Context]\n{user_context}")
        
        enriched_prompt = "\n".join(enriched_parts)
        
        # Log enrichment
        if len(enriched_parts) > 1:
            self.logger.info(f"📚 Enriched prompt with {len(enriched_parts)-1} context sections")
        
        return enriched_prompt
    
    def _get_temporal_context(self, user_id: str, limit: int = 5) -> str:
        """Get recent command history for temporal context"""
        try:
            # Get recent learning trajectory
            trajectory = self.store.temporal.get_learning_trajectory(user_id)
            
            if not trajectory:
                return ""
            
            # Get last N commands
            recent = trajectory[-limit:] if len(trajectory) > limit else trajectory
            
            context_lines = []
            for event in recent:
                command = event.get('command', '')
                success = "✓" if event.get('success') else "✗"
                context_lines.append(f"- {success} {command}")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            self.logger.debug(f"Could not get temporal context: {e}")
            return ""
    
    def _get_semantic_context(self, prompt: str, limit: int = 3) -> str:
        """Find semantically similar past interactions"""
        try:
            # Find similar commands
            similar = self.store.semantic.find_similar_commands(prompt, n_results=limit)
            
            if not similar:
                return ""
            
            context_lines = []
            for item in similar:
                if 'documents' in item:
                    # ChromaDB format
                    docs = item['documents'][0] if item['documents'] else []
                    for doc in docs[:limit]:
                        context_lines.append(f"- {doc}")
                else:
                    # Simple format
                    context_lines.append(f"- {item.get('text', '')}")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            self.logger.debug(f"Could not get semantic context: {e}")
            return ""
    
    def _get_relational_context(self, prompt: str) -> str:
        """Get related concepts from knowledge graph"""
        try:
            # Extract key concept from prompt
            concepts = self._extract_concepts(prompt)
            
            if not concepts:
                return ""
            
            context_lines = []
            for concept in concepts[:2]:  # Limit to avoid overwhelming
                # Get prerequisites
                prereqs = self.store.relational.get_prerequisites(concept)
                if prereqs:
                    context_lines.append(f"{concept} requires: {', '.join(prereqs)}")
                
                # Could also get related concepts, next steps, etc.
            
            return "\n".join(context_lines)
            
        except Exception as e:
            self.logger.debug(f"Could not get relational context: {e}")
            return ""
    
    def _get_user_context(self, user_id: str, task_type: str) -> str:
        """Get user's understanding level and preferences"""
        try:
            # Get user understanding
            understanding = self.store.get_user_understanding(user_id, task_type)
            
            if not understanding:
                return ""
            
            context_lines = []
            
            # Add readiness level
            readiness = understanding.get('readiness', 0)
            if readiness < 0.3:
                context_lines.append("User level: Beginner (use simple explanations)")
            elif readiness < 0.7:
                context_lines.append("User level: Intermediate")
            else:
                context_lines.append("User level: Advanced (can handle complex topics)")
            
            # Add mastered concepts
            mastered = understanding.get('mastered_concepts', [])
            if mastered:
                context_lines.append(f"User knows: {', '.join(mastered[:5])}")
            
            # Add suggested next topic
            next_concept = self.store.suggest_next_concept(user_id)
            if next_concept:
                context_lines.append(f"Suggested next topic: {next_concept}")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            self.logger.debug(f"Could not get user context: {e}")
            return ""
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simple version)"""
        # Common NixOS concepts
        concepts = []
        concept_keywords = {
            'package': ['install', 'package', 'software'],
            'configuration': ['config', 'configure', 'settings'],
            'flake': ['flake', 'flakes'],
            'generation': ['generation', 'rollback', 'switch'],
            'service': ['service', 'systemd', 'daemon'],
            'user': ['user', 'home-manager'],
            'network': ['network', 'wifi', 'ethernet'],
        }
        
        text_lower = text.lower()
        for concept, keywords in concept_keywords.items():
            if any(kw in text_lower for kw in keywords):
                concepts.append(concept)
        
        return concepts
    
    def build_rag_context(self, 
                          query: str,
                          user_id: str = 'default',
                          max_context_length: int = 2000) -> Dict[str, Any]:
        """
        Build a RAG (Retrieval Augmented Generation) context.
        
        This provides structured context for the LLM to use.
        
        Returns:
            Dict with structured context for LLM
        """
        context = {
            'query': query,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'retrieved_context': {}
        }
        
        if not self.store:
            return context
        
        # Retrieve from all three databases
        retrieved = {}
        
        # Temporal: Recent history
        if hasattr(self.store, 'temporal') and self.store.temporal:
            try:
                trajectory = self.store.temporal.get_learning_trajectory(user_id)
                if trajectory:
                    retrieved['recent_commands'] = [
                        {
                            'command': e.get('command'),
                            'success': e.get('success'),
                            'timestamp': e.get('timestamp')
                        }
                        for e in trajectory[-10:]  # Last 10 commands
                    ]
            except:
                pass
        
        # Semantic: Similar content
        if hasattr(self.store, 'semantic') and self.store.semantic:
            try:
                similar = self.store.semantic.find_similar_commands(query, n_results=5)
                if similar:
                    retrieved['similar_interactions'] = similar
            except:
                pass
        
        # Relational: Knowledge graph
        if hasattr(self.store, 'relational') and self.store.relational:
            try:
                concepts = self._extract_concepts(query)
                if concepts:
                    retrieved['related_concepts'] = {}
                    for concept in concepts[:3]:
                        prereqs = self.store.relational.get_prerequisites(concept)
                        if prereqs:
                            retrieved['related_concepts'][concept] = {
                                'prerequisites': prereqs
                            }
            except:
                pass
        
        # User understanding
        try:
            understanding = self.store.get_user_understanding(user_id, query)
            if understanding:
                retrieved['user_profile'] = {
                    'readiness': understanding.get('readiness', 0),
                    'mastered_concepts': understanding.get('mastered_concepts', []),
                    'suggested_next': self.store.suggest_next_concept(user_id)
                }
        except:
            pass
        
        context['retrieved_context'] = retrieved
        
        # Calculate context size
        import json
        context_str = json.dumps(retrieved)
        if len(context_str) > max_context_length:
            self.logger.warning(f"Context too large ({len(context_str)} chars), truncating")
            # TODO: Implement smart truncation
        
        return context
    
    def format_for_llm(self, rag_context: Dict[str, Any]) -> str:
        """
        Format RAG context for inclusion in LLM prompt.
        
        Returns:
            Formatted string to prepend to prompt
        """
        lines = []
        retrieved = rag_context.get('retrieved_context', {})
        
        # Format recent commands
        if 'recent_commands' in retrieved:
            lines.append("=== Recent User History ===")
            for cmd in retrieved['recent_commands'][-5:]:
                status = "✓" if cmd['success'] else "✗"
                lines.append(f"{status} {cmd['command']}")
            lines.append("")
        
        # Format user profile
        if 'user_profile' in retrieved:
            profile = retrieved['user_profile']
            lines.append("=== User Profile ===")
            
            readiness = profile.get('readiness', 0)
            if readiness < 0.3:
                lines.append("Experience: Beginner (use simple language)")
            elif readiness < 0.7:
                lines.append("Experience: Intermediate")
            else:
                lines.append("Experience: Advanced")
            
            mastered = profile.get('mastered_concepts', [])
            if mastered:
                lines.append(f"Knows: {', '.join(mastered[:5])}")
            
            next_topic = profile.get('suggested_next')
            if next_topic:
                lines.append(f"Ready to learn: {next_topic}")
            lines.append("")
        
        # Format related concepts
        if 'related_concepts' in retrieved:
            lines.append("=== Related Knowledge ===")
            for concept, info in retrieved['related_concepts'].items():
                prereqs = info.get('prerequisites', [])
                if prereqs:
                    lines.append(f"{concept} requires: {', '.join(prereqs)}")
            lines.append("")
        
        return "\n".join(lines)


def test_context_enricher():
    """Test the context enricher"""
    print("🧠 Testing Context Enricher")
    print("=" * 60)
    
    enricher = ContextEnricher()
    
    # Test prompt enrichment
    test_prompts = [
        ("How do I install firefox?", "default", "help"),
        ("What is a flake?", "default", "explanation"),
        ("My system won't boot", "default", "troubleshooting")
    ]
    
    for prompt, user_id, task_type in test_prompts:
        print(f"\nOriginal: {prompt}")
        print(f"Task: {task_type}")
        
        # Enrich the prompt
        enriched = enricher.enrich_prompt(
            prompt=prompt,
            user_id=user_id,
            task_type=task_type
        )
        
        if enriched != prompt:
            print("Enriched with context:")
            print(enriched[:300] + "..." if len(enriched) > 300 else enriched)
        else:
            print("No enrichment available")
        
        # Build RAG context
        rag_context = enricher.build_rag_context(prompt, user_id)
        if rag_context.get('retrieved_context'):
            print(f"RAG context sections: {list(rag_context['retrieved_context'].keys())}")
    
    print("\n" + "=" * 60)
    print("✨ Context enricher ready to inform AI decisions!")


if __name__ == "__main__":
    test_context_enricher()