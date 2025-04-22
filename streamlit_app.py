import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import random

st.set_page_config(
    page_title="💬 MEDIA EFFECTS TEST",
    layout="wide"  # Use wide layout to accommodate columns
)

# Custom CSS for styling
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
        margin: 10px 0;
        font-style: italic;
        color: #555;
    }
    
    /* Loading animation */
    .loading-dots {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
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
    
    /* Make the sidebar sticky */
    [data-testid="stSidebar"] {
        position: fixed !important;
    }
    
    /* Fix some Streamlit UI elements */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Fixed reasoning section */
    .fixed-reasoning {
        position: fixed;
        top: 150px;
        right: 30px;
        width: 25%;
        max-height: 70vh;
        overflow-y: auto;
        z-index: 1000;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Show title
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 MEDIA EFFECTS TEST</h1>", unsafe_allow_html=True)

# Experimental condition selector (you would remove this in the actual study
# and set it based on participant assignment)
with st.sidebar:
    reasoning_condition = st.selectbox(
        "Reasoning Cue Condition",
        ["None", "Short", "Long"],
        help="Select which type of reasoning cues to display (for testing)",
        key="condition_selector"
    )

# Place for fixed reasoning display (using custom HTML/CSS instead of iframe)
reasoning_container = st.container()

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "reasoning_content" not in st.session_state:
    st.session_state.reasoning_content = ""

# Create two columns for layout
chat_col, _ = st.columns([7, 3])

# Display chat in the left column
with chat_col:
    st.subheader("Chat")
    
    # Display the existing chat messages
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Add chat input at the bottom
    prompt = st.chat_input("What would you like to know today?")

# JavaScript to ensure the reasoning container stays fixed
components.html("""
<script>
document.addEventListener('DOMContentLoaded', () => {
    // Function to fix the reasoning container position
    const fixReasoningPosition = () => {
        const reasoningDiv = document.getElementById('fixed-reasoning');
        if (reasoningDiv) {
            reasoningDiv.className = 'fixed-reasoning';
        }
    };
    
    // Run when DOM loads
    fixReasoningPosition();
    
    // Also run on scroll events
    window.addEventListener('scroll', fixReasoningPosition);
    
    // Create a mutation observer to detect changes in the DOM
    const observer = new MutationObserver(fixReasoningPosition);
    observer.observe(document.body, { subtree: true, childList: true });
});
</script>
""", height=0)

# Function to update the reasoning content
def update_reasoning(content):
    st.session_state.reasoning_content = content
    
    # Display the reasoning in a fixed div
    reasoning_container.markdown(
        f'<div id="fixed-reasoning" class="fixed-reasoning"><div class="reasoning-cue">{content}</div></div>',
        unsafe_allow_html=True
    )

# Function to process user input and generate responses
def process_input(user_prompt):
    # Add user's message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Process response based on condition
    if reasoning_condition == "None":
        # Show loading dots in the reasoning column
        reasoning_container.markdown(
            '<div id="fixed-reasoning" class="fixed-reasoning"><div class="loading-dots"><span></span><span></span><span></span></div></div>',
            unsafe_allow_html=True
        )
        
        # Get the final response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        # Simulate thinking time
        time.sleep(2)
        
        # Clear the reasoning column
        reasoning_container.empty()
        
        # Display the response in the chat column
        with chat_col:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response word by word
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        word = chunk.choices[0].delta.content
                        full_response += word
                        message_placeholder.markdown(full_response)
                
                # Add the final response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    elif reasoning_condition == "Short":
        # Get reasoning with 2-3 sentences
        reasoning_prompt = [
            {"role": "system", "content": "You are an assistant that shows your reasoning process. For the user's query, provide a brief reasoning that shows how you're approaching their question. Use 2-3 short sentences. Don't answer the question yet, just show your thinking approach."},
            {"role": "user", "content": user_prompt}
        ]
        
        reasoning_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=reasoning_prompt,
            stream=True,
        )
        
        # Display reasoning line by line
        lines = []
        current_line = ""
        reasoning_text = ""
        
        for chunk in reasoning_response:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                reasoning_text += word
                current_line += word
                
                # Check if we've reached a sentence end
                if word in ['.', '!', '?'] and len(current_line.strip()) > 0:
                    lines.append(current_line)
                    current_line = ""
                    
                    # Display all lines collected so far
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning container
                    update_reasoning(displayed_text)
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning container
                    update_reasoning(displayed_text)
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            update_reasoning(displayed_text)
        
        # Get the final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        # Wait a moment to let user read the reasoning
        time.sleep(1)
        
        # Display the response in the chat column
        with chat_col:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response word by word
                for chunk in final_response:
                    if chunk.choices[0].delta.content:
                        word = chunk.choices[0].delta.content
                        full_response += word
                        message_placeholder.markdown(full_response)
                
                # Add the final response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    elif reasoning_condition == "Long":
        # Get detailed reasoning
        reasoning_prompt = [
            {"role": "system", "content": "You are an assistant that shows your step-by-step reasoning process. For the user's query, provide a detailed paragraph (4-6 sentences) explaining how you're approaching their question. Show your thought process for understanding and analyzing the question. Don't answer their question yet, just explain your reasoning approach."},
            {"role": "user", "content": user_prompt}
        ]
        
        reasoning_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=reasoning_prompt,
            stream=True,
        )
        
        # Display reasoning line by line
        lines = []
        current_line = ""
        reasoning_text = ""
        
        for chunk in reasoning_response:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                reasoning_text += word
                current_line += word
                
                # Check if we've reached a sentence end
                if word in ['.', '!', '?'] and len(current_line.strip()) > 0:
                    lines.append(current_line)
                    current_line = ""
                    
                    # Display all lines collected so far
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning container
                    update_reasoning(displayed_text)
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning container
                    update_reasoning(displayed_text)
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            update_reasoning(displayed_text)
        
        # Get the final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        # Wait a moment to let user read the reasoning
        time.sleep(1)
        
        # Display the response in the chat column
        with chat_col:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Stream the response word by word
                for chunk in final_response:
                    if chunk.choices[0].delta.content:
                        word = chunk.choices[0].delta.content
                        full_response += word
                        message_placeholder.markdown(full_response)
                
                # Add the final response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# Handle user input
if prompt:
    process_input(prompt)
elif st.session_state.reasoning_content:
    # If there's existing reasoning content, keep displaying it
    update_reasoning(st.session_state.reasoning_content)
