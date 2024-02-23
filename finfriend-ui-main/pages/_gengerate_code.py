import streamlit as st
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES

st.set_page_config(
    page_title="Generate Code",
    page_icon="🪚",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

import asyncio
import io
import os
import pathlib
from os.path import isfile, join
import pandas as pd
import helpers.sidebar
import helpers.util
import services.prompts
import services.llm

helpers.sidebar.show()



st.header("Generate Code")
st.write(" review code.  The use case is for a developer to provide some code and to ask for a code review.")
st.write(" debug code.  The use case is for a developer to provide some code and to ask for help debugging the code.")
st.write(" modify code.  The use case is for a developer to provide some code and to ask for some modification instructions.")



# ===========================================================================================
# ===================================== sidebar status ======================================
# ===========================================================================================

# Initiate the status session
if 'menu_status' not in st.session_state:
    st.session_state.menu_status = "default"

def get_menu_status()->str:
    return st.session_state.menu_status

def set_menu_status(status:str):
    st.session_state.menu_status = status

# =================================================================================================================
# =================================================== module END ==================================================
# =================================================================================================================

code = st_ace(
    value="",
    language="python",
    placeholder="You can provide some code here",
    theme="solarized_light",
    keybinding="vscode",
    font_size=14,
    tab_size=4,
    wrap=False,
    show_gutter=True,
    show_print_margin=True,
    auto_update=False,
    readonly=False,
    key="editor-basic"
)


# Choose the language of the provided code
language=st.sidebar.selectbox("Language mode", options=LANGUAGES, index=121)
# Choose the ide mode of the given code
keybinding=st.sidebar.selectbox(
            "Keybinding mode", options=KEYBINDINGS, index=3
        )
# review the code
review_button = st.sidebar.button('review code')
# debug the code
debug_button = st.sidebar.button('debug code')
# mofify the code
modify_button = st.sidebar.button('modify mode')

st.write('Your code is:')
st.code(code, language="python")
st.write('### Advice...')
advice =st.markdown("")


# =================================================================================================================
# ====================================Review, Debug and Modify implemetation module================================
# =================================================================================================================

# ==================================== Review implemetation ================================
if review_button:
    set_menu_status('review')
if get_menu_status == 'review':
    st.write('status is review')
    review_prompt = services.prompts.review_prompt(code, 'python', 'VS Code')
    messages = services.llm.create_conversation_starter(review_prompt)
    messages.append({"role": "user", "content": review_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))

# ==================================== Debug implemetation ================================
    
if debug_button or get_menu_status == 'debug':
    set_menu_status('debug')
    debug_prompt = services.prompts.debug_prompt(code, 'python', 'VS Code')
    messages = services.llm.create_conversation_starter(debug_prompt)
    messages.append({"role": "user", "content": debug_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))

# ==================================== Modify implemetation ================================
    
if modify_button:
    set_menu_status('modify')

if get_menu_status == 'modify':

    # ==================================== modify chat bar ================================

    # Define a Streamlit layout using custom CSS
    st.markdown(
        """
        <style>
        .stApp {
            margin-bottom: 50px; /* Add some space at the bottom of the page */
        }
        .stButton>button {
            width: auto; /* Adjust button width */
        }
        .stText>div>div {
            justify-content: flex-start; /* Align chat messages to the left */
        }
        .stTextInput>div>div {
            width: 90%; /* Adjust input field width */
            position: fixed; /* Fix position */
            bottom: 5px; /* Place at the bottom */
            left: 5%; /* Center horizontally */
            z-index: 100; /* Ensure it's above other content */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Input field for user to type
    user_req = st.chat_input("Supplementary requirements here...")
    # You can use user_input variable to retrieve the input value

# ==================================== end chat bar ================================

    # Ensure the session state is initialized
    initial_messages = [{"role": "system",
                         "content": services.prompts.quick_chat_system_prompt()}]
    st.session_state.messages = initial_messages

    # Print all messages in the session state
    # for message in [m for m in st.session_state.messages if m["role"] == "assistant"]:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])


    # Chat with the LLM, and update the messages list with the response.
    # Handles the chat UI and partial responses along the way.
    async def chat(messages):
        # with st.chat_message("user"):
        #     st.markdown(modify_prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            messages = await helpers.util.run_conversation(messages, message_placeholder)
            st.session_state.messages = messages
        return messages
    
    # React to the user prompt
    if user_req:
        if modify_req := user_req:
            modify_prompt = services.prompts.modify_code_prompt(code, modify_req, 'python', 'VS Code')
            st.session_state.messages.append({"role":"user", "content":modify_prompt})
            asyncio.run(chat(st.session_state.messages))

# =================================================================================================================
# =================================================== module END ==================================================
# =================================================================================================================
    
    
 


