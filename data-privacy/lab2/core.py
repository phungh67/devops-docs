"""
Core data structures and types for the Differential Privacy DSL

This module defines the fundamental data types used throughout the DSL:
- Dataset with stability tracking (abstract datatype)
- DPResult for measurement outputs
- Exception types
- Privacy budget management

STUDENT TODO: Complete the implementation of the Dataset abstract base class
and the concrete dataset implementation.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Iterator, Any
from dataclasses import dataclass

T = TypeVar('T')
Epsilon = float
Budget = float


class Dataset(Generic[T], ABC):
    """Abstract base class for Datasets with stability tracking

    This class provides an abstract interface for datasets that encapsulates
    the data and tracks stability (how much one individual can affect results).

    STUDENT TODO: Complete the implementation of this abstract base class.
    You need to:
    1. Implement the constructor that validates stability >= 1
    2. Implement the abstract methods
    3. Implement the __len__ and __iter__ methods for the interface

    Key concepts:
    - Stability: Integer >= 1 representing the maximum contribution of one individual
    - Data encapsulation: Internal data should not be directly accessible
    - Abstract methods: Subclasses must implement _get_data() and _create_new()
    """

    def __init__(self, data: List[T], stability: int = 1):
        """Initialize dataset with data and stability

        Args:
            data: The underlying data elements
            stability: Stability parameter for noise calibration
        Raises:
            ValueError: If stability < 1
        """
        if stability < 1:
            raise ValueError(f"Stability must be larger or at least 1, but got {stability}")
        self._data = list(data)
        self._stability = stability



    @property
    def stability(self) -> int:
        """Get the stability parameter (read-only)"""
        return self._stability

    def __len__(self) -> int:
        """Get the number of elements in the dataset"""
        return len(self._data)
        

    def __iter__(self) -> Iterator[T]:
        """Iterate over the dataset elements (read-only)"""
        return iter(self._data)
    

    # Abstract methods for controlled access (to be used by DP_DSL class only)
    @abstractmethod
    def _get_data(self) -> List[T]:
        """Get the underlying data (for use by internal DP_DSL operations only)
        """
        pass

    @abstractmethod
    def _create_new(self, new_data: List[Any], new_stability: int) -> 'Dataset':
        """Create new dataset with given data and stability"""
        pass 


class ConcreteDataset(Dataset[T]):
    """Concrete implementation of Dataset

    This is the actual implementation that should be used internally by the DP_DSL.
    Users should create datasets using the factory function `create_dataset()`.

    STUDENT TODO: Complete this implementation.
    This is a simple concrete implementation that stores data in a list.
    """

    def _get_data(self) -> List[T]:
        """Get underlying data - for internal DP_DSL operations only"""
        return self._data

    def _create_new(self, new_data: List[Any], new_stability: int) -> 'ConcreteDataset':
        """Create new concrete dataset with given data and stability"""
        return ConcreteDataset(new_data, new_stability)


def create_dataset(data: List[T], stability: int = 1) -> Dataset[T]:
    """Factory function to create a new Dataset

    Args:
        data: The data elements
        stability: Stability parameter (default: 1)

    Returns:
        A new Dataset instance

    Example:
        >>> data = create_dataset([1, 2, 3, 4, 5])
        >>> print(f"Dataset size: {len(data)}")
        >>> print(f"Stability: {data.stability}")
    """
    return ConcreteDataset(data, stability)



@dataclass
class DPResult:
    """Result of a differentially private computation

    Encapsulates both the noisy result and the privacy cost (epsilon spent).
    """
    dp_value: float
    epsilon_spent: float


class PrivacyError(Exception):
    """Exception types for privacy operations"""
    pass


class InsufficientBudget(PrivacyError):
    """Raised when requested privacy budget exceeds available budget"""
    def __init__(self, requested: Budget, available: Budget):
        self.requested = requested
        self.available = available
        super().__init__(f"Insufficient budget: need {requested}, have {available}")


class InvalidParameter(PrivacyError):
    """Raised when invalid parameters are provided"""
    def __init__(self, message: str):
        super().__init__(f"Invalid parameter: {message}")
