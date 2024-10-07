"""Main module."""
import streamlit as st
from edo.mkt.ml.llm import Messages

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

        print(content)
        if content.startswith('http'):
            chat_message_.image(content, width=512)
        else:
            chat_message_.markdown(content, unsafe_allow_html=True)


class ImageModel:
    def __init__(self, model='dall-e-3'):
        self.model = model
        self.prompt_template = "prompt_template"

    def predict_sample(self, prompt):
        from openai import OpenAI
        client = OpenAI()

        response = client.images.generate(
            model=self.model,
            prompt=prompt,
            # size="512x512",
            # quality="standard",
            # n=1,
        )

        if len(response.data) == 0:
            raise ValueError("No image returned")
        elif len(response.data) == 1:
            image_url = response.data[0].url
        else:
            image_url = [v.url for v in response.data]

        return image_url


def app():
    st.set_page_config(page_title=f'chatGPT', layout="wide")
    st.markdown(theme_css, unsafe_allow_html=True)

    model = ImageModel()
    prompt = st.chat_input()
    if prompt is None:
        prompt = st.session_state.get("prompt")

    with st.expander("Config"):
        model.model = st.text_input("model", model.model)

    messages = st.session_state.get("messages", Messages())

    st.subheader("messages")
    if st.button("new chat"):
        del st.session_state["messages"]
        st.rerun()

    # if st.button("repl")

    get_chat(messages, st)
    if prompt:
        prompt = prompt.strip()
        messages.add_user(prompt)
        get_chat(messages, st, last=True)
        with st.spinner("Generating image..."):
            img = model.predict_sample(prompt=prompt)
        st.image(img, width=512)
        messages.add_assistant(img, 'image')
    st.session_state["messages"] = messages
    st.session_state["prompt"] = prompt
    print(messages())


app()
