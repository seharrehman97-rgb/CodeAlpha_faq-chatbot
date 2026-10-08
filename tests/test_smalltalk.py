"""Tests for the small-talk intents."""
from src.smalltalk import CAPABILITIES, small_talk_reply


def test_greeting_gets_a_reply():
    assert small_talk_reply("Hi!") is not None


def test_thanks_gets_a_reply():
    assert "welcome" in small_talk_reply("thank you").lower()


def test_joke_request_gets_a_friendly_refusal():
    assert "comedian" in small_talk_reply("tell me a joke")


def test_what_can_you_do_for_developers():
    question = "which things you can do for developers, can you tell how you can benefit developers"
    assert small_talk_reply(question) == CAPABILITIES


def test_real_question_starting_with_hi_is_not_intercepted():
    assert small_talk_reply("hi, my webhook is not firing") is None


def test_question_with_status_code_is_not_intercepted():
    assert small_talk_reply("help me with a 401 error") is None
    assert small_talk_reply("what can you do about a 502") is None


def test_question_about_an_api_topic_is_not_intercepted():
    assert small_talk_reply("how can you benefit developers working with webhooks") is None


def test_unrelated_question_is_not_small_talk():
    assert small_talk_reply("what is the weather today") is None