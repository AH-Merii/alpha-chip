"""Tests for configuration dataclass models."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from circuit_training.config import ValidationError


class TestEnvironmentConfig:
    """Test environment configuration model."""

    def test_valid_config(self):
        """Valid configuration should be accepted."""
        from circuit_training.config import EnvironmentConfig

        config = EnvironmentConfig(
            netlist_file=Path(
                "circuit_training/environment/test_data/ariane/netlist.pb.txt"
            ),
            std_cell_placer_mode="fd",
            wirelength_weight=1.0,
        )
        assert config.std_cell_placer_mode == "fd"

    def test_invalid_placer_mode_rejected(self):
        """Invalid placer mode should raise error."""
        from circuit_training.config import EnvironmentConfig

        with pytest.raises(ValidationError):
            EnvironmentConfig(
                netlist_file=Path("test.pb.txt"),
                std_cell_placer_mode="invalid_mode",
            )

    def test_negative_weights_rejected(self):
        """Negative weights should raise error."""
        from circuit_training.config import EnvironmentConfig

        with pytest.raises(ValidationError):
            EnvironmentConfig(
                netlist_file=Path("test.pb.txt"),
                wirelength_weight=-1.0,
            )

    def test_config_immutable(self):
        """Config should be immutable after creation."""
        from circuit_training.config import EnvironmentConfig

        config = EnvironmentConfig(
            netlist_file=Path(
                "circuit_training/environment/test_data/ariane/netlist.pb.txt"
            ),
        )
        with pytest.raises(FrozenInstanceError):
            config.wirelength_weight = 2.0


class TestTrainingConfig:
    """Test training configuration model."""

    def test_valid_training_config(self):
        """Valid training config should be accepted."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig(
            num_iterations=100,
            batch_size=64,
            learning_rate=1e-4,
        )
        assert config.num_iterations == 100

    def test_default_values(self):
        """Default values should be sensible."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig()
        assert config.num_iterations > 0
        assert config.batch_size > 0
        assert 0 < config.learning_rate < 1

    def test_invalid_batch_size_rejected(self):
        """Zero or negative batch size should raise error."""
        from circuit_training.config import TrainingConfig

        with pytest.raises(ValidationError):
            TrainingConfig(batch_size=0)

        with pytest.raises(ValidationError):
            TrainingConfig(batch_size=-1)


class TestConfigSerialization:
    """Test config serialization/deserialization."""

    def test_to_dict(self):
        """Config should serialize to dict."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig(num_iterations=50)
        d = config.model_dump()
        assert isinstance(d, dict)
        assert d["num_iterations"] == 50

    def test_to_json(self):
        """Config should serialize to JSON."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig()
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)

    def test_from_dict(self):
        """Config should deserialize from dict."""
        from circuit_training.config import TrainingConfig

        d = {"num_iterations": 200, "batch_size": 256}
        config = TrainingConfig(**d)
        assert config.num_iterations == 200
