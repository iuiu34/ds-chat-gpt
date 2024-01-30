"""Main module."""

import streamlit as st
from edo.mkt.ml.llm import LlmBaseModel, Messages

from edo.chat_gpt._utils.theme import theme_css


def get_avatar(role):
    if role == 'assistant':
        avatar = "img/assistant_logo.png"
    elif role == 'user':
        avatar = "img/user_logo.png"
    else:
        raise ValueError(f'role {role} not understood')
    return avatar


def get_chat(messages, c1, last=False):
    messages_ = messages()
    if last:
        messages_ = messages_[-1:]
    for n, chat_ in enumerate(messages_):
        if last:
            n += 1
        role = chat_["role"]
        content = chat_["content"]

        if role in ['system', 'tool_call', 'tool_response']:
            continue

        if role == 'function':
            role = "assistant"

        avatar = get_avatar(role)

        print(content)
        chat_message_ = c1.chat_message(role, avatar=avatar)
        chat_message_.markdown(content, unsafe_allow_html=True)


class LlmModel(LlmBaseModel):
    pass


def app():
    st.set_page_config(page_title=f'chatGPT', layout="wide")
    st.markdown(theme_css, unsafe_allow_html=True)

    model = LlmModel()
    prompt = st.chat_input()

    c1, c2, c3 = st.columns([1, 1, 3])
    c1.subheader("messages")

    with c3.expander("Config"):
        model.model = st.text_input("model", model.model)
        model.system = st.text_area("system", model.system.strip())

    messages = st.session_state.get("messages", Messages())

    if c2.button("new chat"):
        del st.session_state["messages"]
        st.rerun()
    ct = st.container(height=512)
    get_chat(messages, ct)
    if prompt:
        prompt = prompt.strip()
        messages.add_user(prompt)
        get_chat(messages, ct, last=True)
        stream = model.predict_stream(messages=messages)
        message = ''
        empty = ct.empty()
        for chunk in stream:
            chunk_ = chunk.choices[0].delta.content
            if chunk_ is not None:
                print(chunk_, end="")
                message += chunk_
                with empty.chat_message("assistant", avatar=get_avatar("assistant")):
                    st.markdown(message, unsafe_allow_html=True)

        messages.add_assistant(message)
    st.session_state["messages"] = messages
    print(messages())


app()
