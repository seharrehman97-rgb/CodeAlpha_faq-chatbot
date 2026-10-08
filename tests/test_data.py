"""Checks on the data files. If someone breaks the CSV, these tests fail."""
import pandas as pd
import pytest

REQUIRED_COLUMNS = ["faq_id", "category", "question", "answer", "source_url"]


@pytest.fixture(scope="module")
def faqs():
    return pd.read_csv("data/faqs.csv")


@pytest.fixture(scope="module")
def held_out_set():
    return pd.read_csv("data/test_questions.csv")


def test_faq_columns(faqs):
    assert list(faqs.columns) == REQUIRED_COLUMNS


def test_faq_has_no_missing_values(faqs):
    assert faqs.isna().sum().sum() == 0


def test_each_faq_has_one_answer_and_one_source(faqs):
    # All wordings of the same FAQ must share the same answer, category and source.
    grouped = faqs.groupby("faq_id")
    assert (grouped["answer"].nunique() == 1).all()
    assert (grouped["category"].nunique() == 1).all()
    assert (grouped["source_url"].nunique() == 1).all()


def test_each_faq_has_several_wordings(faqs):
    assert (faqs.groupby("faq_id").size() >= 3).all()


def test_no_duplicate_questions(faqs):
    assert not faqs["question"].str.lower().str.strip().duplicated().any()


def test_sources_are_web_links(faqs):
    assert faqs["source_url"].str.startswith("https://").all()


def test_test_questions_point_to_real_faqs(faqs, held_out_set):
    allowed = set(faqs["faq_id"]) | {"NONE"}
    assert set(held_out_set["expected_faq_id"]) <= allowed


def test_test_questions_are_not_copied_from_the_faq_file(faqs, held_out_set):
    # The test set must contain questions the bot has never seen.
    seen = set(faqs["question"].str.lower().str.strip())
    assert not (set(held_out_set["question"].str.lower().str.strip()) & seen)