import sys
import argparse
import typing
import json
import getpass
import logging

from rawake.logging import logger
from rawake.config import Config, Computer
from rawake.computer_controller import ComputerController


def print_computers(computers: typing.Set[Computer]):
    class ComputerJsonEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, Computer):
                return {
                    "name": o.name,
                    "mac_address": o.mac_address,
                    "ip_address": o.ip_address,
                    "ss_suspend_command": o.ssh_suspend_command,
                    "ssh_port": o.ssh_port,
                }
            return super().default(o)

    print(json.dumps(list(computers), cls=ComputerJsonEncoder, indent=2))


def run():
    parser = argparse.ArgumentParser(prog="rawake", description="Remotly awake your computers")
    parser.add_argument("-v", "--verbose", help="verbose logging.", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--awake", help="awakes a computer by it's name.")
    group.add_argument("-s", "--suspend", help="suspends a computer by it's name.")
    group.add_argument("-l", "--list", help="list configured computers.", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    controller = ComputerController(Config.load())

    if args.list:
        print_computers(controller.list_computers())
    elif args.awake:
        controller.awake_by_name(computer_name=args.awake)
    elif args.suspend:
        print("SSH Connection:")
        ssh_username = input("\tusername:")
        ssh_password = getpass.getpass("\tpassword:")
        controller.suspend_by_name(computer_name=args.suspend, ssh_username=ssh_username, ssh_password=ssh_password)
    else:
        parser.print_usage()
        sys.exit(-1)
