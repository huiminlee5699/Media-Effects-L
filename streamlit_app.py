import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import random
import re

st.set_page_config(
    page_title="💬 CHATBOT AI",
    layout="wide"  # Use wide layout for better space allocation
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
    }
    
    /* Loading animation */
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
    
    /* Chat layout styling for two-column display */
    .chat-columns {
        display: flex;
        width: 100%;
    }
    .column-left {
        width: 35%;
        padding-right: 15px;
    }
    .column-right {
        width: 65%;
        padding-left: 15px;
        border-left: 1px solid #eee;
    }
    
    /* Custom Dropdown Styling */
    .reasoning-dropdown {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 10px;
        overflow: hidden;
        background-color: #f7f7f7;
    }
    .dropdown-header {
        padding: 12px 15px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f7f7f7;
        border-bottom: 1px solid #e0e0e0;
        font-weight: 500;
        color: #333;
    }
    .dropdown-header:hover {
        background-color: #f0f0f0;
    }
    .dropdown-content {
        padding: 12px 15px;
        background-color: white;
        border-top: 1px solid #e0e0e0;
        font-style: italic;
        color: #555;
    }
    .dropdown-icon {
        transition: transform 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Show title and description.
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 CHATBOT AI</h1>", unsafe_allow_html=True)
st.write(
    "Welcome to Chatbot, a new OpenAI-powered chatbot! "
    "Feel free to ask me anything!"
)

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

# Create session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "reasoning_history" not in st.session_state:
    st.session_state.reasoning_history = []
if "dropdown_states" not in st.session_state:
    st.session_state.dropdown_states = {}

# Function to split text into sentences
def split_into_sentences(text):
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if s.strip()]

# Function to create dropdown component for reasoning
def create_dropdown(id, header_text, content):
    dropdown_key = f"dropdown_{id}"
    if dropdown_key not in st.session_state.dropdown_states:
        st.session_state.dropdown_states[dropdown_key] = False  # Default closed
    
    is_open = st.session_state.dropdown_states.get(dropdown_key, False)
    icon = "▼" if is_open else "▶"
    
    # Truncate header text if it's too long
    header_display = header_text[:50] + "..." if len(header_text) > 50 else header_text
    
    html = f"""
    <div class="reasoning-dropdown" id="{dropdown_key}">
        <div class="dropdown-header" onclick="toggleDropdown('{dropdown_key}')">
            <span>{header_display}</span>
            <span class="dropdown-icon" id="{dropdown_key}_icon">{icon}</span>
        </div>
        <div class="dropdown-content" id="{dropdown_key}_content" style="display: {'block' if is_open else 'none'}">
            {content}
        </div>
    </div>
    <script>
    function toggleDropdown(id) {{
        const content = document.getElementById(id + '_content');
        const icon = document.getElementById(id + '_icon');
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            icon.innerHTML = '▼';
            // Send message to Streamlit to update state
            const data = {{
                dropdown: id,
                isOpen: true
            }};
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: data
            }}, '*');
        }} else {{
            content.style.display = 'none';
            icon.innerHTML = '▶';
            // Send message to Streamlit to update state
            const data = {{
                dropdown: id,
                isOpen: false
            }};
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: data
            }}, '*');
        }}
    }}
    </script>
    """
    components.html(html, height=60 if not is_open else 150)
    return is_open

# Custom component to handle dropdown state changes
def handle_dropdown_change():
    key = "dropdown_handler"
    ret = components.html(
        """
        <script>
        window.addEventListener('message', function(event) {
            const data = event.data;
            if (data.type === 'streamlit:componentReady') {
                window.parent.addEventListener('message', function(parentEvent) {
                    const parentData = parentEvent.data;
                    if (parentData.dropdown) {
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: parentData
                        }, '*');
                    }
                });
            }
        });
        </script>
        """,
        height=0,
        key=key
    )
    if ret and 'dropdown' in ret:
        dropdown_id = ret['dropdown']
        is_open = ret['isOpen']
        st.session_state.dropdown_states[dropdown_id] = is_open
        st.experimental_rerun()

# Initialize dropdown handler
handle_dropdown_change()

# Display the existing chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and i < len(st.session_state.reasoning_history) and st.session_state.reasoning_history[i]:
            # Create two columns for layout
            col1, col2 = st.columns([35, 65])
            
            with col1:
                # Create dropdown for reasoning
                reasoning = st.session_state.reasoning_history[i]
                if reasoning:  # Only display if there's reasoning
                    # Get the first sentence for the header
                    sentences = split_into_sentences(reasoning)
                    header = sentences[0] if sentences else "Reasoning"
                    create_dropdown(f"history_{i}", header, reasoning)
            
            with col2:
                # Display the response
                st.markdown(message["content"])
        else:
            # Regular message display
            st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("What would you like to know today?"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create a two-column layout for the assistant's response
    with st.chat_message("assistant"):
        # Create explicit columns using Streamlit's column feature
        col1, col2 = st.columns([35, 65])
        
        with col1:
            reasoning_placeholder = st.empty()
            
        with col2:
            response_container = st.empty()
        
        final_reasoning = ""  # Store the final reasoning for history
        
        if reasoning_condition == "None":
            # Just show loading dots in the reasoning area
            reasoning_placeholder.markdown("""
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
                stream=False,
            )
            
            # Simulate thinking time before showing response
            time.sleep(2)
            
            # Clear the reasoning area and display the final response
            reasoning_placeholder.empty()  # We still clear the loading dots
            full_response = response.choices[0].message.content
            response_container.markdown(full_response)
            
            # No reasoning to store
            final_reasoning = ""
            
        elif reasoning_condition == "Short":
            # Get reasoning from model with 2-3 brief sentences
            reasoning_prompt = [
                {"role": "system", "content": "You are an assistant that shows your reasoning process. For the user's query, provide 2-3 very brief sentences showing how you're approaching their question. Each sentence should be concise (under 15 words). Don't answer the question yet, just show your thinking approach."},
                {"role": "user", "content": prompt}
            ]
            
            reasoning_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=reasoning_prompt,
                stream=False,
            )
            
            # Split the reasoning into sentences and display them one by one
            reasoning_text = reasoning_response.choices[0].message.content
            sentences = split_into_sentences(reasoning_text)
            
            # Show each sentence one at a time, replacing the previous one
            for sentence in sentences:
                reasoning_placeholder.markdown(f'<div class="reasoning-cue">{sentence}</div>', unsafe_allow_html=True)
                time.sleep(1.5)  # Wait a moment between sentences
            
            # Store the full reasoning for history
            final_reasoning = reasoning_text
            
            # Get the final response
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Before streaming response, replace the reasoning area with dropdown
            header = sentences[0] if sentences else "Reasoning"
            with reasoning_placeholder.container():
                create_dropdown(f"current", header, reasoning_text)
            
            # Stream the final response (keep reasoning visible)
            full_response = ""
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response)
            
        elif reasoning_condition == "Long":
            # Get detailed reasoning from model
            reasoning_prompt = [
                {"role": "system", "content": "You are an assistant that shows your step-by-step reasoning process. For the user's query, provide a detailed paragraph (4-6 sentences) explaining how you're approaching their question. Show your thought process for understanding and analyzing the question. Don't answer their question yet, just explain your reasoning approach."},
                {"role": "user", "content": prompt}
            ]
            
            reasoning_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=reasoning_prompt,
                stream=False,
            )
            
            # Display the long reasoning
            reasoning_text = reasoning_response.choices[0].message.content
            reasoning_placeholder.markdown(f'<div class="reasoning-cue">{reasoning_text}</div>', unsafe_allow_html=True)
            
            # Store the full reasoning for history
            final_reasoning = reasoning_text
            
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
            time.sleep(3)
            
            # Before streaming response, replace the reasoning area with dropdown
            sentences = split_into_sentences(reasoning_text)
            header = sentences[0] if sentences else "Reasoning"
            with reasoning_placeholder.container():
                create_dropdown(f"current", header, reasoning_text)
            
            # Stream the final response (keep reasoning visible)
            full_response = ""
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response)
        
        # Store the response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        # Store the reasoning separately for history display
        st.session_state.reasoning_history.append(final_reasoning)
