"""
Parser for daemon.md files.
Converts the bracket-section format into structured data.
"""

import re
from pathlib import Path
from typing import Any


def parse_daemon_file(file_path: Path) -> dict[str, Any]:
    """Parse a daemon.md file into a structured dictionary."""
    content = file_path.read_text()

    # Remove comments (lines starting with #)
    lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
    content = '\n'.join(lines)

    # Find all sections
    section_pattern = r'\[([A-Z_]+)\]\s*\n(.*?)(?=\n\[|$)'
    matches = re.findall(section_pattern, content, re.DOTALL)

    daemon_data = {}

    for section_name, section_content in matches:
        key = section_name.lower()
        parsed = parse_section(section_content.strip())
        daemon_data[key] = parsed

    return daemon_data


def parse_section(content: str) -> Any:
    """Parse section content into appropriate data structure."""
    lines = content.strip().split('\n')

    # Check if it's a list (lines starting with -)
    if all(line.strip().startswith('-') for line in lines if line.strip()):
        return [line.strip().lstrip('- ').strip() for line in lines if line.strip()]

    # Check if it's key-value pairs
    if ':' in content:
        result = {}
        current_key = None
        current_value = []

        for line in lines:
            # Check for multiline value indicator
            if line.strip().endswith('|'):
                current_key = line.split(':')[0].strip()
                current_value = []
                continue

            # If we're in a multiline value
            if current_key and (line.startswith('  ') or line.startswith('\t')):
                current_value.append(line.strip())
                continue

            # If we have a completed multiline value
            if current_key and current_value:
                result[current_key] = ' '.join(current_value)
                current_key = None
                current_value = []

            # Regular key: value pair
            if ':' in line and not line.strip().endswith('|'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    # Handle null values
                    if value.lower() == 'null':
                        value = None
                    result[key] = value

        # Handle final multiline value
        if current_key and current_value:
            result[current_key] = ' '.join(current_value)

        return result

    # Otherwise return as plain text
    return content.strip()


def get_daemon_data(data_dir: Path) -> dict[str, Any]:
    """Load and return daemon data from the data directory."""
    daemon_file = data_dir / "daemon.md"

    if not daemon_file.exists():
        return {"error": "daemon.md not found"}

    return parse_daemon_file(daemon_file)
