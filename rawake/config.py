import os
import typing
import re

from rawake.logging import logger


class Computer:
    MAC_ADDRESS_REGEX = re.compile("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$")
    IP_ADDRESS_REGEX = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    def __init__(self, name: str, mac_address: str, ip_address: str, ssh_suspend_command: str, ssh_port: int = 22) -> None:
        self.name = name
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.ssh_suspend_command = ssh_suspend_command
        self.ssh_port = int(ssh_port)
        self.validate()

    def validate(self):
        if Computer.MAC_ADDRESS_REGEX.fullmatch(self.mac_address) is None:
            raise ValueError(f"Invalid computer MAC address: {self.mac_address}.")
        if Computer.IP_ADDRESS_REGEX.fullmatch(self.ip_address) is None:
            raise ValueError(f"Invalid computer IP address: {self.ip_address}.")

    def __str__(self) -> str:
        return f"Computer(name={self.name}, mac_address={self.mac_address}, ip_address={self.ip_address}), ssh_port={self.ssh_port})"

    def __repr__(self) -> str:
        return f"Computer(name={self.name}, mac_address={self.mac_address}, ip_address={self.ip_address}), ssh_port={self.ssh_port})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Computer):
            return False
        return self.name == other.name or self.mac_address == other.mac_address

    def __hash__(self) -> int:
        return hash(self.name)


class Config:
    DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/rawake/config.py")

    def __init__(self, computers: typing.List[Computer]) -> None:
        if len(computers) <= 0:
            raise ValueError("Invalid config. Computer list is empty.")

        self.computers = set([])
        for computer in computers:
            if computer in self.computers:
                raise ValueError(f"Duplicated computer configuration: {computer}.")
            self.computers.add(computer)

    @staticmethod
    def load(filename: str = DEFAULT_CONFIG_PATH):
        logger.debug(f"Loading config from: {filename}")
        config_dict = {}
        with open(filename, "r") as file:
            exec(file.read(), config_dict)

        configuration = config_dict["CONFIGURATION"]
        if isinstance(configuration, Config):
            return configuration
        raise ValueError(f"Invalid configuration file.")

    def find_computer_by_name(self, name: str) -> Computer:
        for computer in self.computers:
            if computer.name == name:
                return computer
        raise LookupError(f"Computer with name='{name}' not found.")

    def __str__(self) -> str:
        return f"Config(computers={self.computers})"

    def __repr__(self) -> str:
        return f"Config(computers={self.computers})"
