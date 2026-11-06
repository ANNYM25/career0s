"""Job collectors. Each targets a public, permitted job-board API — no scraping
of LinkedIn and no paid services. Add new sources by dropping a module here.
"""
from .greenhouse import GreenhouseCollector
from .lever import LeverCollector

REGISTRY = {
    "greenhouse": GreenhouseCollector,
    "lever": LeverCollector,
}
