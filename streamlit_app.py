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
    
    /* Hide the default Streamlit padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    
    /* Custom layout styles */
    .custom-layout {
        display: flex;
        width: 100%;
    }
    
    .chat-column {
        flex: 7;
        padding-right: 20px;
        overflow-y: auto;
        height: calc(100vh - 120px);
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Make the iframe container stick on the right */
    .iframe-container {
        position: fixed;
        top: 150px;
        right: 20px;
        width: 27%;  /* Match this to the 3fr from the grid layout */
        z-index: 1000;
        background: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 5px;
        max-height: 70vh;
        overflow: auto;
    }
    
    /* Style the iframe itself */
    .reasoning-iframe {
        width: 100%;
        height: 100%;
        border: none;
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
    help="Select which type of reasoning cues to display (for testing)",
    key="condition_selector"
)

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

# Create a container for chat that takes 70% of the width
chat_col1, chat_col2 = st.columns([7, 3])

with chat_col1:
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

# Create an iframe to display reasoning in a fixed position
if "iframe_height" not in st.session_state:
    st.session_state.iframe_height = 300

# Function to update the reasoning content
def update_reasoning_content(content):
    st.session_state.reasoning_content = content
    
    # Calculate a reasonable height based on content length
    content_length = len(content)
    if content_length < 100:
        height = 150
    elif content_length < 300:
        height = 250
    else:
        height = 350
    
    st.session_state.iframe_height = height
    
    # Create HTML for the reasoning content
    reasoning_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 10px;
            }}
            .reasoning-cue {{
                background-color: #f7f7f7;
                border-left: 3px solid #3f39e3;
                padding: 10px 15px;
                margin: 5px 0;
                font-style: italic;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="reasoning-cue">{content}</div>
    </body>
    </html>
    """
    
    return reasoning_html

# Create a fixed iframe for reasoning content
iframe_container = st.empty()

# Function to process user input and generate responses
def process_input(user_prompt):
    # Add user's message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Process response based on condition
    if reasoning_condition == "None":
        # Show loading dots in the reasoning iframe
        loading_html = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                }
                .loading-dots {
                    display: flex;
                    align-items: center;
                    justify-content: center;
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
            </style>
        </head>
        <body>
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
        </body>
        </html>
        """
        
        iframe_container.markdown(
            f'<div class="iframe-container"><iframe srcdoc="{loading_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
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
        
        # Clear the reasoning iframe
        iframe_container.empty()
        
        # Display the response in the chat
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
                    
                    # Update the reasoning iframe
                    reasoning_html = update_reasoning_content(displayed_text)
                    iframe_container.markdown(
                        f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning iframe
                    reasoning_html = update_reasoning_content(displayed_text)
                    iframe_container.markdown(
                        f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                        unsafe_allow_html=True
                    )
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            reasoning_html = update_reasoning_content(displayed_text)
            iframe_container.markdown(
                f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                unsafe_allow_html=True
            )
        
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
        
        # Display the response in the chat
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
                    
                    # Update the reasoning iframe
                    reasoning_html = update_reasoning_content(displayed_text)
                    iframe_container.markdown(
                        f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Regular update (not at sentence end)
                    displayed_text = "<br>".join(lines)
                    if current_line:
                        displayed_text += "<br>" + current_line
                    
                    # Update the reasoning iframe
                    reasoning_html = update_reasoning_content(displayed_text)
                    iframe_container.markdown(
                        f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                        unsafe_allow_html=True
                    )
        
        # Make sure we add the last line if it doesn't end with a period
        if current_line:
            lines.append(current_line)
            displayed_text = "<br>".join(lines)
            reasoning_html = update_reasoning_content(displayed_text)
            iframe_container.markdown(
                f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
                unsafe_allow_html=True
            )
        
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
        
        # Display the response in the chat
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
    reasoning_html = update_reasoning_content(st.session_state.reasoning_content)
    iframe_container.markdown(
        f'<div class="iframe-container"><iframe srcdoc="{reasoning_html}" class="reasoning-iframe" height="{st.session_state.iframe_height}px"></iframe></div>',
        unsafe_allow_html=True
    )
