import io
import zipfile
from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
import streamlit as st
from neo4j.exceptions import SessionExpired
from streamlit import session_state as ss


def append_user_question(question: str) -> None:
    ss.messages.append({"role": "user", "content": question})
    st.chat_message("user").markdown(question)


def append_llm_response(question: str) -> None:
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.status("thinking...")
        print("question: ", question)
        response: Any = ss.agent.invoke({"input": question, "chat_history": []})[
            "agent_outcome"
        ]

        message_placeholder.markdown(response.answer)

    show_response_information(response=response)

    ss.messages.append({"role": "assistant", "content": response})


def show_response_information(response: Any) -> None:
    if (
        hasattr(response, "cypher")
        and response.cypher
        and not response.answer.startswith("I can only generate queries based on")
    ):
        download_csv_button(cypher_result=response.cypher_result)

        with st.expander("Cypher"):
            if isinstance(response.cypher, str):
                st.code(response.cypher, language="cypher")
                if response.cypher_result: st.json(response.cypher_result, expanded=False)
            else:
                print("LENGTHS: ", len(response.cypher), len(response.cypher_result))
                [
                    (
                        st.write(response.sub_questions[i]),
                        st.code(response.cypher[i], language="cypher"),
                        st.json(response.cypher_result[i] if response.cypher_result else "", expanded=False),
                    )
                    for i in range(len(response.cypher))
                ]

    if hasattr(response, "sources") and response.sources:
        with st.expander("Vector Search"):
            st.write("Source Node IDs")
            st.write(response.sources)


def chat(question: str):
    try:
        append_user_question(question=question)
        append_llm_response(question=question)
    except SessionExpired as e:
        st.error("Neo4j Session expired. Please restart the application.")


def display_chat_history() -> None:
    for message in ss.messages:
        print(message)
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                st.markdown(message["content"].answer)
        if not isinstance(message["content"], str):
            show_response_information(response=message["content"])


def prepare_csv(cypher_result: List[Dict[str, Any]]) -> str:
    # if not cypher_result: return pd.DataFrame().to_csv().encode("utf-8")

    index = [i for i in range(len(cypher_result[0].values()))]
    return pd.DataFrame(data=cypher_result).to_csv(index=index).encode("utf-8")


@st.experimental_fragment()
def download_csv_button(cypher_result: List[Dict[str, Any]]) -> None:
    try:
        print("cypher result in button", cypher_result)
        if len(cypher_result) > 0 and isinstance(cypher_result[0], list):
            content = [prepare_csv(result) for result in cypher_result if result]
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "x") as zip:
                for file_num, csv in enumerate(content):
                    zip.writestr(f"cypher_result_part_{str(file_num+1)}.csv", csv)

            st.download_button(
                label="Download Cypher Results Tables as CSV",
                data=buf.getvalue(),
                file_name="cypher_results.zip",
                mime="application/zip",
                help="The cypher results .csv files in a .zip.",
                key=str(uuid4()),
            )
        else:
            csv = prepare_csv(cypher_result=cypher_result)
            st.download_button(
                label="Download Cypher Results Table as CSV",
                data=csv,
                file_name=f"cypher_results.csv",
                mime="text/csv",
                help="The cypher results .csv file.",
                key=str(uuid4()),
            )
    except Exception as e:
        print("Unable to generate Download Button for most recent question.")
