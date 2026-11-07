"""Job collectors. Each targets a public, permitted job-board API — no scraping
of LinkedIn and no paid services. Add new sources by dropping a module here.
"""
from .ashby import AshbyCollector
from .greenhouse import GreenhouseCollector
from .lever import LeverCollector
from .smartrecruiters import SmartRecruitersCollector

REGISTRY = {
    "greenhouse": GreenhouseCollector,
    "lever": LeverCollector,
    "ashby": AshbyCollector,
    "smartrecruiters": SmartRecruitersCollector,
}
