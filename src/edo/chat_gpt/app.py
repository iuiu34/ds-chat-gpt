"""Main module."""
import streamlit as st
from edo.mkt.ml.llm import LlmBaseModel, Messages


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
        chat_message_.markdown(content)


class LlmModel(LlmBaseModel):
    pass


def app():
    model = LlmModel()
    prompt = st.chat_input()

    with st.expander("Config"):
        model.model = st.text_input("model", model.model)
        model.system = st.text_area("system", model.system.strip())
        model.prompt_template = st.text_area("prompt_template", model.prompt_template.strip())
        if st.button("new chat"):
            del st.session_state["messages"]

    messages = st.session_state.get("messages", Messages())


    st.subheader("messages")
    get_chat(messages, st)
    if prompt:
        prompt = prompt.strip()
        messages.add_user(prompt)
        get_chat(messages, st, last=True)
        stream = model.predict_stream(messages=messages)
        message = ''
        empty = st.empty()
        for chunk in stream:
            chunk_ = chunk.choices[0].delta.content
            if chunk_ is not None:
                print(chunk_, end="")
                message += chunk_
                with empty.chat_message("assistant", avatar=get_avatar("assistant")):
                    st.markdown(message)
                # get_chat(messages, empty, last=True)

        messages.add_assistant(message)
    st.session_state["messages"] = messages
    print(messages())


app()
