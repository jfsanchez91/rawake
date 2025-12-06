import pytest
import subprocess
from unittest.mock import MagicMock, patch
from rawake.computer_controller import ComputerController
from rawake.config import Config, Computer

@pytest.fixture
def sample_computer():
    return Computer(name="test-pc", mac_address="00:11:22:33:44:55", ip_address="192.168.1.100", ssh_suspend_command="sudo sleep 1")

@pytest.fixture
def mock_config(sample_computer):
    config = MagicMock(spec=Config)
    config.computers = {sample_computer}
    config.find_computer_by_name.side_effect = lambda name: sample_computer if name == "test-pc" else None
    
    # Adding side effect to raise LookupError if not found, effectively mimicking real behavior for non-matching names if needed
    def find_mock(name):
        if name == "test-pc":
            return sample_computer
        raise LookupError("Computer not found")
        
    config.find_computer_by_name.side_effect = find_mock
    return config

@patch("rawake.computer_controller.wol")
def test_awake(mock_wol, mock_config, sample_computer):
    controller = ComputerController(mock_config)
    controller.awake_by_name("test-pc")
    
    mock_wol.send_magic_packet.assert_called_once_with(sample_computer.mac_address)

@patch("rawake.computer_controller.paramiko.SSHClient")
def test_suspend(mock_ssh_class, mock_config, sample_computer):
    mock_ssh = mock_ssh_class.return_value
    mock_ssh.exec_command.return_value = (MagicMock(), MagicMock(), MagicMock())
    
    controller = ComputerController(mock_config)
    controller.suspend_by_name("test-pc", "user", "pass")
    
    # Check connection
    mock_ssh.connect.assert_called_once_with(sample_computer.ip_address, sample_computer.ssh_port, username="user", password="pass")
    # Check command execution
    mock_ssh.exec_command.assert_called_once_with(sample_computer.ssh_suspend_command)
    # Check closure
    mock_ssh.close.assert_called_once()

@patch("rawake.computer_controller.paramiko.SSHClient")
def test_suspend_no_password(mock_ssh_class, mock_config, sample_computer):
    mock_ssh = mock_ssh_class.return_value
    mock_ssh.exec_command.return_value = (MagicMock(), MagicMock(), MagicMock())
    
    controller = ComputerController(mock_config)
    controller.suspend_by_name("test-pc", "user") # No password
    
    # Check connection calls with password=None
    mock_ssh.connect.assert_called_once_with(sample_computer.ip_address, sample_computer.ssh_port, username="user", password=None)

@patch("rawake.computer_controller.paramiko.SSHClient")
def test_suspend_auth_failure(mock_ssh_class, mock_config, sample_computer):
    import paramiko
    mock_ssh = mock_ssh_class.return_value
    mock_ssh.connect.side_effect = paramiko.AuthenticationException("Auth failed")
    
    controller = ComputerController(mock_config)
    
    with pytest.raises(paramiko.AuthenticationException):
        controller.suspend_by_name("test-pc", "user")

@patch("rawake.computer_controller.subprocess.run")
def test_check_status_online(mock_run, mock_config, sample_computer):
    mock_run.return_value = MagicMock(returncode=0)
    
    controller = ComputerController(mock_config)
    assert controller.check_status_by_name("test-pc") is True
    
    mock_run.assert_called_once_with(
        ["ping", "-c", "1", "-W", "2", sample_computer.ip_address],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

@patch("rawake.computer_controller.subprocess.run")
def test_check_status_offline(mock_run, mock_config, sample_computer):
    mock_run.return_value = MagicMock(returncode=1)
    
    controller = ComputerController(mock_config)
    assert controller.check_status_by_name("test-pc") is False

@patch("rawake.computer_controller.subprocess.run")
def test_check_status_exception(mock_run, mock_config, sample_computer):
    mock_run.side_effect = Exception("Ping failed")
    
    controller = ComputerController(mock_config)
    assert controller.check_status_by_name("test-pc") is False
