# For protocol definitions, please refer to: https://clinicaltrials.gov/policy/protocol-definitions

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Agency(BaseModel):
    name: str
    type: Literal[
        "NIH", "FED", "OTHER_GOV", "INDIV", "INDUSTRY", "NETWORK", "AMBIG", "OTHER", "UNKNOWN"
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-AgencyClass


class ArmGroup(BaseModel):
    label: str
    type: Optional[
        Literal[
            "EXPERIMENTAL",
            "ACTIVE_COMPARATOR",
            "PLACEBO_COMPARATOR",
            "SHAM_COMPARATOR",
            "NO_INTERVENTION",
            "OTHER",
        ]
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-ArmGroupType
    description: Optional[str]
    intervention_names: list[str] = Field(default_factory=list)


class Condition(BaseModel):
    name: str
    mesh_uid: Optional[str]


class DateStruct(BaseModel):
    date: str
    type: Optional[
        Literal["ACTUAL", "ESTIMATED"]
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-DateType


class Intervention(BaseModel):
    name: str
    mesh_uid: Optional[str]
    type: Literal[
        "BEHAVIORAL",
        "BIOLOGICAL",
        "COMBINATION_PRODUCT",
        "DEVICE",
        "DIAGNOSTIC_TEST",
        "DIETARY_SUPPLEMENT",
        "DRUG",
        "GENETIC",
        "PROCEDURE",
        "RADIATION",
        "OTHER",
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-InterventionType
    arm_group_labels: list[str] = Field(default_factory=list)
    other_names: list[str] = Field(default_factory=list)
    description: Optional[str]


class TrialCore(BaseModel):
    nct_id: str

    brief_title: str
    official_title: str

    study_type: Literal[
        "EXPANDED_ACCESS", "INTERVENTIONAL", "OBSERVATIONAL"
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-StudyType

    overall_status: Literal[
        "ACTIVE_NOT_RECRUITING",
        "COMPLETED",
        "ENROLLING_BY_INVITATION",
        "NOT_YET_RECRUITING",
        "RECRUITING",
        "SUSPENDED",
        "TERMINATED",
        "WITHDRAWN",
        "AVAILABLE",
        "NO_LONGER_AVAILABLE",
        "TEMPORARILY_NOT_AVAILABLE",
        "APPROVED_FOR_MARKETING",
        "WITHHELD",
        "UNKNOWN",
    ]  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-Status

    phases: list[Literal["NA", "EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"]] = Field(
        default_factory=list
    )  # https://clinicaltrials.gov/data-api/about-api/study-data-structure#enum-Phase

    lead_sponsor: Agency
    collaborators: list[Agency] = Field(default_factory=list)

    conditions: list[Condition] = Field(default_factory=list)
    arm_groups: list[ArmGroup] = Field(default_factory=list)
    interventions: list[Intervention] = Field(default_factory=list)

    start_date: Optional[DateStruct]
    primary_completion_date: Optional[DateStruct]
    completion_date: Optional[DateStruct]

    has_results: bool = False
