import pytest

from edo.chat_gpt.chat_gpt import chat_gpt


def test_chat_gpt():
    with pytest.raises(TypeError):
        chat_gpt()


