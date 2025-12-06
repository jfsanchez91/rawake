import typing
import wakeonlan as wol
import subprocess
import paramiko

from rawake.logging import logger, panic
from rawake.config import Config, Computer


class ComputerController:
    def __init__(self, config: Config):
        self.config = config
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()

    def awake_by_name(self, computer_name: str) -> None:
        computer = self.find_computer_by_name_or_panic(computer_name)
        return self.awake(computer)

    def awake(self, computer: Computer) -> None:
        logger.info(f"Awaking computer: {computer}")
        wol.send_magic_packet(computer.mac_address)
        logger.debug(f"Wake-On-Lan magic packet sent to MAC address {computer.mac_address}")

    def suspend_by_name(self, computer_name: str, ssh_username: str, ssh_password: str = None) -> None:
        computer = self.find_computer_by_name_or_panic(computer_name)
        return self.suspend(computer, ssh_username, ssh_password)

    def suspend(self, computer: Computer, ssh_username: str, ssh_password: str = None) -> None:
        logger.info(f"Suspending computer: {computer}")
        try:
            logger.debug(f"Connecting to ssh://{computer.ip_address}:{computer.ssh_port}")
            self.ssh_client.connect(computer.ip_address, computer.ssh_port, username=ssh_username, password=ssh_password)
            logger.debug(f"Running SSH command: {computer.ssh_suspend_command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(computer.ssh_suspend_command)
            stdin.close()
            stdout.close()
            stderr.close()
            logger.debug(f"Closing SSH connection")
            self.ssh_client.close()
        except paramiko.AuthenticationException:
            raise
        except Exception as e:
            panic("Can not execute SSH command: " + str(e))

    def check_status_by_name(self, computer_name: str) -> bool:
        computer = self.find_computer_by_name_or_panic(computer_name)
        return self.check_status(computer)

    def check_status(self, computer: Computer) -> bool:
        """
        Ping the computer to check if it is online.
        Returns True if online (responds to ping), False otherwise.
        """
        logger.info(f"Checking status for: {computer}")
        try:
            # -c 1: count 1 packet
            # -W 2: timeout 2 seconds
            command = ["ping", "-c", "1", "-W", "2", computer.ip_address]
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            is_online = result.returncode == 0
            status_str = "Online" if is_online else "Offline"
            logger.info(f"Computer {computer.name} is {status_str}")
            return is_online
        except Exception as e:
            logger.error(f"Error pinging computer {computer.name}: {e}")
            return False

    def find_computer_by_name_or_panic(self, name: str) -> Computer:
        try:
            return self.config.find_computer_by_name(name)
        except LookupError as e:
            panic(e)

    def list_computers(self) -> typing.List[Computer]:
        return self.config.computers
