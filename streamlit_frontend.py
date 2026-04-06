import uuid
import json
import streamlit as st

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langgraph_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)

# ================= Utilities =================

def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages", [])


# ================= Session =================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_thread(st.session_state["thread_id"])

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["chat_threads"][::-1]

selected_thread = None


# ================= Sidebar =================

st.sidebar.title("LangGraph PDF Chatbot")

st.sidebar.markdown(f"Thread ID: `{thread_key}`")

if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()
    st.rerun()


if thread_docs:

    latest_doc = list(thread_docs.values())[-1]

    st.sidebar.success(
        f"{latest_doc.get('filename')}\n"
        f"pages: {latest_doc.get('documents')} | "
        f"chunks: {latest_doc.get('chunks')}"
    )

else:
    st.sidebar.info("No PDF indexed")


uploaded_pdf = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_pdf:

    if uploaded_pdf.name in thread_docs:

        st.sidebar.info("PDF already processed")

    else:

        with st.sidebar.status("Indexing PDF..."):

            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )

            thread_docs[uploaded_pdf.name] = summary

            st.sidebar.success("PDF indexed")


st.sidebar.subheader("Past chats")

for thread_id in threads:

    if st.sidebar.button(
        str(thread_id),
        key=f"thread-{thread_id}"
    ):

        selected_thread = thread_id


# ================= Main =================

st.title("Multi Utility Chatbot")


# ================= Chat History =================

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


        # show stored youtube videos again
        if "videos" in message and message["videos"]:

            st.markdown("### Videos")

            for video in message["videos"]:

                col1, col2 = st.columns([1,3])

                with col1:
                    st.image(video["thumbnail"], width=150)

                with col2:

                    st.markdown(
                        f"#### [{video['title']}]({video['url']})"
                    )

                    st.write("Channel:", video["channel"])

                    st.write("Date:", video["published_at"])

                    st.write(video["description"])

                st.divider()


# ================= Input =================

user_input = st.chat_input(
    "Ask something or search videos"
)


if user_input:

    # save user message
    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input
        }
    )


    with st.chat_message("user"):
        st.markdown(user_input)


    CONFIG = {
        "configurable": {
            "thread_id": thread_key
        }
    }


    # ================= Assistant =================

    with st.chat_message("assistant"):

        status_box = None

        final_text = ""

        youtube_videos = None


        for message_chunk, _ in chatbot.stream(

            {
                "messages": [
                    HumanMessage(content=user_input)
                ]
            },

            config=CONFIG,

            stream_mode="messages",

        ):


            # tool call indicator
            if isinstance(message_chunk, ToolMessage):

                tool_name = getattr(
                    message_chunk,
                    "name",
                    "tool"
                )


                if status_box is None:

                    status_box = st.status(
                        f"Using tool: {tool_name}",
                        expanded=True,
                    )


                # read tool output
                try:

                    if isinstance(
                        message_chunk.content,
                        str
                    ):

                        data = json.loads(
                            message_chunk.content
                        )

                    else:

                        data = message_chunk.content


                    if (
                        isinstance(data, dict)
                        and "videos" in data
                    ):

                        youtube_videos = data["videos"]


                except:
                    pass


            # AI response text
            if isinstance(
                message_chunk,
                AIMessage
            ):

                final_text += message_chunk.content


        # tool finished
        if status_box:

            status_box.update(
                label="Tool finished",
                state="complete",
                expanded=False,
            )


        # show text response
        st.markdown(final_text)


        # show videos
        if youtube_videos:

            st.markdown("### Videos")

            for video in youtube_videos:

                col1, col2 = st.columns([1,3])


                with col1:

                    st.image(
                        video["thumbnail"],
                        width=150
                    )


                with col2:

                    st.markdown(
                        f"#### [{video['title']}]({video['url']})"
                    )

                    st.write(
                        "Channel:",
                        video["channel"]
                    )

                    st.write(
                        "Date:",
                        video["published_at"]
                    )

                    st.write(
                        video["description"]
                    )


                st.divider()


    # store assistant message
    st.session_state["message_history"].append(

        {
            "role": "assistant",

            "content": final_text,

            "videos": youtube_videos,
        }

    )


    # pdf metadata
    doc_meta = thread_document_metadata(
        thread_key
    )


    if doc_meta:

        st.caption(

            f"PDF: {doc_meta.get('filename')} | "

            f"pages: {doc_meta.get('documents')} | "

            f"chunks: {doc_meta.get('chunks')}"

        )


st.divider()


# ================= Load old thread =================

if selected_thread:

    st.session_state["thread_id"] = selected_thread

    messages = load_conversation(
        selected_thread
    )


    temp_messages = []


    for msg in messages:

        role = (
            "user"
            if isinstance(msg, HumanMessage)
            else "assistant"
        )


        temp_messages.append(

            {
                "role": role,

                "content": msg.content
            }

        )


    st.session_state["message_history"] = temp_messages

    st.session_state["ingested_docs"].setdefault(
        str(selected_thread),
        {}
    )


    st.rerun()