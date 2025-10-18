
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import namedtuple, deque
import random

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class ReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.memory = deque(maxlen=buffer_size)
        self.Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

    def add(self, state, action, reward, next_state, done):
        transition = self.Transition(state, action, reward, next_state, done)
        self.memory.append(transition)

    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        return self.Transition(*zip(*batch))

class DQNAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.99, buffer_size=10000, batch_size=64, epsilon=1.0, min_epsilon=0.01, epsilon_decay=0.995, target_update_frequency=100):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.batch_size = batch_size
        self.buffer = ReplayBuffer(buffer_size)
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay
        self.target_update_frequency = target_update_frequency
        self.total_steps = 0

        self.q_network = QNetwork(state_size, action_size)
        self.target_network = QNetwork(state_size, action_size)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            with torch.no_grad():
                q_values = self.q_network(state)
                return torch.argmax(q_values).item()

    def train(self):
        if len(self.buffer.memory) < self.batch_size:
            return

        transitions = self.buffer.sample(self.batch_size)
        batch = self.Transition(*zip(*transitions))

        states = torch.cat(batch.state)
        actions = torch.tensor(batch.action, dtype=torch.int64).view(-1, 1)
        rewards = torch.tensor(batch.reward, dtype=torch.float32).view(-1, 1)
        next_states = torch.cat(batch.next_state)
        dones = torch.tensor(batch.done, dtype=torch.float32).view(-1, 1)

        q_values = self.q_network(states).gather(1, actions)

        next_q_values = self.target_network(next_states).detach()
        max_next_q_values = torch.max(next_q_values, dim=1, keepdim=True).values
        td_targets = rewards + self.gamma * (1 - dones) * max_next_q_values

        loss = self.loss_fn(q_values, td_targets)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.total_steps += 1
        if self.total_steps % self.target_update_frequency == 0:
            self.update_target_network()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
