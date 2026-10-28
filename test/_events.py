import os
import subprocess
import pytest

DATA_FILE = "events_data.json"

def setup_function():
    """Clean up the local data file before each test function runs."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def teardown_function():
    """Clean up the local data file after each test function completes."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_prevent_overbooking():
    """Test the domain rule: ensure an event cannot be overbooked beyond its capacity[cite: 166]."""
    
    # 1. Create an event with capacity 1
    subprocess.run(
        ["python", "events.py", "event", "add", "--name", "DevOps Workshop", "--capacity", "1"],
        check=True
    )

    # 2. First registration should succeed (returncode == 0)
    res1 = subprocess.run(
        ["python", "events.py", "registration", "create", "--event", "1", "--attendee", "Alice"],
        capture_output=True,
        text=True
    )
    assert res1.returncode == 0
    assert "Registration successful" in res1.stdout

    # 3. Second registration should fail due to capacity limit (returncode != 0)
    res2 = subprocess.run(
        ["python", "events.py", "registration", "create", "--event", "1", "--attendee", "Bob"],
        capture_output=True,
        text=True
    )
    assert res2.returncode != 0
    assert "Error: Cannot register" in res2.stdout