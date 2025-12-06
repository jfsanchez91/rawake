import pytest
import os
import tempfile
from rawake.config import Computer, Config

def test_computer_validation_valid():
    c = Computer(name="test", mac_address="00:11:22:33:44:55", ip_address="192.168.1.1", ssh_suspend_command="sleep 1")
    assert c.name == "test"

def test_computer_validation_invalid_mac():
    with pytest.raises(ValueError, match="Invalid computer MAC"):
        Computer(name="test", mac_address="invalid", ip_address="192.168.1.1", ssh_suspend_command="sleep 1")

def test_computer_validation_invalid_ip():
    with pytest.raises(ValueError, match="Invalid computer IP"):
        Computer(name="test", mac_address="00:11:22:33:44:55", ip_address="999.999.999.999", ssh_suspend_command="sleep 1")

def test_config_load_valid():
    config_content = """
from rawake.config import Config, Computer
CONFIGURATION = Config(computers=[
    Computer(name="c1", mac_address="00:11:22:33:44:55", ip_address="192.168.1.1", ssh_suspend_command="cmd")
])
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(config_content)
        tmp.close()
        try:
            config = Config.load(tmp.name)
            assert len(config.computers) == 1
            assert list(config.computers)[0].name == "c1"
        finally:
            os.remove(tmp.name)

def test_config_duplicate_computers():
    with pytest.raises(ValueError, match="Duplicated computer"):
        Config(computers=[
            Computer(name="c1", mac_address="00:11:22:33:44:55", ip_address="192.168.1.1", ssh_suspend_command="cmd"),
            Computer(name="c1", mac_address="00:11:22:33:44:55", ip_address="192.168.1.1", ssh_suspend_command="cmd")
        ])
