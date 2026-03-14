import os

__author__ = ["Joseph Kenny"]
__copyright__ = "ETH Zurich, Princeton University"
__license__ = "MIT License"
__email__ = "kenny@arch.ethz.ch"
__version__ = "1.0.0"


HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "data"))

__all__ = ["HERE", "DATA"]
