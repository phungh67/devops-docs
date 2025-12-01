"""
Differential Privacy DSL - Main module

A unified implementation of a Domain Specific Language for Differential Privacy
using the DP_DSL class that encapsulates budget management, transformations,
and measurements in a single, easy-to-use interface.
"""

# Main DP_DSL class
from dp_dsl import DP_DSL

# Core data structures
from core import Dataset, create_dataset, DPResult, PrivacyError, InsufficientBudget, InvalidParameter, Epsilon, Budget

# Adult dataset utilities
from adult_dataset import (
    Adult, WorkClass, Education, MaritalStatus, Occupation,
    Relationship, Race, Sex, Income, load_adult_dataset
)

__all__ = [
    # Main DSL class
    'DP_DSL',

    # Core types
    'Dataset', 'create_dataset', 'DPResult', 'PrivacyError', 'InsufficientBudget', 'InvalidParameter',
    'Epsilon', 'Budget',

    # Adult dataset
    'Adult', 'WorkClass', 'Education', 'MaritalStatus', 'Occupation',
    'Relationship', 'Race', 'Sex', 'Income', 'load_adult_dataset'
]