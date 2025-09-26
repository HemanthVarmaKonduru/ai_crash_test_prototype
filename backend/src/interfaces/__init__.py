"""
Interfaces and abstract base classes
"""
from .model_interface import ModelInterface
from .evaluator_interface import EvaluatorInterface
from .dataset_interface import DatasetInterface
from .storage_interface import StorageInterface

__all__ = [
    "ModelInterface",
    "EvaluatorInterface", 
    "DatasetInterface",
    "StorageInterface"
]


