from importlib.metadata import version, PackageNotFoundError

__all__ = ["__version__"]

try:
    __version__ = version("rawake")
except PackageNotFoundError:
    # package is not installed
    pass
