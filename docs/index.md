# Circuit Training

**Reinforcement Learning for Chip Placement**

Circuit Training is an open-source framework for generating chip floorplans using
distributed deep reinforcement learning.

## Features

- **Deep RL Placement**: Uses PPO to learn optimal macro placement
- **Distributed Training**: Scales to hundreds of collection workers
- **Multi-objective**: Optimizes wirelength, congestion, and density
- **Configurable**: Extensive configuration via Pydantic models

## Quick Start

```bash
# Install with uv
uv pip install circuit-training

# Or install from source
git clone https://github.com/google-research/circuit_training.git
cd circuit_training
uv sync

# Run training
ct-train --config configs/ariane.yaml
```

## Installation

### Requirements

- Python 3.11+
- TensorFlow 2.15+
- TF-Agents 0.19+

### From PyPI

```bash
pip install circuit-training
```

### From Source

```bash
git clone https://github.com/google-research/circuit_training.git
cd circuit_training
uv sync --dev
```

## Usage

### Environment

```python
from circuit_training.environment.environment import CircuitEnv

env = CircuitEnv(
    netlist_file="path/to/netlist.pb.txt",
    init_placement="path/to/initial.plc",
)

obs = env.reset()
done = False
while not done:
    action = env.action_space.sample()  # Your policy here
    obs, reward, done, info = env.step(action)
```

### Configuration

```python
from circuit_training.config import (
    EnvironmentConfig,
    TrainingConfig,
    ExperimentConfig,
)

env_config = EnvironmentConfig(
    netlist_file="path/to/netlist.pb.txt",
    std_cell_placer_mode="fd",
)

training_config = TrainingConfig(
    num_iterations=1000,
    batch_size=128,
)
```

## Citation

```bibtex
@article{mirhoseini2021graph,
  title={A graph placement methodology for fast chip design},
  author={Mirhoseini, Azalia and others},
  journal={Nature},
  year={2021}
}
```

## License

Apache 2.0 License. See [LICENSE](https://github.com/google-research/circuit_training/blob/main/LICENSE) for details.
