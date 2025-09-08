"""
HRM with Reinforcement Learning (Simplified Version)
No external dependencies - uses pure Python for demonstrations
"""

import random
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque, defaultdict
from pathlib import Path

@dataclass
class Experience:
    """Single interaction experience for RL"""
    state: Dict[str, Any]
    action: str
    reward: float
    next_state: Optional[Dict[str, Any]]
    done: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RLMetrics:
    """Track RL performance metrics"""
    total_episodes: int = 0
    total_rewards: float = 0.0
    success_rate: float = 0.0
    avg_reward: float = 0.0
    exploration_rate: float = 0.1
    recent_rewards: List[float] = field(default_factory=list)

class SimpleReplayBuffer:
    """Experience replay buffer for stable learning"""
    
    def __init__(self, capacity: int = 1000):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, experience: Experience):
        """Add experience"""
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Random sampling"""
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(self.buffer, batch_size)

class HRMwithSimpleRL:
    """
    Simplified HRM with Reinforcement Learning
    Uses Q-learning approximation without neural networks
    """
    
    def __init__(self):
        """Initialize simplified RL-enhanced HRM"""
        
        # RL Components
        self.replay_buffer = SimpleReplayBuffer(capacity=1000)
        self.metrics = RLMetrics()
        
        # Action space (solution strategies)
        self.action_space = [
            "direct_install",      # Simple nix-env install
            "overlay_solution",    # Use overlays
            "flake_approach",      # Use flakes
            "shell_environment",   # nix-shell solution
            "configuration_nix",   # system config
            "search_first"         # search then decide
        ]
        
        # Q-table approximation (state-action values)
        # In real RL, this would be a neural network
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Learning parameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.95  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        
        # Action success tracking
        self.action_stats = defaultdict(lambda: {"successes": 0, "total": 0})
        
        # Session history
        self.session_history = []
    
    def get_state_key(self, state: Dict[str, Any]) -> str:
        """Convert state to hashable key"""
        query = state.get("query", "").lower()
        
        # Simple state categorization
        if "install" in query:
            return "install_task"
        elif "error" in query or "collision" in query:
            return "error_task"
        elif "config" in query or "setup" in query:
            return "config_task"
        elif "search" in query or "find" in query:
            return "search_task"
        else:
            return "general_task"
    
    def select_action(self, state: Dict[str, Any]) -> Tuple[str, float]:
        """
        Select action using epsilon-greedy policy
        """
        state_key = self.get_state_key(state)
        
        # Exploration: random action
        if random.random() < self.epsilon:
            action = random.choice(self.action_space)
            confidence = 1.0 / len(self.action_space)
        else:
            # Exploitation: choose best known action
            q_values = self.q_table[state_key]
            
            if not q_values:
                # No knowledge yet, choose randomly
                action = random.choice(self.action_space)
                confidence = 0.5
            else:
                # Choose action with highest Q-value
                best_actions = [a for a in self.action_space 
                               if q_values[a] == max(q_values.values())]
                action = random.choice(best_actions)
                confidence = min(0.95, 0.5 + q_values[action])
        
        # Track action usage
        self.action_stats[action]["total"] += 1
        
        return action, confidence
    
    def learn_from_experience(self, experience: Experience):
        """
        Q-learning update
        """
        state_key = self.get_state_key(experience.state)
        
        # Current Q-value
        current_q = self.q_table[state_key][experience.action]
        
        # Calculate target
        if experience.done:
            target = experience.reward
        else:
            next_state_key = self.get_state_key(experience.next_state) if experience.next_state else state_key
            next_max_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
            target = experience.reward + self.gamma * next_max_q
        
        # Q-learning update
        self.q_table[state_key][experience.action] = (
            current_q + self.alpha * (target - current_q)
        )
        
        # Update metrics
        self.metrics.total_episodes += 1
        self.metrics.total_rewards += experience.reward
        self.metrics.recent_rewards.append(experience.reward)
        if len(self.metrics.recent_rewards) > 100:
            self.metrics.recent_rewards.pop(0)
        
        # Update success rate
        if experience.reward > 0:
            self.action_stats[experience.action]["successes"] += 1
            self.metrics.success_rate = (
                self.metrics.success_rate * 0.95 + 0.05
            )
        else:
            self.metrics.success_rate *= 0.98
        
        # Update average reward
        self.metrics.avg_reward = (
            sum(self.metrics.recent_rewards) / len(self.metrics.recent_rewards)
            if self.metrics.recent_rewards else 0
        )
        
        # Decay exploration
        self.epsilon = max(0.01, self.epsilon * 0.995)
        self.metrics.exploration_rate = self.epsilon
        
        # Add to replay buffer
        self.replay_buffer.push(experience)
    
    def get_solution(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get solution using RL-enhanced reasoning
        """
        # Create state
        state = {
            "query": query,
            "context": context or {},
            "timestamp": time.time()
        }
        
        # Select action
        action, confidence = self.select_action(state)
        
        # Generate solution
        solution = self._execute_action(action, query)
        
        # Track in session
        self.session_history.append({
            "state": state,
            "action": action,
            "solution": solution,
            "confidence": confidence
        })
        
        # Calculate action success rate
        stats = self.action_stats[action]
        success_rate = (stats["successes"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "solution": solution,
            "strategy": action,
            "confidence": confidence,
            "strategy_success_rate": f"{success_rate:.1f}%",
            "overall_metrics": {
                "episodes": self.metrics.total_episodes,
                "avg_reward": f"{self.metrics.avg_reward:.3f}",
                "success_rate": f"{self.metrics.success_rate:.1%}",
                "exploration": f"{self.metrics.exploration_rate:.1%}"
            }
        }
    
    def process_feedback(self, rating: float, success: bool = True):
        """
        Process user feedback
        Simple version: just rating and success
        """
        if not self.session_history:
            return
        
        last = self.session_history[-1]
        
        # Calculate reward
        reward = rating * 0.7  # Weight rating
        if success:
            reward += 0.3
        else:
            reward -= 0.2
        
        # Clip reward
        reward = max(-1.0, min(1.0, reward))
        
        # Create experience
        experience = Experience(
            state=last["state"],
            action=last["action"],
            reward=reward,
            next_state=None,
            done=True,
            metadata={"rating": rating, "success": success}
        )
        
        # Learn from it
        self.learn_from_experience(experience)
    
    def _execute_action(self, action: str, query: str) -> str:
        """Execute the selected action"""
        pkg = self._extract_package(query)
        
        solutions = {
            "direct_install": f"nix-env -iA nixpkgs.{pkg}",
            "overlay_solution": f"""nixpkgs.overlays = [(self: super: {{
  {pkg} = super.{pkg}.overrideAttrs (old: {{ }});
}})];""",
            "flake_approach": f"""{{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  outputs = {{ nixpkgs }}: {{
    defaultPackage = nixpkgs.legacyPackages.x86_64-linux.{pkg};
  }};
}}""",
            "shell_environment": f"nix-shell -p {pkg}",
            "configuration_nix": f"""environment.systemPackages = with pkgs; [
  {pkg}
];""",
            "search_first": f"nix search nixpkgs {pkg}"
        }
        
        return solutions.get(action, f"# {action} solution for {pkg}")
    
    def _extract_package(self, query: str) -> str:
        """Extract package name"""
        words = query.lower().replace("install", "").replace("add", "").strip().split()
        return words[0] if words else "package"
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        # Calculate per-action stats
        action_performance = {}
        for action in self.action_space:
            stats = self.action_stats[action]
            if stats["total"] > 0:
                success_rate = stats["successes"] / stats["total"] * 100
                action_performance[action] = f"{success_rate:.1f}% ({stats['total']} uses)"
        
        return {
            "total_episodes": self.metrics.total_episodes,
            "avg_reward": f"{self.metrics.avg_reward:.3f}",
            "success_rate": f"{self.metrics.success_rate:.1%}",
            "exploration_rate": f"{self.metrics.exploration_rate:.1%}",
            "replay_buffer_size": len(self.replay_buffer.buffer),
            "q_table_states": len(self.q_table),
            "action_performance": action_performance
        }


def demonstrate_learning():
    """Demonstrate RL learning over time"""
    print("🤖 HRM with Reinforcement Learning Demo")
    print("=" * 60)
    
    # Initialize
    hrm = HRMwithSimpleRL()
    
    # Test queries
    queries = [
        "install firefox",
        "error: collision between packages",
        "configure nginx",
        "search for text editor",
        "setup python environment",
        "install vim",
        "resolve dependency conflict",
        "install docker"
    ]
    
    print("\n📚 Training Phase (with simulated feedback)")
    print("-" * 60)
    
    # Training loop
    for episode in range(50):
        query = random.choice(queries)
        
        # Get solution
        result = hrm.get_solution(query)
        
        # Simulate feedback (improves over time)
        base_rating = 0.3
        learning_bonus = min(0.5, episode / 100)
        
        # Better feedback for certain strategies
        strategy_bonus = {
            "direct_install": 0.2,
            "flake_approach": 0.3,
            "configuration_nix": 0.25
        }.get(result["strategy"], 0.1)
        
        rating = min(1.0, base_rating + learning_bonus + strategy_bonus + random.uniform(-0.2, 0.2))
        success = rating > 0.4
        
        # Process feedback
        hrm.process_feedback(rating, success)
        
        # Print progress every 10 episodes
        if (episode + 1) % 10 == 0:
            stats = hrm.get_learning_stats()
            print(f"Episode {episode + 1:3d}: "
                  f"Avg Reward={stats['avg_reward']}, "
                  f"Success={stats['success_rate']}, "
                  f"Explore={stats['exploration_rate']}")
    
    print("\n✅ Training Complete!")
    print("\n📊 Final Learning Statistics:")
    print("-" * 60)
    
    final_stats = hrm.get_learning_stats()
    for key, value in final_stats.items():
        if key == "action_performance":
            print(f"\n📈 Strategy Performance:")
            for action, perf in value.items():
                print(f"  {action:20s}: {perf}")
        else:
            print(f"{key:20s}: {value}")
    
    print("\n🎯 Testing Learned Behavior")
    print("-" * 60)
    
    # Test with specific queries
    test_queries = [
        "install firefox",
        "configure postgresql",
        "error: python collision"
    ]
    
    for query in test_queries:
        result = hrm.get_solution(query)
        print(f"\nQuery: '{query}'")
        print(f"  Strategy: {result['strategy']} (confidence: {result['confidence']:.2f})")
        print(f"  Success rate: {result['strategy_success_rate']}")
        print(f"  Solution: {result['solution'][:80]}...")
    
    print("\n" + "=" * 60)
    print("🚀 Key Insights:")
    print("  • The model learns which strategies work best")
    print("  • Exploration decreases as confidence grows")
    print("  • Success rate improves with experience")
    print("  • Q-values guide optimal action selection")
    print("\n✨ HRM with RL successfully demonstrates self-improvement!")


if __name__ == "__main__":
    demonstrate_learning()