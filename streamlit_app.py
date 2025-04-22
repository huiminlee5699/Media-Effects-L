import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import random

st.set_page_config(
    page_title="💬 MEDIA EFFECTS TEST",
    layout="wide"  # Use wide layout to accommodate columns
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
        margin: 10px 0;
        font-style: italic;
        color: #555;
        height: 100%;
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
    
    /* Fix some Streamlit UI elements */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Style the chat input to be at the bottom of left column */
    .chat-input {
        position: fixed;
        bottom: 20px;
        width: calc(70% - 40px);
    }
    
    /* Make column divider more visible */
    .column-divider {
        border-left: 1px solid #e0e0e0;
        height: 100vh;
    }
    
    /* Fix column heights */
    .stColumn {
        height: 100vh;
    }
</style>
""", unsafe_allow_html=True)

# Show title
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 MEDIA EFFECTS TEST</h1>", unsafe_allow_html=True)

# Experimental condition selector (you would remove this in the actual study
# and set it based on participant assignment)
reasoning_condition = st.sidebar.selectbox(
    "Reasoning Cue Condition",
    ["None", "Short", "Long"],
    help="Select which type of reasoning cues to display (for testing)"
)

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_response" not in st.session_state:
    st.session_state.current_response = ""
    
if "reasoning_text" not in st.session_state:
    st.session_state.reasoning_text = ""
    
if "processing" not in st.session_state:
    st.session_state.processing = False

# Function to generate responses (both reasoning and main response)
def generate_response(prompt):
    st.session_state.processing = True
    
    # Add user message to chat history
    if {"role": "user", "content": prompt} not in st.session_state.messages:
        st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process based on condition
    if reasoning_condition == "None":
        # Just show loading dots in the reasoning column
        with col2:
            with reasoning_placeholder.container():
                st.markdown("""
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
                """, unsafe_allow_html=True)
        
        # Get the final response without showing reasoning
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
        
        # Clear the loading animation from reasoning column
        with col2:
            reasoning_placeholder.empty()
        
        # Stream the final response word by word in the chat column
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                full_response += word
                # Update response in session state to trigger rerun
                st.session_state.current_response = full_response
                # Force a rerun to update the UI
                st.experimental_rerun()
        
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.current_response = ""
        
    elif reasoning_condition == "Short":
        # Get reasoning from model with 2-3 sentences
        reasoning_prompt = [
            {"role": "system", "content": "You are an assistant that shows your reasoning process. For the user's query, provide a brief reasoning that shows how you're approaching their question. Use 2-3 short sentences. Don't answer the question yet, just show your thinking approach."},
            {"role": "user", "content": prompt}
        ]
        
        reasoning_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=reasoning_prompt,
            stream=True,
        )
        
        # Stream the short reasoning line by line in the reasoning column
        reasoning_text = ""
        lines = []
        current_line = ""
        
        # Process the reasoning text line by line
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
                    
                    with col2:
                        reasoning_placeholder.markdown(
                            f'<div class="reasoning-cue">{displayed_text}</div>', 
                            unsafe_allow_html=True
                        )
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    with col2:
                        reasoning_placeholder.markdown(
                            f'<div class="reasoning-cue">{displayed_text}</div>', 
                            unsafe_allow_html=True
                        )
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            with col2:
                reasoning_placeholder.markdown(
                    f'<div class="reasoning-cue">{displayed_text}</div>', 
                    unsafe_allow_html=True
                )
        
        # Store the reasoning text
        st.session_state.reasoning_text = displayed_text
        
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
        
        # Stream the final response word by word
        full_response = ""
        for chunk in final_response:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                full_response += word
                # Update response in session state
                st.session_state.current_response = full_response
                # Force a rerun to update the UI
                st.experimental_rerun()
        
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.current_response = ""
            
    elif reasoning_condition == "Long":
        # Get detailed reasoning from model
        reasoning_prompt = [
            {"role": "system", "content": "You are an assistant that shows your step-by-step reasoning process. For the user's query, provide a detailed paragraph (4-6 sentences) explaining how you're approaching their question. Show your thought process for understanding and analyzing the question. Don't answer their question yet, just explain your reasoning approach."},
            {"role": "user", "content": prompt}
        ]
        
        reasoning_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=reasoning_prompt,
            stream=True,
        )
        
        # Stream the long reasoning line by line in the reasoning column
        reasoning_text = ""
        lines = []
        current_line = ""
        
        # Process the reasoning text line by line
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
                    
                    with col2:
                        reasoning_placeholder.markdown(
                            f'<div class="reasoning-cue">{displayed_text}</div>', 
                            unsafe_allow_html=True
                        )
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    with col2:
                        reasoning_placeholder.markdown(
                            f'<div class="reasoning-cue">{displayed_text}</div>', 
                            unsafe_allow_html=True
                        )
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            with col2:
                reasoning_placeholder.markdown(
                    f'<div class="reasoning-cue">{displayed_text}</div>', 
                    unsafe_allow_html=True
                )
        
        # Store the reasoning text
        st.session_state.reasoning_text = displayed_text
        
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
        
        # Stream the final response word by word
        full_response = ""
        for chunk in final_response:
            if chunk.choices[0].delta.content:
                word = chunk.choices[0].delta.content
                full_response += word
                # Update response in session state
                st.session_state.current_response = full_response
                # Force a rerun to update the UI
                st.experimental_rerun()
        
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.current_response = ""
    
    st.session_state.processing = False

# Create a two-column layout
col1, col2 = st.columns([0.7, 0.3])

# Main chat column
with col1:
    st.subheader("Chat")
    
    # Display the existing chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Show current response being generated (if any)
    if st.session_state.current_response:
        with st.chat_message("assistant"):
            st.markdown(st.session_state.current_response)
    
    # Add chat input
    prompt = st.chat_input("What would you like to know today?", disabled=st.session_state.processing)

# Reasoning column
with col2:
    # No header as per request
    
    # Create a placeholder for the reasoning content
    reasoning_placeholder = st.empty()
    
    # Display current reasoning if available
    if st.session_state.reasoning_text and not st.session_state.processing:
        reasoning_placeholder.markdown(f'<div class="reasoning-cue">{st.session_state.reasoning_text}</div>', unsafe_allow_html=True)

# Process the user's input
if prompt and not st.session_state.processing:
    # Trigger response generation
    generate_response(prompt)
