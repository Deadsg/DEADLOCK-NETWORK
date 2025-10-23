# DQN Mining Equations

This document outlines the core equations used in the DQN-based mining system.

## Q-Learning Update Rule

The fundamental Q-learning update rule is:

```
Q(s, a) = r + γ * max(Q'(s', a'))
```

Where:
- `Q(s, a)` is the Q-value for state `s` and action `a`.
- `r` is the reward.
- `γ` is the discount factor.
- `Q'(s', a')` is the future Q-value for the next state `s'` and action `a'`.

## Reward Calculation

The reward for a mining action is calculated as:

```
reward = mining_effort / (difficulty + ϵ)
```

Where:
- `mining_effort` is a measure of the computational work done by the miner.
- `difficulty` is the current mining difficulty.
- `ϵ` is a small constant to prevent division by zero.

## Learning Update

The learning update for the neural network is:

```
update = α * (target - prediction)
```

Where:
- `α` is the learning rate.
- `target` is the target Q-value calculated from the Bellman equation.
- `prediction` is the Q-value predicted by the neural network.

## Emission Rate Adjustment

The token emission rate is adjusted based on the network's performance:

```
E(t+1) = E(t) * (1 - λ * (Q_avg / Q_max))
```

Where:
- `E(t)` is the emission rate at time `t`.
- `λ` is the decay factor.
- `Q_avg` is the average Q-value across all miners.
- `Q_max` is the maximum Q-value.
