"""Main module."""
import base64
import os.path

import streamlit as st
from edo.mkt.ml.llm import Messages
from streamlit.runtime.uploaded_file_manager import UploadedFile

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

        chat_message_ = c1.chat_message(role, avatar=avatar)

        # print(content)
        if type(content) is UploadedFile:
            chat_message_.image(content, width=512)
        elif os.path.isfile(content):
            chat_message_.image(content, width=512)
        elif content.startswith('http'):
            chat_message_.image(content, width=512)
        else:
            chat_message_.markdown(content, unsafe_allow_html=True)


class VisionModel:
    def __init__(self, model='gpt-4-vision-preview'):
        self.model = model
        self.prompt_template = "prompt_template"

    def predict_stream(self, messages):
        from openai import OpenAI
        # img_b64 = encode_image(img_file)
        client = OpenAI()
        messages = messages()
        messages_ = []
        for v in messages:
            v = v.copy()
            if v["role"] == "user":
                prompt = v["content"]
                if os.path.isfile(prompt):
                    v["content"] = get_img_64(prompt)
            messages_.append(v)

        stream = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages_,
            max_tokens=300,
            stream=True
        )

        # print(response.choices[0])
        #
        # if len(response.choices) != 1:
        #     raise ValueError("No image returned")
        # else:
        #     out = response.choices[0]

        return stream


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_img_64(img_file):
    img_b64 = encode_image(img_file)
    out = [
        dict(type='image_url',
             image_url=dict(
                 url=f"data:image/png;base64,{img_b64}"
             ))
    ]
    return out


def app():
    st.set_page_config(page_title=f'chatGPT', layout="wide")
    st.markdown(theme_css, unsafe_allow_html=True)

    model = VisionModel()

    with st.expander("Config"):
        model.model = st.text_input("model", model.model)
    # img_file_ = "tmp/snap.png"
    # img_ = encode_image(img_file_)
    messages_ = Messages()
    # messages_.add_user(img_)
    messages = st.session_state.get("messages", messages_)

    st.subheader("messages")
    if st.button("new chat"):
        del st.session_state["messages"]
        st.rerun()

    img = st.file_uploader('upload image')
    prompt = st.chat_input()
    # if prompt is None:
    # prompt = "Provide script(s) in react + ts + antd to replicate the site."
    # prompt = "Which color are the primary buttons? (red, green, blue, yellow, black, white)"
    ct = st.container(height=512)

    get_chat(messages, ct)
    if img is None:
        img_file = "tmp/snap.png"
    else:
        with open("tmp/img_1.png", "wb") as f:
            f.write(img.read())
        img_file = "tmp/img_1.png"
    if prompt:
        prompt = prompt.strip()
        messages.add_user(img_file)
        get_chat(messages, ct, last=True)
        messages.add_user(prompt)
        get_chat(messages, ct, last=True)
        stream = model.predict_stream(messages)
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
