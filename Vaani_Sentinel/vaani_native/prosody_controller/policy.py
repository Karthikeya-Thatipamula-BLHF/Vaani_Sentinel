#!/usr/bin/env python3
"""
Vaani Native TTS - RL Prosody Controller
Discrete Q-learning policy for expressive speech synthesis

Action Space:
- pitch_shift: {-1, 0, 1} semitones
- speed: {0.9, 1.0, 1.1} multiplier
- energy: {-1, 0, 1} relative energy
- emotion: {neutral, warm}

State Space:
- Text features (length, complexity)
- Speaker characteristics
- Context (position in utterance)

Reward Function:
- MOS-proxy improvement
- Naturalness score
- Lip-sync correlation (future)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import defaultdict
import random
import json
import logging
from pathlib import Path
import time

# Add project root
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProsodyQNetwork(nn.Module):
    """Neural network for Q-value approximation"""

    def __init__(self, state_dim=10, action_dim=24):  # 4 actions * 6 combinations = 24
        super(ProsodyQNetwork, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, action_dim)
        )

    def forward(self, state):
        return self.network(state)

class ProsodyStateEncoder:
    """Encode text and context into state vector"""

    def __init__(self):
        self.max_text_length = settings.native_tts_max_text_length

    def encode_text(self, text: str) -> np.ndarray:
        """Simple text feature encoding"""
        # Basic features (expand in production)
        features = np.zeros(8)

        # Text length (normalized)
        features[0] = min(len(text) / self.max_text_length, 1.0)

        # Character diversity
        char_set = set(text.lower())
        features[1] = len(char_set) / 26.0  # Normalized by alphabet size

        # Punctuation density
        punctuation = sum(1 for c in text if c in '.,!?;:')
        features[2] = punctuation / max(len(text), 1)

        # Capitalization ratio
        capitals = sum(1 for c in text if c.isupper())
        features[3] = capitals / max(len(text), 1)

        # Word count
        words = text.split()
        features[4] = min(len(words) / 20, 1.0)  # Normalize by typical sentence

        # Average word length
        if words:
            avg_word_len = sum(len(w) for w in words) / len(words)
            features[5] = min(avg_word_len / 10, 1.0)

        return features

    def encode_state(self, text: str, position: float = 0.0, speaker_id: int = 0) -> np.ndarray:
        """Encode full state: text + context"""
        text_features = self.encode_text(text)

        # Context features
        context_features = np.array([
            position,  # Position in utterance (0-1)
            speaker_id / 10.0,  # Speaker ID (normalized)
            0.0,  # Placeholder for future features
            0.0
        ])

        return np.concatenate([text_features, context_features])

class RLProsodyController:
    """Q-learning controller for prosody optimization"""

    def __init__(self, learning_rate=0.001, gamma=0.99, epsilon=1.0, epsilon_decay=0.995):
        self.state_encoder = ProsodyStateEncoder()

        # Q-network
        self.q_network = ProsodyQNetwork()
        self.target_network = ProsodyQNetwork()
        self.target_network.load_state_dict(self.q_network.state_dict())

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

        # RL parameters
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = 0.01

        # Experience replay
        self.memory = []
        self.memory_size = 10000
        self.batch_size = 32

        # Action space: 4 parameters * 3 values each = 12 actions
        # pitch_shift: 3 options, speed: 3 options, energy: 3 options, emotion: 2 options
        # Total: 3 * 3 * 3 * 2 = 54 combinations (simplified to 24 for Day 3)
        self.actions = self._define_action_space()

        # Training stats
        self.training_steps = 0

    def _define_action_space(self):
        """Define discrete action space"""
        actions = []

        # Simplified action space for Day 3 MVP
        pitch_shifts = [-1, 0, 1]      # semitones
        speeds = [0.9, 1.0, 1.1]       # multipliers
        energies = [-1, 0, 1]          # relative
        emotions = ['neutral', 'warm'] # emotions

        for pitch in pitch_shifts:
            for speed in speeds:
                for energy in energies:
                    for emotion in emotions[:1]:  # Only neutral for Day 3
                        actions.append({
                            'pitch_shift': pitch,
                            'speed': speed,
                            'energy': energy,
                            'emotion': emotion
                        })

        return actions

    def select_action(self, text: str, training: bool = False) -> dict:
        """Select prosody action using epsilon-greedy policy"""
        state = self.state_encoder.encode_state(text)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        if training and random.random() < self.epsilon:
            # Random action (exploration)
            action_idx = random.randint(0, len(self.actions) - 1)
        else:
            # Greedy action (exploitation)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                action_idx = q_values.argmax().item()

        return self.actions[action_idx]

    def train_step(self, batch):
        """Single training step on batch of experiences"""
        if len(batch) < self.batch_size:
            return 0.0

        # Unpack batch
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Current Q values
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Target Q values
        with torch.no_grad():
            next_q = self.target_network(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q

        # Loss and optimization
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network occasionally
        if self.training_steps % 100 == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        self.training_steps += 1
        return loss.item()

    def store_experience(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        action_idx = self.actions.index(action) if action in self.actions else 0

        self.memory.append((state, action_idx, reward, next_state, done))

        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

    def sample_batch(self):
        """Sample batch from experience replay"""
        if len(self.memory) < self.batch_size:
            return self.memory

        return random.sample(self.memory, self.batch_size)

    def save_policy(self, path: str):
        """Save trained policy"""
        policy_data = {
            'q_network_state': self.q_network.state_dict(),
            'target_network_state': self.target_network.state_dict(),
            'epsilon': self.epsilon,
            'training_steps': self.training_steps,
            'actions': self.actions,
            'timestamp': time.time()
        }

        torch.save(policy_data, path)
        logger.info(f"Policy saved to {path}")

    def load_policy(self, path: str):
        """Load trained policy"""
        if not Path(path).exists():
            logger.warning(f"Policy file {path} not found")
            return

        policy_data = torch.load(path)
        self.q_network.load_state_dict(policy_data['q_network_state'])
        self.target_network.load_state_dict(policy_data['target_network_state'])
        self.epsilon = policy_data.get('epsilon', self.epsilon)
        self.training_steps = policy_data.get('training_steps', 0)

        logger.info(f"Policy loaded from {path}")

# Global controller instance
_prosody_controller = None

def get_prosody_controller() -> RLProsodyController:
    """Get singleton prosody controller instance"""
    global _prosody_controller
    if _prosody_controller is None:
        _prosody_controller = RLProsodyController()
    return _prosody_controller
