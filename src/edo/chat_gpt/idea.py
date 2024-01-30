"""Main module."""
import streamlit as st
from edo.mkt.ml.llm import LlmBaseModel, Messages
from streamlit_extras.stylable_container import stylable_container

from edo.chat_gpt._utils.theme import theme_css

import re

def str_to_html(out):
    # Split the text into sections based on triple backtick delimiters
    sections = re.split(r'(```)', out)

    # Replace single newline characters with <br> in non-code sections
    for i in range(len(sections)):
        if i % 2 == 0:  # Non-code section
            sections[i] = re.sub(r'(?<!\n)\n(?!\\n)', r'<br>', sections[i])

    # Join the sections back together
    out = '```'.join(sections)
    return out

def app():
    out = st.chat_input("hello")

    if out:
        print(out)
        st.write(out)
        st.text(out)
        out = out.replace('\n', ' <br> ')
        # out = re.sub(r'(?<!\n)\n(?!\\n)', r'<br>', out)

        st.markdown(out, unsafe_allow_html=True)




app()
