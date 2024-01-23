# Remote Computer Awake (rawake)

## Installation
```bash
$ pip install -U rawake # install latest version
$ rawake --version # verify installation
```

## Configuration
The `rawake` configuration is a python-base configuration file. Configuration should be stored at `~/.config/rawake/config.py`

*Example:*
```python
from rawake.config import Config, Computer

DEFAULT_SSH_SUSPEND_COMMAND = "sudo systemctl suspend"

CONFIGURATION = Config(
    computers=[
        Computer(
            name="remote-server",
            ip_address="192.168.0.10",
            mac_address="22:1b:5c:44:12:6b",
            ssh_port=2222,
            ssh_suspend_command=DEFAULT_SSH_SUSPEND_COMMAND,
        ),
        Computer(
            name="other-server",
            ip_address="192.168.0.200",
            mac_address="a4:44:c3:61:10:b8",
            ssh_suspend_command="sudo shutdown -h now",
        ),
    ],
)
```

## Listing the configuration
```bash
$ rawake --list
[
  {
    "name": "other-server",
    "mac_address": "a4:44:c3:61:10:b8",
    "ip_address": "192.168.0.200",
    "ss_suspend_command": "sudo shutdown -h now",
    "ssh_port": 22
  },
  {
    "name": "remote-server",
    "mac_address": "22:1b:5c:44:12:6b",
    "ip_address": "192.168.0.10",
    "ss_suspend_command": "sudo systemctl suspend",
    "ssh_port": 2222
  }
]
```

## Suspend remote computer:
`rawake` requires a username:password SSH connection to the remote host to be able to execute the configured suspend command.
```bash
$ rawake --suspend remote-server
SSH authentication:
username:username
password:<password>
```

## Awake remote computer:
For awaking a remote computer, `rawake` sends a [Wake-On-Lan magic packet](https://en.wikipedia.org/wiki/Wake-on-LAN).
```bash
rawake --awake remote-server
```


## Development

### Python dev environment:

- Create new Python virtual environment:
  ```bash
  pyenv virtualenv 3.11 rawake
  ```
- Activate the virtualenv:
  ```bash
  pyenv activate rawake
  ```

- Install dev and test dependencies:
    - `pip install .[dev]`
    - `pip install .[test]`
- Install git pre-commit hooks
    - `pre-commit install`
    - `pre-commit autoupdate`

### Running the tests:
  ```bash
  pytest .
  ```
