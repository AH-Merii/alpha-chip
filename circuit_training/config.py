# Copyright 2021 The Circuit Training Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Configuration dataclasses for circuit training."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


class ValidationError(ValueError):
    """Raised when configuration validation fails."""

    pass


def _validate_range(
    value: float | int,
    name: str,
    ge: float | None = None,
    gt: float | None = None,
    le: float | None = None,
    lt: float | None = None,
) -> None:
    """Validate that a value is within a range."""
    if ge is not None and value < ge:
        raise ValidationError(f"{name} must be >= {ge}, got {value}")
    if gt is not None and value <= gt:
        raise ValidationError(f"{name} must be > {gt}, got {value}")
    if le is not None and value > le:
        raise ValidationError(f"{name} must be <= {le}, got {value}")
    if lt is not None and value >= lt:
        raise ValidationError(f"{name} must be < {lt}, got {value}")


def _validate_literal(value: str, name: str, options: tuple[str, ...]) -> None:
    """Validate that a value is one of the allowed options."""
    if value not in options:
        raise ValidationError(f"{name} must be one of {options}, got '{value}'")


@dataclass(frozen=True)
class EnvironmentConfig:
    """Configuration for the circuit training environment."""

    # File paths
    netlist_file: Path | str
    init_placement: Path | str | None = None
    blockage_file: Path | str | None = None

    # Placer mode
    std_cell_placer_mode: Literal["fd", "dreamplace"] = "fd"

    # Grid configuration
    grid_cols: int = 35
    grid_rows: int = 33

    # Cost weights (must be non-negative)
    wirelength_weight: float = 1.0
    density_weight: float = 1.0
    congestion_weight: float = 0.5

    # Placement options
    node_order: Literal[
        "descending_size_macro_first",
        "random",
        "sequential",
    ] = "descending_size_macro_first"
    save_placement: bool = False
    save_best_cost: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Convert string paths to Path objects
        object.__setattr__(self, "netlist_file", Path(self.netlist_file))
        if self.init_placement is not None:
            object.__setattr__(self, "init_placement", Path(self.init_placement))
        if self.blockage_file is not None:
            object.__setattr__(self, "blockage_file", Path(self.blockage_file))

        # Validate placer mode
        _validate_literal(
            self.std_cell_placer_mode, "std_cell_placer_mode", ("fd", "dreamplace")
        )

        # Validate grid dimensions
        _validate_range(self.grid_cols, "grid_cols", ge=1, le=512)
        _validate_range(self.grid_rows, "grid_rows", ge=1, le=512)

        # Validate weights
        _validate_range(self.wirelength_weight, "wirelength_weight", ge=0.0)
        _validate_range(self.density_weight, "density_weight", ge=0.0)
        _validate_range(self.congestion_weight, "congestion_weight", ge=0.0)

        # Validate node order
        _validate_literal(
            self.node_order,
            "node_order",
            ("descending_size_macro_first", "random", "sequential"),
        )

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        # Convert Path objects to strings for JSON serialization
        d["netlist_file"] = str(d["netlist_file"])
        if d["init_placement"] is not None:
            d["init_placement"] = str(d["init_placement"])
        if d["blockage_file"] is not None:
            d["blockage_file"] = str(d["blockage_file"])
        return d

    def model_dump_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump())


@dataclass(frozen=True)
class TrainingConfig:
    """Configuration for PPO training."""

    # Training loop
    num_iterations: int = 1000
    num_episodes_per_iteration: int = 256
    batch_size: int = 128
    num_epochs: int = 4

    # Optimizer
    learning_rate: float = 4e-4
    gradient_clipping: float = 1.0

    # PPO hyperparameters
    clip_epsilon: float = 0.2
    entropy_coef: float = 0.01
    value_loss_coef: float = 0.5
    discount_factor: float = 1.0

    # Sequence
    sequence_length: int = 134

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        _validate_range(self.num_iterations, "num_iterations", ge=1)
        _validate_range(
            self.num_episodes_per_iteration, "num_episodes_per_iteration", ge=1
        )
        _validate_range(self.batch_size, "batch_size", ge=1)
        _validate_range(self.num_epochs, "num_epochs", ge=1)

        _validate_range(self.learning_rate, "learning_rate", gt=0, lt=1)
        _validate_range(self.gradient_clipping, "gradient_clipping", gt=0)

        _validate_range(self.clip_epsilon, "clip_epsilon", gt=0, lt=1)
        _validate_range(self.entropy_coef, "entropy_coef", ge=0)
        _validate_range(self.value_loss_coef, "value_loss_coef", ge=0)
        _validate_range(self.discount_factor, "discount_factor", ge=0, le=1)

        _validate_range(self.sequence_length, "sequence_length", ge=1)

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def model_dump_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump())


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for the GCN model."""

    # GCN architecture
    num_gcn_layers: int = 3
    gcn_node_dim: int = 8
    edge_fc_layers: int = 1

    # Policy head
    max_grid_size: int = 128

    # Noise for exploration
    dirichlet_alpha: float = 0.1
    policy_noise_weight: float = 0.0

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        _validate_range(self.num_gcn_layers, "num_gcn_layers", ge=1, le=10)
        _validate_range(self.gcn_node_dim, "gcn_node_dim", ge=1, le=256)
        _validate_range(self.edge_fc_layers, "edge_fc_layers", ge=1, le=5)

        _validate_range(self.max_grid_size, "max_grid_size", ge=16, le=512)

        _validate_range(self.dirichlet_alpha, "dirichlet_alpha", gt=0, lt=1)
        _validate_range(self.policy_noise_weight, "policy_noise_weight", ge=0, le=1)

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def model_dump_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump())


@dataclass(frozen=True)
class DistributedConfig:
    """Configuration for distributed training."""

    # Reverb server
    replay_buffer_address: str = "localhost:8008"
    variable_container_address: str = "localhost:8008"

    # Collection
    num_collectors: int = 20
    task_id: int = 0

    # Hardware
    use_gpu: bool = True
    use_tpu: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        _validate_range(self.num_collectors, "num_collectors", ge=1)
        _validate_range(self.task_id, "task_id", ge=0)

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def model_dump_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump())


@dataclass(frozen=True)
class ExperimentConfig:
    """Complete experiment configuration."""

    environment: EnvironmentConfig
    training: TrainingConfig
    model: ModelConfig
    distributed: DistributedConfig = field(default_factory=DistributedConfig)

    # Experiment metadata
    experiment_name: str = "circuit_training"
    seed: int = 42
    root_dir: Path | str = "./logs"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Convert root_dir to Path
        object.__setattr__(self, "root_dir", Path(self.root_dir))

        # Validate seed
        _validate_range(self.seed, "seed", ge=0)

        # Validate sequence length matches grid size
        max_actions = self.model.max_grid_size**2
        if self.training.sequence_length > max_actions:
            raise ValidationError(
                f"sequence_length ({self.training.sequence_length}) cannot exceed "
                f"max_grid_size^2 ({max_actions})"
            )

    def model_dump(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "environment": self.environment.model_dump(),
            "training": self.training.model_dump(),
            "model": self.model.model_dump(),
            "distributed": self.distributed.model_dump(),
            "experiment_name": self.experiment_name,
            "seed": self.seed,
            "root_dir": str(self.root_dir),
        }

    def model_dump_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump())
