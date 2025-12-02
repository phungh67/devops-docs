"""
Adult Census Dataset types, parsing, and loading

This module contains all the types and functionality for working with
the Adult Census Dataset, including enums for categorical data,
parsing functions, and dataset loading utilities.
"""

from enum import Enum, auto
from typing import Optional, List
from dataclasses import dataclass
from core import Dataset, create_dataset
import csv


class WorkClass(Enum):
    PRIVATE = "Private"
    SELF_EMP_NOT_INC = "Self-emp-not-inc"
    SELF_EMP_INC = "Self-emp-inc"
    FEDERAL_GOV = "Federal-gov"
    LOCAL_GOV = "Local-gov"
    STATE_GOV = "State-gov"
    WITHOUT_PAY = "Without-pay"
    NEVER_WORKED = "Never-worked"
    UNKNOWN_WORK_CLASS = "Unknown"


class Education(Enum):
    BACHELORS = "Bachelors"
    SOME_COLLEGE = "Some-college"
    ELEVENTH_GRADE = "11th"
    HS_GRAD = "HS-grad"
    PROF_SCHOOL = "Prof-school"
    ASSOC_ACDM = "Assoc-acdm"
    ASSOC_VOC = "Assoc-voc"
    NINTH_GRADE = "9th"
    SEVENTH_EIGHTH_GRADE = "7th-8th"
    TWELFTH_GRADE = "12th"
    MASTERS = "Masters"
    FIRST_FOURTH_GRADE = "1st-4th"
    TENTH_GRADE = "10th"
    DOCTORATE = "Doctorate"
    FIFTH_SIXTH_GRADE = "5th-6th"
    PRESCHOOL = "Preschool"


class MaritalStatus(Enum):
    MARRIED_CIV_SPOUSE = "Married-civ-spouse"
    DIVORCED = "Divorced"
    NEVER_MARRIED = "Never-married"
    SEPARATED = "Separated"
    WIDOWED = "Widowed"
    MARRIED_SPOUSE_ABSENT = "Married-spouse-absent"
    MARRIED_AF_SPOUSE = "Married-AF-spouse"


class Occupation(Enum):
    TECH_SUPPORT = "Tech-support"
    CRAFT_REPAIR = "Craft-repair"
    OTHER_SERVICE = "Other-service"
    SALES = "Sales"
    EXEC_MANAGERIAL = "Exec-managerial"
    PROF_SPECIALTY = "Prof-specialty"
    HANDLERS_CLEANERS = "Handlers-cleaners"
    MACHINE_OP_INSPCT = "Machine-op-inspct"
    ADM_CLERICAL = "Adm-clerical"
    FARMING_FISHING = "Farming-fishing"
    TRANSPORT_MOVING = "Transport-moving"
    PRIV_HOUSE_SERV = "Priv-house-serv"
    PROTECTIVE_SERV = "Protective-serv"
    ARMED_FORCES = "Armed-Forces"
    UNKNOWN_OCCUPATION = "Unknown"


class Relationship(Enum):
    WIFE = "Wife"
    OWN_CHILD = "Own-child"
    HUSBAND = "Husband"
    NOT_IN_FAMILY = "Not-in-family"
    OTHER_RELATIVE = "Other-relative"
    UNMARRIED = "Unmarried"


class Race(Enum):
    WHITE = "White"
    ASIAN_PAC_ISLANDER = "Asian-Pac-Islander"
    AMER_INDIAN_ESKIMO = "Amer-Indian-Eskimo"
    OTHER = "Other"
    BLACK = "Black"


class Sex(Enum):
    MALE = "Male"
    FEMALE = "Female"


class Income(Enum):
    LOW_INCOME = "<=50K"
    HIGH_INCOME = ">50K"


@dataclass
class Adult:
    """Adult census record structure with proper enum types"""
    age: int
    workclass: WorkClass
    fnlwgt: int
    education: Education
    education_num: int
    marital_status: MaritalStatus
    occupation: Occupation
    relationship: Relationship
    race: Race
    sex: Sex
    capital_gain: int
    capital_loss: int
    hours_per_week: int
    native_country: str  # Keep as string due to many country codes
    income: Income


def parse_enum_safely(enum_class, value: str, default_value):
    """Parse enum value safely, returning default if not found"""
    value = value.strip()
    try:
        return next(e for e in enum_class if e.value == value)
    except StopIteration:
        return default_value


def parse_adult(row: List[str]) -> Optional[Adult]:
    """Parse a CSV row into an Adult record

    Args:
        row: List of strings representing one CSV row

    Returns:
        Adult object if parsing succeeds, None otherwise
    """
    if len(row) != 15:
        return None

    try:
        return Adult(
            age=int(row[0].strip()),
            workclass=parse_enum_safely(WorkClass, row[1], WorkClass.UNKNOWN_WORK_CLASS),
            fnlwgt=int(row[2].strip()),
            education=parse_enum_safely(Education, row[3], Education.HS_GRAD),
            education_num=int(row[4].strip()),
            marital_status=parse_enum_safely(MaritalStatus, row[5], MaritalStatus.NEVER_MARRIED),
            occupation=parse_enum_safely(Occupation, row[6], Occupation.UNKNOWN_OCCUPATION),
            relationship=parse_enum_safely(Relationship, row[7], Relationship.NOT_IN_FAMILY),
            race=parse_enum_safely(Race, row[8], Race.OTHER),
            sex=parse_enum_safely(Sex, row[9], Sex.MALE),
            capital_gain=int(row[10].strip()),
            capital_loss=int(row[11].strip()),
            hours_per_week=int(row[12].strip()),
            native_country=row[13].strip(),
            income=parse_enum_safely(Income, row[14], Income.LOW_INCOME)
        )
    except (ValueError, IndexError):
        return None


def load_adult_dataset(filename: str = "adult.csv") -> Dataset[Adult]:
    """Load adult dataset from CSV file

    Args:
        filename: Path to the CSV file

    Returns:
        Dataset containing Adult records with stability 1
    """
    adults = []

    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header

            for row in reader:
                adult = parse_adult(row)
                if adult is not None:
                    adults.append(adult)

    except FileNotFoundError:
        print(f"Warning: {filename} not found, returning empty dataset")
        return create_dataset([], stability=1)

    return create_dataset(adults, stability=1)