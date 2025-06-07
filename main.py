# -*- coding: utf-8 -*-
from typing import Set
import streamlit as st
from backend.core import run_llm

# Configure page
st.set_page_config(
    page_title="LangChain Documentation Helper",
    page_icon="🤖",
    layout="wide"
)

# Sidebar for user information
with st.sidebar:
    st.header("👤 User Profile")

    # Profile picture upload
    uploaded_file = st.file_uploader(
        "Upload Profile Picture",
        type=['png', 'jpg', 'jpeg'],
        help="Upload your profile picture"
    )

    if uploaded_file is not None:
        st.image(uploaded_file, width=150, caption="Profile Picture")
    else:
        # Default avatar
        st.image("https://via.placeholder.com/150/cccccc/666666?text=👤", width=150)

    # User information form
    with st.form("user_info_form"):
        user_name = st.text_input(
            "Full Name",
            value=st.session_state.get("user_name", ""),
            placeholder="Enter your full name"
        )

        user_email = st.text_input(
            "Email",
            value=st.session_state.get("user_email", ""),
            placeholder="Enter your email address"
        )

        user_role = st.selectbox(
            "Role",
            ["Developer", "Student", "Researcher", "Data Scientist", "Other"],
            index=0 if "user_role" not in st.session_state else
            ["Developer", "Student", "Researcher", "Data Scientist", "Other"].index(
                st.session_state.get("user_role", "Developer"))
        )

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            st.session_state["user_name"] = user_name
            st.session_state["user_email"] = user_email
            st.session_state["user_role"] = user_role
            st.success("Profile saved!")

    # Display current user info
    if st.session_state.get("user_name"):
        st.markdown("---")
        st.markdown("**Current User:**")
        st.write(f"**Name:** {st.session_state['user_name']}")
        st.write(f"**Email:** {st.session_state['user_email']}")
        st.write(f"**Role:** {st.session_state['user_role']}")

    # Chat statistics
    if st.session_state.get("chat_answers_history"):
        st.markdown("---")
        st.markdown("**Chat Statistics:**")
        st.write(f"Messages sent: {len(st.session_state['user_prompt_history'])}")
        st.write(f"Responses received: {len(st.session_state['chat_answers_history'])}")

    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["chat_answers_history"] = []
        st.session_state["user_prompt_history"] = []
        st.session_state["chat_history"] = []
        st.rerun()

# Main content area
st.header("🤖 LangChain Udemy Course - Documentation Helper Bot")

# Welcome message with user name
if st.session_state.get("user_name"):
    st.write(f"Welcome back, **{st.session_state['user_name']}**! 👋")
else:
    st.info("👈 Please fill out your profile information in the sidebar to get started!")

prompt = st.text_input("Prompt", placeholder="Enter your prompt here..")

# Initialize session state
if ("chat_answers_history" not in st.session_state
        and "user_prompt_history" not in st.session_state
        and "chat_history" not in st.session_state
):
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []


def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{1 + i}. {source}\n"
    return sources_string


# Process user input
if prompt:
    # Only process if user has filled out basic info
    if not st.session_state.get("user_name") or not st.session_state.get("user_email"):
        st.warning("Please complete your profile information in the sidebar before chatting!")
    else:
        with st.spinner("Generating response.."):
            generated_response = run_llm(query=prompt, chat_history=st.session_state["chat_history"])
            sources = set([doc.metadata["source"] for doc in generated_response["source_documents"]])
            formatted_response = (
                f"{generated_response['result']} \n\n {create_sources_string(sources)}"
            )

            st.session_state["user_prompt_history"].append(prompt)
            st.session_state["chat_answers_history"].append(formatted_response)
            st.session_state["chat_history"].append(("human", prompt))
            st.session_state["chat_history"].append(("ai", generated_response['result']))

# Display chat history
if st.session_state["chat_answers_history"]:
    st.markdown("---")
    st.subheader("💬 Chat History")

    for generated_response, user_query in zip(
            st.session_state["chat_answers_history"],
            st.session_state["user_prompt_history"]
    ):
        # User message
        with st.chat_message("user", avatar="👤"):
            st.write(user_query)

        # Assistant message
        with st.chat_message("assistant", avatar="🤖"):
            st.write(generated_response)