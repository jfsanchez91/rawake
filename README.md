# Remote Computer Awake (rawake)

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
