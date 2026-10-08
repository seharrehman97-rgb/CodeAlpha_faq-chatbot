"""Shared test setup: run every test from the project folder so data/faqs.csv is found."""
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def run_from_project_root():
    os.chdir(ROOT)