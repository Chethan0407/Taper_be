from fastapi import APIRouter
from enum import Enum
from typing import List

router = APIRouter()

class PlatformEnum(str, Enum):
    TSMC = "TSMC"
    INTEL = "Intel"
    SAMSUNG = "Samsung"

class EdaToolEnum(str, Enum):
    CALIBRE = "Calibre"
    INNOVUS = "Innovus"
    ICC2 = "ICC2"

class ProjectTypeEnum(str, Enum):
    DRC = "DRC"
    LVS = "LVS"
    STA = "STA"
    LAYOUT = "Layout"

class StatusEnum(str, Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    PASSED = "Passed"
    FAILED = "Failed"

@router.get("/platforms", response_model=List[str])
def get_platforms():
    return [e.value for e in PlatformEnum]

@router.get("/eda-tools", response_model=List[str])
def get_eda_tools():
    return [e.value for e in EdaToolEnum]

@router.get("/types", response_model=List[str])
def get_types():
    return [e.value for e in ProjectTypeEnum]

@router.get("/statuses", response_model=List[str])
def get_statuses():
    return [e.value for e in StatusEnum] 