import typing
import wakeonlan as wol

from paramiko import SSHClient

from rawake.logging import logger, panic
from rawake.config import Config, Computer


class ComputerController:
    def __init__(self, config: Config):
        self.config = config
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()

    def awake_by_name(self, computer_name: str) -> None:
        computer = self.find_computer_by_name_or_panic(computer_name)
        return self.awake(computer)

    def awake(self, computer: Computer) -> None:
        logger.info(f"Awaking computer: {computer}")
        wol.send_magic_packet(computer.mac_address)
        logger.debug(f"Wake-On-Lan magic packet sent to MAC address {computer.mac_address}")

    def suspend_by_name(self, computer_name: str, ssh_username: str, ssh_password: str) -> None:
        computer = self.find_computer_by_name_or_panic(computer_name)
        return self.suspend(computer, ssh_username, ssh_password)

    def suspend(self, computer: Computer, ssh_username: str, ssh_password: str) -> None:
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
        except Exception as e:
            panic("Can not execute SSH command: " + str(e))

    def find_computer_by_name_or_panic(self, name: str) -> Computer:
        try:
            return self.config.find_computer_by_name(name)
        except LookupError as e:
            panic(e)

    def list_computers(self) -> typing.List[Computer]:
        return self.config.computers
