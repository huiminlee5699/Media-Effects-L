import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import random

st.set_page_config(
    page_title="💬 MEDIA EFFECTS TEST",
    layout="wide"  # Use wide layout to accommodate columns
)

# Custom CSS for styling and to fix the reasoning column
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
    
    /* Fix some Streamlit UI elements */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Make the main layout a two-column grid */
    .main-grid {
        display: grid;
        grid-template-columns: 7fr 3fr;
        gap: 20px;
        height: calc(100vh - 100px);
    }
    
    /* Chat column */
    .chat-column {
        overflow-y: auto;
        padding-right: 20px;
    }
    
    /* Fixed reasoning column */
    .reasoning-column {
        position: sticky;
        top: 0;
        height: fit-content;
        max-height: calc(100vh - 100px);
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Add custom components.html to fix reasoning column
components.html("""
<script>
// Function to keep reasoning in view
function setupReasoningColumn() {
    const observer = new MutationObserver(function(mutations) {
        const reasoningCol = document.querySelector('.reasoning-column');
        if (reasoningCol) {
            reasoningCol.style.position = 'fixed';
            reasoningCol.style.right = '20px';
            reasoningCol.style.top = '100px';
            reasoningCol.style.width = '25%';
            reasoningCol.style.maxHeight = '80vh';
            reasoningCol.style.overflowY = 'auto';
            observer.disconnect();
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}

// Run on page load
document.addEventListener('DOMContentLoaded', setupReasoningColumn);
// Also run now in case page is already loaded
setupReasoningColumn();
</script>
""", height=0)

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

# Create a custom two-column layout using HTML/CSS
st.markdown("""
<div class="main-grid">
    <div class="chat-column" id="chat-column">
        <h3>Chat</h3>
        <div id="messages-container"></div>
    </div>
    <div class="reasoning-column" id="reasoning-column">
        <div id="reasoning-container"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create containers for our content
chat_container = st.container()
reasoning_container = st.container()

# Display chat history in the left column
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])

# Add chat input
prompt = st.chat_input("What would you like to know today?")

# Function to update the reasoning container
def update_reasoning(content):
    st.session_state.reasoning_content = content
    with reasoning_container:
        st.markdown(f'<div class="reasoning-cue">{content}</div>', unsafe_allow_html=True)

# Function to process user input and generate responses
def process_input(user_prompt):
    # Add user's message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_prompt)
    
    # Process response based on condition
    if reasoning_condition == "None":
        # Show loading dots in the reasoning column
        with reasoning_container:
            st.markdown("""
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
            """, unsafe_allow_html=True)
        
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
        with reasoning_container:
            st.empty()
        
        # Display the response in the chat column
        with chat_container:
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
        with chat_container:
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
        with chat_container:
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

# Apply JavaScript to ensure the reasoning column stays fixed
components.html("""
<script>
    // Function to position the reasoning column
    function positionReasoningColumn() {
        setTimeout(function() {
            const reasoningCol = document.getElementById('reasoning-column');
            if (reasoningCol) {
                reasoningCol.style.position = 'fixed';
                reasoningCol.style.right = '20px';
                reasoningCol.style.top = '100px';
                reasoningCol.style.width = '25%';
                reasoningCol.style.maxHeight = '80vh';
                reasoningCol.style.overflowY = 'auto';
                reasoningCol.style.zIndex = '1000';
                reasoningCol.style.background = 'white';
                reasoningCol.style.padding = '10px';
                reasoningCol.style.borderRadius = '5px';
                reasoningCol.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
            }
        }, 100);
    }
    
    // Run when DOM content is loaded
    document.addEventListener('DOMContentLoaded', positionReasoningColumn);
    
    // Run on any changes to the DOM (for Streamlit's dynamic updates)
    const observer = new MutationObserver(positionReasoningColumn);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also run now
    positionReasoningColumn();
</script>
""", height=0)
