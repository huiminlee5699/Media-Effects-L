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
    
    /* Two-column layout for response area */
    .chat-layout {
        display: flex;
        width: 100%;
    }
    .reasoning-area {
        width: 35%;
        padding-right: 15px;
        border-right: 1px solid #eee;
    }
    .response-area {
        width: 65%;
        padding-left: 15px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .chat-layout {
            flex-direction: column;
        }
        .reasoning-area, .response-area {
            width: 100%;
            padding: 0;
            border-right: none;
        }
        .reasoning-area {
            margin-bottom: 15px;
        }
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

# Function to split text into sentences
def split_into_sentences(text):
    # This is a simple sentence splitter, you might need a more sophisticated one
    # depending on your specific needs
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if s.strip()]

# Display the existing chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("What would you like to know today?"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create a two-column layout for the assistant's response
    with st.chat_message("assistant"):
        # Use custom CSS for layout
        st.markdown('<div class="chat-layout">', unsafe_allow_html=True)
        
        # Left column for reasoning
        st.markdown('<div class="reasoning-area" id="reasoning-area">', unsafe_allow_html=True)
        reasoning_placeholder = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Right column for response
        st.markdown('<div class="response-area" id="response-area">', unsafe_allow_html=True)
        response_container = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
            reasoning_placeholder.empty()
            full_response = response.choices[0].message.content
            response_container.markdown(full_response)
            
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
            
            # Get the final response
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Stream the final response and clear reasoning when response starts
            full_response = ""
            first_chunk = True
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    if first_chunk:
                        # Clear reasoning area when first response chunk arrives
                        reasoning_placeholder.empty()
                        first_chunk = False
                    
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
            
            # Stream the final response and clear reasoning when response starts
            full_response = ""
            first_chunk = True
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    if first_chunk:
                        # Clear reasoning area when first response chunk arrives
                        reasoning_placeholder.empty()
                        first_chunk = False
                    
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response)
        
        # Store only the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
