import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import random

st.set_page_config(
    page_title="💬 MEDIA EFFECTS TEST",
    layout="wide" # Keep wide layout for better spacing if needed
)

st.markdown("""
<style>
    /* Import fonts */
    @import url("https://fonts.googleapis.com/css2?family=Inria+Sans:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&display=swap");
    @import url("https://fonts.googleapis.com/css2?family=Inria+Sans:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap");

    /* Title font (Inria Sans) */
    .main h1 {
        font-family: 'Inria Sans', sans-serif !important;
        color: #3f39e3 !important;
    }

    /* Additional selectors to ensure title styling */
    .st-emotion-cache-10trblm h1,
    .stMarkdown h1 {
        font-family: 'Inria Sans', sans-serif !important;
        color: #3f39e3 !important;
    }

    /* All other text (Inter) */
    body, p, div, span, li, a, button, input, textarea, .stTextInput label {
        font-family: 'Inter', sans-serif !important;
    }

    /* Reasoning cue styling */
    .reasoning-cue {
        background-color: #f7f7f7;
        border-left: 3px solid #3f39e3;
        padding: 10px 15px;
        margin: 0px 0px 10px 0px; /* Adjusted margin */
        font-style: italic;
        color: #555;
        height: 100%; /* Let height adjust dynamically */
        box-sizing: border-box; /* Include padding in height/width */
    }

    /* Loading animation */
    .loading-dots {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px; /* Reduced margin */
        margin-bottom: 10px;
    }
    .loading-dots span {
        background-color: #3f39e3;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin: 0 4px;
        animation: bounce 1.5s infinite ease-in-out;
    }
    .loading-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .loading-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    /* Fix some Streamlit UI elements */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem; /* Add more padding at bottom for chat input */
    }

    /* Style the chat input container */
    /* Removed fixed positioning - chat input will now be at the bottom of the flow */
    .stChatInputContainer {
         background-color: white; /* Optional: ensure it has a background */
         /* position: fixed; /* Removed fixed positioning */
         /* bottom: 0; */
         /* width: 100%; /* Adjust width as needed */
         /* z-index: 1000; */
         padding: 10px 0; /* Add some padding */
    }

    /* Ensure columns inside chat messages align well */
    .stChatMessage .stColumns {
        margin-bottom: 0px !important; /* Prevent extra space below columns in a message */
    }
</style>
""", unsafe_allow_html=True)

# Show title
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 MEDIA EFFECTS TEST</h1>", unsafe_allow_html=True)

# Experimental condition selector
reasoning_condition = st.sidebar.selectbox(
    "Reasoning Cue Condition",
    ["None", "Short", "Long"],
    help="Select which type of reasoning cues to display (for testing)",
    key="condition_selector"
)

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if "messages" not in st.session_state:
    # Raw messages for API call
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    # History for display, including reasoning
    st.session_state.chat_history = []

# --- Core Logic Function (Modified) ---
def process_input(user_prompt):
    # Add user's message to API message list
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    # Add user's message to display history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # --- Display Existing Chat History ---
    # Clear the main area and redraw the whole history to place new messages correctly
    chat_display_area.empty()
    with chat_display_area.container():
        for i, message in enumerate(st.session_state.chat_history):
            is_last_message = i == len(st.session_state.chat_history) - 1
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            elif message["role"] == "assistant":
                 with st.chat_message("assistant"):
                    # Check if reasoning exists for this message
                    if "reasoning" in message and message["reasoning"]:
                        # Create columns for this specific message
                        msg_cols = st.columns([0.7, 0.3])
                        with msg_cols[0]:
                            st.markdown(message["content"])
                        with msg_cols[1]:
                            st.markdown(f'<div class="reasoning-cue">{message["reasoning"]}</div>', unsafe_allow_html=True)
                    else:
                        # Display message without reasoning column
                        st.markdown(message["content"])


    # --- Generate and Stream New Response ---
    assistant_response_content = ""
    reasoning_text_full = ""

    # Placeholder for the new assistant message area
    with chat_display_area.container():
        with st.chat_message("assistant"):
            # Create placeholders within the chat message context
            if reasoning_condition != "None":
                cols = st.columns([0.7, 0.3])
                message_placeholder = cols[0].empty()
                reasoning_placeholder = cols[1].empty()
                # Display loading dots in reasoning placeholder initially
                reasoning_placeholder.markdown("""
                    <div class="reasoning-cue">
                        <i>Thinking...</i>
                        <div class="loading-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                message_placeholder = st.empty()
                reasoning_placeholder = None # No placeholder needed if no reasoning

    # --- Reasoning Generation (if applicable) ---
    if reasoning_condition != "None":
        reasoning_prompt_content = ""
        if reasoning_condition == "Short":
            reasoning_prompt_content = "You are an assistant that shows your reasoning process. For the user's query, provide a brief reasoning that shows how you're approaching their question. Use 2-3 short sentences. Don't answer the question yet, just show your thinking approach."
        elif reasoning_condition == "Long":
            reasoning_prompt_content = "You are an assistant that shows your step-by-step reasoning process. For the user's query, provide a detailed paragraph (4-6 sentences) explaining how you're approaching their question. Show your thought process for understanding and analyzing the question. Don't answer their question yet, just explain your reasoning approach."

        reasoning_api_prompt = [
             {"role": "system", "content": reasoning_prompt_content},
             # Include only the *last* user message for reasoning context
             {"role": "user", "content": user_prompt}
        ]

        try:
            reasoning_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=reasoning_api_prompt,
                stream=True,
            )

            # Stream reasoning into its placeholder
            lines = []
            current_line = ""
            reasoning_text_streamed = ""

            for chunk in reasoning_response:
                if chunk.choices[0].delta.content:
                    word = chunk.choices[0].delta.content
                    reasoning_text_streamed += word
                    current_line += word

                    # Simple sentence splitting for live display (adjust if needed)
                    if word.strip() in ['.', '!', '?'] and len(current_line.strip()) > 1:
                       lines.append(current_line.strip())
                       current_line = ""

                    # Update placeholder content during streaming
                    display_text = "<br>".join(lines)
                    if current_line.strip():
                         display_text += ("<br>" if lines else "") + current_line.strip()

                    reasoning_placeholder.markdown(
                        f'<div class="reasoning-cue">{display_text}</div>',
                        unsafe_allow_html=True
                    )
                    # Small delay to simulate typing/thinking per chunk
                    # time.sleep(0.02) # Optional: Adjust speed

            # Ensure the last part is captured and displayed
            if current_line.strip():
                lines.append(current_line.strip())
            reasoning_text_full = "<br>".join(lines) # Store final HTML formatted reasoning
            reasoning_placeholder.markdown(
                 f'<div class="reasoning-cue">{reasoning_text_full}</div>',
                 unsafe_allow_html=True
             )

        except Exception as e:
            st.error(f"Error fetching reasoning: {e}")
            reasoning_placeholder.markdown(
                f'<div class="reasoning-cue"><i>Error getting reasoning.</i></div>',
                unsafe_allow_html=True
            )
            reasoning_text_full = "Error generating reasoning."


    # --- Final Answer Generation ---
    # Show loading in message placeholder before streaming answer
    message_placeholder.markdown("...")
    try:
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages # Use the full conversation history for the answer
            ],
            stream=True,
        )

        # Stream the final answer word by word into its placeholder
        full_response_streamed = ""
        for chunk in final_response:
             if chunk.choices[0].delta.content:
                 word = chunk.choices[0].delta.content
                 full_response_streamed += word
                 message_placeholder.markdown(full_response_streamed + "▌") # Add blinking cursor
                 # time.sleep(0.01) # Optional: Adjust speed

        # Final update to remove cursor
        message_placeholder.markdown(full_response_streamed)
        assistant_response_content = full_response_streamed # Store final text content

    except Exception as e:
         st.error(f"Error fetching final response: {e}")
         message_placeholder.markdown("Sorry, I encountered an error.")
         assistant_response_content = "Error generating response."


    # Add the complete assistant response (with reasoning if generated) to history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": assistant_response_content,
        "reasoning": reasoning_text_full # Add the captured reasoning text
    })

    # No need to manually redraw here as Streamlit handles updates based on state changes
    # when the next input happens or if triggered otherwise. The placeholders were updated live.


# --- Main App Layout ---

# Area where chat history will be displayed
chat_display_area = st.container()

# Display initial chat history
with chat_display_area.container():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
             with st.chat_message("assistant"):
                # Check if reasoning exists for this message
                if "reasoning" in message and message["reasoning"]:
                    # Create columns for this specific message
                    msg_cols = st.columns([0.7, 0.3])
                    with msg_cols[0]:
                        st.markdown(message["content"])
                    with msg_cols[1]:
                        st.markdown(f'<div class="reasoning-cue">{message["reasoning"]}</div>', unsafe_allow_html=True)
                else:
                    # Display message without reasoning column
                    st.markdown(message["content"])

# Chat input at the bottom
prompt = st.chat_input("What would you like to know today?")

if prompt:
    process_input(prompt)
