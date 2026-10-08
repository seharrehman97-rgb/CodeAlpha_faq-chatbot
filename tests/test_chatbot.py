"""Tests for the whole chatbot (preprocessing + matching + decision rules)."""
import pytest

from src.chatbot import FAQChatbot


@pytest.fixture(scope="module")
def bot():
    return FAQChatbot()


def test_reply_has_all_expected_keys(bot):
    reply = bot.get_response("Why is my webhook not firing?")
    expected = {"found", "faq_id", "top_faq_ids", "answer", "category",
                "source_url", "score", "suggestions"}
    assert expected <= set(reply)


def test_exact_faq_question_finds_its_faq(bot):
    reply = bot.get_response("Why is my webhook not firing?")
    assert reply["found"] is True
    assert reply["faq_id"] == "f037"
    assert reply["source_url"].startswith("https://")


def test_status_code_shortcut(bot):
    reply = bot.get_response("429")
    assert reply["found"] is True
    assert reply["faq_id"] == "f044"


def test_status_code_inside_a_sentence(bot):
    reply = bot.get_response("i got the error 404")
    assert reply["found"] is True
    assert "404" in reply["source_url"]


def test_unknown_status_code_is_refused(bot):
    reply = bot.get_response("418")
    assert reply["found"] is False
    assert "418" in reply["answer"]


def test_off_topic_question_is_refused(bot):
    reply = bot.get_response("what is the weather today")
    assert reply["found"] is False
    assert reply["faq_id"] is None


def test_empty_question(bot):
    reply = bot.get_response("   ")
    assert reply["found"] is False
    assert reply["answer"] == "Please type a question."


def test_small_talk_is_not_treated_as_an_faq_answer(bot):
    reply = bot.get_response("hi")
    assert reply["found"] is False
    assert reply["answer"].startswith("Hi!")