import streamlit as st
import uuid

from langchain_core.messages import HumanMessage

from langgraph_backend import chatbot, reterieve_all_threads


# generate chat id
def generate_thread_id():
    return str(uuid.uuid4())


# reset conversation
def reset_chat():

    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id

    add_thread(thread_id)

    st.session_state["message_history"] = []


# store thread
def add_thread(thread_id):

    if thread_id not in st.session_state["chat_threads"]:

        st.session_state["chat_threads"].append(thread_id)


# load old messages
def load_conversation(thread_id):

    state = chatbot.get_state(

        config={"configurable": {"thread_id": thread_id}}

    )

    # FIX: messages instead of message
    if state and "messages" in state.values:

        return state.values["messages"]

    return []


# session state
if "message_history" not in st.session_state:

    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:

    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:

    st.session_state["chat_threads"] = reterieve_all_threads()


add_thread(st.session_state["thread_id"])


# sidebar
st.sidebar.title("AI Agent")

if st.sidebar.button("New Chat"):

    reset_chat()


st.sidebar.header("Conversations")


# conversation list
for thread_id in st.session_state["chat_threads"][::-1]:

    if st.sidebar.button(thread_id):

        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        formatted_messages = []

        for msg in messages:

            role = "user" if isinstance(msg, HumanMessage) else "assistant"

            formatted_messages.append(

                {"role": role, "content": msg.content}

            )

        st.session_state["message_history"] = formatted_messages


# show chat history
for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# user input
user_input = st.chat_input("Ask anything...")


if user_input and user_input.strip() != "":

    st.session_state["message_history"].append(

        {"role": "user", "content": user_input}

    )

    with st.chat_message("user"):

        st.write(user_input)


    CONFIG = {

        "configurable": {

            "thread_id": st.session_state["thread_id"]

        }

    }


    with st.chat_message("assistant"):

        response_text = ""
        placeholder = st.empty()


        # FIX: messages instead of message
        for chunk, metadata in chatbot.stream(

            {

                "messages": [

                    HumanMessage(content=user_input)

                ]

            },

            config=CONFIG,

            stream_mode="messages"

        ):

            if chunk.content:

                response_text += chunk.content

                placeholder.markdown(response_text)


    st.session_state["message_history"].append(

        {"role": "assistant", "content": response_text}

    )