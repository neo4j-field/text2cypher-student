import streamlit as st

from .questions import get_demo_questions


def sidebar() -> None:
    """
    The Streamlit app side bar.
    """

    demo_questions = get_demo_questions(source=st.session_state["source"])

    st.sidebar.title("Demo Questions")
    with st.sidebar.expander("Demo Questions"):
        for ex in demo_questions:
            if st.sidebar.button(label=ex, key=ex):
                st.session_state["current_question"] = ex

    st.sidebar.divider()
    if len(st.session_state.get("messages", list())) > 0:
        if st.sidebar.button("Reset Chat", type="primary"):
            st.session_state["messages"] = list()
            del st.session_state["current_question"]
