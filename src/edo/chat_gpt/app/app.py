"""Main module."""
import datetime as dt
import os
from importlib.resources import files

import streamlit as st
from edo.mkt.ml.llm import LlmBaseModel, Messages

from edo import chat_gpt
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
    def __init__(self):
        package_path = files(chat_gpt)
        prompts_path = package_path.joinpath('model_configuration', 'prompts')
        filename = prompts_path.joinpath('system.tmpl')
        with open(filename) as f:
            system = f.read()

        super().__init__(
            system=system,
        )


def get_timestamp_id():
    now = dt.datetime.now()
    timestamp_id = now.strftime("%Y%m%d%H%M%S")
    return timestamp_id


@st.cache_data
def get_messages_history():
    out = ['current']
    out += os.listdir("tmp/messages")
    return out


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
        # url = st.text_input("url")
        # url = None if url == "" else url
        # messages_ = st.selectbox("messages", get_messages_history())
        # print(messages_)
        # if messages_ != 'current':
        #     filename = f"tmp/messages/{messages_}"
        #     st.session_state["filename"] = filename
        #     with open(filename) as f:
        #         messages = json.load(f)
        #     messages = Messages(messages)
        #     st.session_state["messages"] = messages

    messages = st.session_state.get("messages", Messages())
    if 'filename' not in st.session_state.keys():
        id = get_timestamp_id()
        st.session_state["filename"] = f"tmp/messages_{id}.json"

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
        with ct.chat_message("assistant", avatar=get_avatar("assistant")):
            message = st.write_stream(stream)

        messages.add_assistant(message)
    st.session_state["messages"] = messages

    print(messages())
    # filename = st.session_state["filename"]
    # with open(filename, "w") as f:
    #     json.dump(messages(), f)


app()
