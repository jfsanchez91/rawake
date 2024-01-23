import typing
import wakeonlan as wol

from paramiko import SSHClient

from rawake.logging import logger
from rawake.config import Config, Computer


class ComputerController:
    def __init__(self, config: Config):
        self.config = config
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()

    def awake_by_name(self, computer_name: str) -> bool:
        computer = self.config.find_computer_by_name(computer_name)
        return self.awake(computer)

    def awake(self, computer: Computer) -> bool:
        logger.info(f"Awaking computer: {computer}")
        wol.send_magic_packet(computer.mac_address)
        return True

    def suspend_by_name(self, computer_name: str, ssh_username: str, ssh_password: str) -> bool:
        computer = self.config.find_computer_by_name(computer_name)
        return self.suspend(computer, ssh_username, ssh_password)

    def suspend(self, computer: Computer, ssh_username: str, ssh_password: str) -> bool:
        logger.info(f"Suspending computer: {computer}")
        try:
            self.ssh_client.connect(computer.ip_address, username=ssh_username, password=ssh_password)
            stdin, stdout, stderr = self.ssh_client.exec_command(computer.ssh_suspend_command)
            stdin.close()
            stdout.close()
            stderr.close()
            self.ssh_client.close()
            return True
        except Exception as e:
            logger.error(f"Can not execute SSH command: {e.strerror}")
            return False

    def list_computers(self) -> typing.List[Computer]:
        return self.config.computers
