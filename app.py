import os
import streamlit as st
import requests

# Access the API key from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Check if the API key is set
if GROQ_API_KEY is None:
    st.error("GROQ_API_KEY is not set in Streamlit secrets")
    st.stop()

# API Configuration
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
}

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are an AI assistant that generates personalized emails. "
            "To create a highly personalized email, you will ask the user a series of questions one by one to gather the necessary information. "
            "Ask one question at a time, and wait for the user's response before asking the next question. "
            "Keep the user's answers short (one sentence at most). And try that your questions are not too long just cut to the point. "
            "You should have enough information, like the necessary user and recipient details, the length of the mail, the tone of the mail, and the purpose of the mail."
            "While you generate the final mail, don't add any other message, make the content ready to copy and paste it directly."
        )}
    ]
    st.session_state.email_generated = False
    st.session_state.progress = 0  # Track the progress of questions

# Function to get the LLM's response
def get_llm_response(messages):
    body = {
        "model": "llama3-8b-8192",
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        llm_reply = response.json()["choices"][0]["message"]
        return llm_reply
    else:
        st.error(f"API request failed with status code {response.status_code}")
        st.stop()

# Streamlit UI Setup
st.set_page_config(page_title="Dynamic Personalized Email Generator", page_icon="👾", layout="centered")

st.markdown("<h1 style='text-align: center;'>Dynamic Personalized Email Generator</h1>", unsafe_allow_html=True)

# Add progress bar based on the conversation

# Collapsible conversation history
with st.expander("Conversation History", expanded=False):
    for message in st.session_state.messages[1:]:
        if message["role"] == "assistant":
            st.write(f"**AI:** {message['content']}")
        elif message["role"] == "user":
            st.write(f"**You:** {message['content']}")

# Check if the email has already been generated
if not st.session_state.email_generated:
    # Get the latest AI message or ask the first question
    if len(st.session_state.messages) == 1 or st.session_state.messages[-1]["role"] == "user":
        # Get AI's next question or email
        llm_reply = get_llm_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": llm_reply["content"]})
        # Check if the AI has generated the final email
        if "Here is the email" in llm_reply["content"] or "Subject" in llm_reply["content"]:
            st.session_state.email_generated = True
            st.text_area("Generated Email", llm_reply["content"], height=300)
        else:
            # Display AI's question and wait for user's answer
            st.subheader("Current Question:")
            st.info(llm_reply["content"])
            user_input = st.text_input("Your Answer:", key=str(len(st.session_state.messages)))
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.rerun()
    else:
        # Wait for user's input
        st.subheader("Current Question:")
        user_input = st.text_input("Your Answer:", key=str(len(st.session_state.messages)))
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()
else:
    st.success("Email generation completed!")
    st.text_area("Generated Email", st.session_state.messages[-1]["content"], height=300)

# Add a Start Over button below the text input field
st.markdown("<br>", unsafe_allow_html=True)  # Add some space
if st.button("Start Over"):
    del st.session_state.messages
    st.session_state.email_generated = False
    st.session_state.progress = 0  # Reset progress
    st.rerun()
