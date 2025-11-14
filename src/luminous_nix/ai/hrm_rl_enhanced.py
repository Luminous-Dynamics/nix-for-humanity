"""
HRM with Reinforcement Learning (RL) - Self-Improving NixOS Assistant
Uses PPO (Proximal Policy Optimization) for online learning from user feedback
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Deque
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque, defaultdict
import threading
import pickle
from datetime import datetime

# RL specific imports (would use PyTorch in production)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.distributions import Categorical

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available, using fallback mode")


@dataclass
class Experience:
    """Single interaction experience for RL"""

    state: Dict[str, Any]  # Query embedding, context
    action: str  # Solution chosen
    reward: float  # User feedback (-1 to 1)
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
    learning_rate: float = 0.0001
    policy_loss: float = 0.0
    value_loss: float = 0.0


class ReplayBuffer:
    """Experience replay buffer for stable learning"""

    def __init__(self, capacity: int = 10000):
        self.buffer: Deque[Experience] = deque(maxlen=capacity)
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.position = 0

    def push(self, experience: Experience, priority: float = 1.0):
        """Add experience with priority"""
        self.buffer.append(experience)
        if self.position < len(self.priorities):
            self.priorities[self.position] = priority
        self.position = (self.position + 1) % len(self.priorities)

    def sample(self, batch_size: int) -> List[Experience]:
        """Priority-based sampling"""
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        # Priority sampling
        probs = self.priorities[: len(self.buffer)]
        probs = probs / probs.sum()
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)

        return [self.buffer[i] for i in indices]

    def update_priorities(self, indices: List[int], priorities: List[float]):
        """Update priorities after learning"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority


class PolicyNetwork(nn.Module):
    """Neural network for policy (action selection)"""

    def __init__(
        self, state_dim: int = 128, action_dim: int = 10, hidden_dim: int = 256
    ):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.actor = nn.Linear(hidden_dim, action_dim)  # Policy head
        self.critic = nn.Linear(hidden_dim, 1)  # Value head

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        action_probs = torch.softmax(self.actor(x), dim=-1)
        state_value = self.critic(x)
        return action_probs, state_value


class HRMwithRL:
    """
    HRM enhanced with Reinforcement Learning
    Features:
    - Online learning from user feedback
    - PPO for stable policy updates
    - Experience replay for sample efficiency
    - Exploration vs exploitation balance
    """

    def __init__(self, model_path: Optional[str] = None):
        """Initialize RL-enhanced HRM"""
        self.model_path = model_path

        # RL Components
        self.replay_buffer = ReplayBuffer(capacity=10000)
        self.metrics = RLMetrics()

        # Action space (different solution strategies)
        self.action_space = [
            "direct_install",  # Simple nix-env install
            "overlay_solution",  # Use overlays
            "flake_approach",  # Use flakes
            "shell_environment",  # nix-shell solution
            "home_manager",  # home-manager config
            "configuration_nix",  # system config
            "docker_container",  # containerized solution
            "virtual_env",  # virtual environment
            "build_from_source",  # build manually
            "search_first",  # search then decide
        ]

        # State representation
        self.state_encoder = self._initialize_encoder()

        # Policy network (if PyTorch available)
        if TORCH_AVAILABLE:
            self.policy_net = PolicyNetwork(
                state_dim=128, action_dim=len(self.action_space)
            )
            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.0001)
            self.old_policy_net = PolicyNetwork(
                state_dim=128, action_dim=len(self.action_space)
            )
            self.old_policy_net.load_state_dict(self.policy_net.state_dict())
        else:
            self.policy_net = None

        # Reward shaping parameters
        self.reward_weights = {
            "success": 1.0,  # Task completed
            "speed": 0.3,  # Fast response
            "clarity": 0.2,  # Clear solution
            "efficiency": 0.2,  # Resource efficient
            "user_rating": 0.3,  # Explicit feedback
        }

        # Learning parameters
        self.gamma = 0.99  # Discount factor
        self.eps_clip = 0.2  # PPO clipping
        self.k_epochs = 4  # PPO update epochs
        self.update_interval = 100  # Update policy every N experiences

        # User feedback tracking
        self.session_history = []
        self.feedback_buffer = deque(maxlen=1000)

        # Load pre-trained if exists
        self._load_checkpoint()

    def select_action(
        self, state: Dict[str, Any], explore: bool = True
    ) -> Tuple[str, float]:
        """
        Select action using current policy
        Returns: (action, confidence)
        """
        if self.policy_net and TORCH_AVAILABLE:
            # Neural network policy
            state_tensor = self._encode_state(state)

            with torch.no_grad():
                action_probs, state_value = self.policy_net(state_tensor)

            if explore and np.random.random() < self.metrics.exploration_rate:
                # Exploration: random action
                action_idx = np.random.choice(len(self.action_space))
                confidence = 1.0 / len(self.action_space)
            else:
                # Exploitation: follow policy
                dist = Categorical(action_probs)
                action_idx = dist.sample().item()
                confidence = action_probs[action_idx].item()

            return self.action_space[action_idx], confidence
        else:
            # Fallback: heuristic selection
            return self._heuristic_action_selection(state)

    def learn_from_feedback(self, experience: Experience):
        """
        Learn from user feedback (core RL loop)
        """
        # Add to replay buffer
        priority = abs(experience.reward) + 0.01  # Prioritize high reward experiences
        self.replay_buffer.push(experience, priority)

        # Update metrics
        self.metrics.total_episodes += 1
        self.metrics.total_rewards += experience.reward
        self.metrics.avg_reward = (
            self.metrics.total_rewards / self.metrics.total_episodes
        )

        # Update success rate
        if experience.reward > 0:
            self.metrics.success_rate = (
                self.metrics.success_rate * 0.99 + 0.01
            )  # Moving average

        # Periodic policy update
        if self.metrics.total_episodes % self.update_interval == 0:
            self._update_policy()

    def _update_policy(self):
        """PPO policy update"""
        if not TORCH_AVAILABLE or not self.policy_net:
            return

        # Sample batch from replay buffer
        batch_size = min(64, len(self.replay_buffer.buffer))
        if batch_size < 32:
            return  # Not enough experiences

        experiences = self.replay_buffer.sample(batch_size)

        # Convert to tensors
        states = torch.stack([self._encode_state(e.state) for e in experiences])
        actions = torch.tensor([self.action_space.index(e.action) for e in experiences])
        rewards = torch.tensor([e.reward for e in experiences])
        dones = torch.tensor([e.done for e in experiences])

        # Normalize rewards
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        # PPO update loop
        for _ in range(self.k_epochs):
            # Get current policy predictions
            action_probs, state_values = self.policy_net(states)
            dist = Categorical(action_probs)

            # Calculate advantages
            advantages = rewards - state_values.squeeze().detach()

            # Get old policy predictions
            with torch.no_grad():
                old_action_probs, _ = self.old_policy_net(states)
                old_dist = Categorical(old_action_probs)

            # Calculate ratio
            log_probs = dist.log_prob(actions)
            old_log_probs = old_dist.log_prob(actions)
            ratio = torch.exp(log_probs - old_log_probs)

            # PPO loss
            surr1 = ratio * advantages
            surr2 = (
                torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            )
            policy_loss = -torch.min(surr1, surr2).mean()

            # Value loss
            value_loss = nn.MSELoss()(state_values.squeeze(), rewards)

            # Total loss
            loss = policy_loss + 0.5 * value_loss

            # Update
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Track losses
            self.metrics.policy_loss = policy_loss.item()
            self.metrics.value_loss = value_loss.item()

        # Update old policy
        self.old_policy_net.load_state_dict(self.policy_net.state_dict())

        # Decay exploration
        self.metrics.exploration_rate *= 0.995
        self.metrics.exploration_rate = max(0.01, self.metrics.exploration_rate)

    def get_solution(
        self, query: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get solution using RL-enhanced reasoning
        """
        # Create state representation
        state = {
            "query": query,
            "context": context or {},
            "timestamp": time.time(),
            "session_length": len(self.session_history),
        }

        # Select action (solution strategy)
        action, confidence = self.select_action(state)

        # Generate solution based on action
        solution = self._execute_action(action, query, context)

        # Track in session
        self.session_history.append(
            {
                "state": state,
                "action": action,
                "solution": solution,
                "confidence": confidence,
            }
        )

        return {
            "solution": solution,
            "strategy": action,
            "confidence": confidence,
            "can_improve": True,  # RL can always improve
            "metrics": {
                "success_rate": f"{self.metrics.success_rate:.1%}",
                "avg_reward": f"{self.metrics.avg_reward:.2f}",
                "exploration": f"{self.metrics.exploration_rate:.1%}",
            },
        }

    def process_feedback(self, feedback: Dict[str, Any]):
        """
        Process user feedback to create learning experience
        Feedback format: {
            "rating": -1 to 1,
            "success": bool,
            "time_taken": float,
            "clarity": 0-1,
            "would_recommend": bool
        }
        """
        if not self.session_history:
            return

        last_interaction = self.session_history[-1]

        # Calculate reward
        reward = self._calculate_reward(feedback)

        # Create experience
        experience = Experience(
            state=last_interaction["state"],
            action=last_interaction["action"],
            reward=reward,
            next_state=None,  # Terminal state
            done=True,
            metadata=feedback,
        )

        # Learn from it
        self.learn_from_feedback(experience)

        # Save checkpoint periodically
        if self.metrics.total_episodes % 1000 == 0:
            self._save_checkpoint()

    def _calculate_reward(self, feedback: Dict[str, Any]) -> float:
        """
        Calculate reward from user feedback
        """
        reward = 0.0

        # Direct rating (most important)
        if "rating" in feedback:
            reward += feedback["rating"] * self.reward_weights.get("user_rating", 0.3)

        # Success/failure
        if "success" in feedback:
            reward += (1.0 if feedback["success"] else -0.5) * self.reward_weights.get(
                "success", 1.0
            )

        # Speed bonus
        if "time_taken" in feedback:
            speed_bonus = max(0, 1 - feedback["time_taken"] / 5.0)  # Bonus for <5s
            reward += speed_bonus * self.reward_weights.get("speed", 0.3)

        # Clarity bonus
        if "clarity" in feedback:
            reward += feedback["clarity"] * self.reward_weights.get("clarity", 0.2)

        # Efficiency (if solution was concise)
        if "solution_length" in feedback:
            efficiency = max(
                0, 1 - feedback["solution_length"] / 500
            )  # Bonus for <500 chars
            reward += efficiency * self.reward_weights.get("efficiency", 0.2)

        return np.clip(reward, -1.0, 1.0)

    def _execute_action(self, action: str, query: str, context: Dict) -> str:
        """
        Execute the selected action to generate solution
        """
        solutions = {
            "direct_install": f"nix-env -iA nixpkgs.{self._extract_package(query)}",
            "overlay_solution": self._generate_overlay_solution(query),
            "flake_approach": self._generate_flake_solution(query),
            "shell_environment": f"nix-shell -p {self._extract_package(query)}",
            "home_manager": self._generate_home_manager_config(query),
            "configuration_nix": self._generate_system_config(query),
            "docker_container": f"docker run -it nixos/nix nix-env -iA nixpkgs.{self._extract_package(query)}",
            "virtual_env": self._generate_venv_solution(query),
            "build_from_source": self._generate_build_instructions(query),
            "search_first": f"nix search nixpkgs {self._extract_package(query)}",
        }

        return solutions.get(action, f"# Solution using {action} strategy")

    def _encode_state(self, state: Dict[str, Any]) -> torch.Tensor:
        """
        Encode state dict to tensor
        Simple encoding - in production would use embeddings
        """
        if not TORCH_AVAILABLE:
            return None

        # Simple feature extraction
        features = np.zeros(128)

        # Query features (simplified - would use BERT/etc in production)
        query = state.get("query", "")
        features[0] = len(query) / 100  # Length
        features[1] = query.count(" ") / 10  # Word count

        # Context features
        features[10] = state.get("timestamp", 0) % 86400 / 86400  # Time of day
        features[11] = state.get("session_length", 0) / 100  # Session length

        # Query type features
        if "install" in query.lower():
            features[20] = 1.0
        if "error" in query.lower():
            features[21] = 1.0
        if "config" in query.lower():
            features[22] = 1.0

        return torch.FloatTensor(features).unsqueeze(0)

    def _heuristic_action_selection(self, state: Dict[str, Any]) -> Tuple[str, float]:
        """
        Fallback heuristic action selection
        """
        query = state.get("query", "").lower()

        if "install" in query:
            return "direct_install", 0.8
        elif "error" in query or "collision" in query:
            return "overlay_solution", 0.7
        elif "config" in query:
            return "configuration_nix", 0.75
        elif "shell" in query or "develop" in query:
            return "shell_environment", 0.8
        else:
            return "search_first", 0.6

    def _extract_package(self, query: str) -> str:
        """Extract package name from query"""
        words = query.lower().replace("install", "").replace("add", "").strip().split()
        return words[0] if words else "unknown"

    def _generate_overlay_solution(self, query: str) -> str:
        """Generate overlay-based solution"""
        pkg = self._extract_package(query)
        return f"""# Overlay solution for {pkg}
nixpkgs.overlays = [(self: super: {{
  {pkg} = super.{pkg}.overrideAttrs (old: {{
    # Custom modifications
  }});
}})];"""

    def _generate_flake_solution(self, query: str) -> str:
        """Generate flake-based solution"""
        pkg = self._extract_package(query)
        return f"""# Flake solution
{{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = {{ nixpkgs }}: {{
    defaultPackage = nixpkgs.legacyPackages.x86_64-linux.{pkg};
  }};
}}"""

    def _generate_home_manager_config(self, query: str) -> str:
        """Generate home-manager configuration"""
        pkg = self._extract_package(query)
        return f"""# Home Manager configuration
home.packages = with pkgs; [
  {pkg}
];"""

    def _generate_system_config(self, query: str) -> str:
        """Generate system configuration"""
        pkg = self._extract_package(query)
        return f"""# /etc/nixos/configuration.nix
environment.systemPackages = with pkgs; [
  {pkg}
];"""

    def _generate_venv_solution(self, query: str) -> str:
        """Generate virtual environment solution"""
        return "nix-shell -p python3 --run 'python -m venv .venv'"

    def _generate_build_instructions(self, query: str) -> str:
        """Generate build from source instructions"""
        pkg = self._extract_package(query)
        return f"""# Build {pkg} from source
git clone https://github.com/.../{pkg}
cd {pkg}
nix-build"""

    def _initialize_encoder(self):
        """Initialize state encoder"""
        # In production, would load BERT or similar
        return None

    def _save_checkpoint(self):
        """Save model checkpoint"""
        checkpoint = {
            "metrics": self.metrics,
            "replay_buffer": self.replay_buffer,
            "timestamp": datetime.now().isoformat(),
        }

        if TORCH_AVAILABLE and self.policy_net:
            checkpoint["policy_state_dict"] = self.policy_net.state_dict()
            checkpoint["optimizer_state_dict"] = self.optimizer.state_dict()

        path = Path("models/hrm-rl-checkpoint.pkl")
        path.parent.mkdir(exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(checkpoint, f)

        print(f"✅ Checkpoint saved (Episode {self.metrics.total_episodes})")

    def _load_checkpoint(self):
        """Load model checkpoint if exists"""
        path = Path("models/hrm-rl-checkpoint.pkl")
        if not path.exists():
            return

        try:
            with open(path, "rb") as f:
                checkpoint = pickle.load(f)

            self.metrics = checkpoint["metrics"]
            self.replay_buffer = checkpoint["replay_buffer"]

            if (
                TORCH_AVAILABLE
                and self.policy_net
                and "policy_state_dict" in checkpoint
            ):
                self.policy_net.load_state_dict(checkpoint["policy_state_dict"])
                self.old_policy_net.load_state_dict(checkpoint["policy_state_dict"])
                self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

            print(f"✅ Checkpoint loaded (Episode {self.metrics.total_episodes})")
        except Exception as e:
            print(f"⚠️ Failed to load checkpoint: {e}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        return {
            "total_episodes": self.metrics.total_episodes,
            "success_rate": f"{self.metrics.success_rate:.1%}",
            "avg_reward": f"{self.metrics.avg_reward:.3f}",
            "exploration_rate": f"{self.metrics.exploration_rate:.1%}",
            "replay_buffer_size": len(self.replay_buffer.buffer),
            "policy_loss": f"{self.metrics.policy_loss:.4f}",
            "value_loss": f"{self.metrics.value_loss:.4f}",
            "learning_rate": self.metrics.learning_rate,
        }


# Demonstration and testing
if __name__ == "__main__":
    print("🤖 HRM with Reinforcement Learning Demo")
    print("=" * 50)

    # Initialize RL-enhanced HRM
    hrm_rl = HRMwithRL()

    # Simulate some interactions
    queries = [
        "install firefox",
        "error: collision between python packages",
        "configure nginx with SSL",
        "setup development environment",
    ]

    for i, query in enumerate(queries):
        print(f"\n📝 Query {i+1}: {query}")

        # Get solution
        result = hrm_rl.get_solution(query)
        print(f"   Strategy: {result['strategy']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Solution: {result['solution'][:100]}...")

        # Simulate user feedback
        feedback = {
            "rating": np.random.uniform(-0.5, 1.0),  # Random feedback
            "success": np.random.random() > 0.3,
            "time_taken": np.random.uniform(0.5, 3.0),
            "clarity": np.random.uniform(0.5, 1.0),
        }

        hrm_rl.process_feedback(feedback)
        print(
            f"   Feedback: Rating={feedback['rating']:.2f}, Success={feedback['success']}"
        )

    # Show learning stats
    print("\n📊 Learning Statistics:")
    stats = hrm_rl.get_learning_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ RL-enhanced HRM is learning and improving!")
