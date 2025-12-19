#!/usr/bin/env python3
"""Update version.py with new version from semantic-release."""
import re
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """Update the version in version.py."""
    version_file = Path(__file__).parent.parent / "circuit_training" / "version.py"
    content = version_file.read_text()

    # Update __version__
    content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        content,
    )

    # Update __rel_version__
    content = re.sub(
        r'__rel_version__ = "[^"]+"',
        f'__rel_version__ = "{new_version}"',
        content,
    )

    # Update __dev_version__
    content = re.sub(
        r'__dev_version__ = "[^"]+"',
        f'__dev_version__ = "{new_version}.dev"',
        content,
    )

    version_file.write_text(content)
    print(f"Updated version to {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_version.py <version>")
        sys.exit(1)

    update_version(sys.argv[1])
