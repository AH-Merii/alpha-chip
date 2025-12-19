"""Shared test fixtures and configuration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest


if TYPE_CHECKING:
    from circuit_training.config import EnvironmentConfig, ExperimentConfig


# Test data paths
TEST_DATA_DIR = (
    Path(__file__).parent.parent / "circuit_training" / "environment" / "test_data"
)
ARIANE_NETLIST = TEST_DATA_DIR / "ariane" / "netlist.pb.txt"
ARIANE_PLACEMENT = TEST_DATA_DIR / "ariane" / "initial.plc"
MEP_NETLIST = TEST_DATA_DIR / "mep_room" / "netlist.pb.txt"
MEP_PLACEMENT = TEST_DATA_DIR / "mep_room" / "initial.plc"


@pytest.fixture
def ariane_netlist_path() -> Path:
    """Path to Ariane RISC-V netlist."""
    assert ARIANE_NETLIST.exists(), f"Test data not found: {ARIANE_NETLIST}"
    return ARIANE_NETLIST


@pytest.fixture
def ariane_placement_path() -> Path:
    """Path to Ariane initial placement."""
    assert ARIANE_PLACEMENT.exists(), f"Test data not found: {ARIANE_PLACEMENT}"
    return ARIANE_PLACEMENT


@pytest.fixture
def mep_netlist_path() -> Path:
    """Path to MEP room netlist."""
    if not MEP_NETLIST.exists():
        pytest.skip("MEP test data not available")
    return MEP_NETLIST


@pytest.fixture
def env_config(
    ariane_netlist_path: Path, ariane_placement_path: Path
) -> EnvironmentConfig:
    """Default environment configuration for testing."""
    from circuit_training.config import EnvironmentConfig

    return EnvironmentConfig(
        netlist_file=ariane_netlist_path,
        init_placement=ariane_placement_path,
        std_cell_placer_mode="fd",
    )


@pytest.fixture
def experiment_config(env_config: EnvironmentConfig) -> ExperimentConfig:
    """Default experiment configuration for testing."""
    from circuit_training.config import (
        ExperimentConfig,
        ModelConfig,
        TrainingConfig,
    )

    return ExperimentConfig(
        environment=env_config,
        training=TrainingConfig(num_iterations=2, batch_size=4),
        model=ModelConfig(num_gcn_layers=1, gcn_node_dim=4),
        experiment_name="test_experiment",
    )


@pytest.fixture
def random_observation() -> dict[str, np.ndarray]:
    """Random observation for model testing."""
    max_nodes = 1000
    max_edges = 5000

    return {
        "netlist_index": np.array([0], dtype=np.int32),
        "current_node": np.array([0], dtype=np.int32),
        "mask": np.ones((128 * 128,), dtype=np.int32),
        "locations_x": np.random.rand(1, max_nodes).astype(np.float32),
        "locations_y": np.random.rand(1, max_nodes).astype(np.float32),
        "is_node_placed": np.zeros((1, max_nodes), dtype=np.float32),
        "macros_w": np.random.rand(1, max_nodes).astype(np.float32),
        "macros_h": np.random.rand(1, max_nodes).astype(np.float32),
        "node_types": np.zeros((1, max_nodes), dtype=np.float32),
        "sparse_adj_i": np.random.randint(0, max_nodes, (1, max_edges)).astype(
            np.int32
        ),
        "sparse_adj_j": np.random.randint(0, max_nodes, (1, max_edges)).astype(
            np.int32
        ),
        "sparse_adj_weight": np.random.rand(1, max_edges).astype(np.float32),
    }


# Markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "gpu: marks tests requiring GPU")
    config.addinivalue_line("markers", "integration: marks integration tests")
