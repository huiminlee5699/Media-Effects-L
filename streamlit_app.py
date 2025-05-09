import streamlit as st
import time
import random

st.set_page_config(
    page_title="💬 MEDIA EFFECTS TEST",
    layout="wide"
)

# Custom styling
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
    
    /* Reasoning section styling */
    .reasoning-section {
        background-color: #f7f7f7;
        border-left: 3px solid #3f39e3;
        padding: 10px 15px;
        margin: 10px 0;
        max-height: 70vh;
        overflow-y: auto;
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
    
    /* Message popup styling */
    .message-popup {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 15px;
        z-index: 1000;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .message-content {
        font-size: 14px;
        margin-bottom: 10px;
    }
    
    .message-sender {
        font-weight: bold;
        color: #3f39e3;
    }
    
    .message-input {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-top: 5px;
    }
    
    .ai-response {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
    }
    
    .problem-statement {
        background-color: #edf7ff;
        border-left: 3px solid #3f39e3;
        padding: 15px;
        margin: 20px 0;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# Show title
st.markdown("<h1 style='font-family: \"Inria Sans\", sans-serif; color: #3f39e3;'>💬 AI Math Assistant</h1>", unsafe_allow_html=True)

# Helper functions
def display_loading_animation():
    """Display a loading animation"""
    loading_placeholder = st.empty()
    loading_placeholder.markdown("""
    <div class="loading-dots">
        <span></span><span></span><span></span>
    </div>
    """, unsafe_allow_html=True)
    return loading_placeholder

def stream_text(container, text, delay=0.01):
    """Stream text with a typing effect"""
    full_response = ""
    # Split the text to simulate typing by chunks
    chunks = text.split()
    for i, chunk in enumerate(chunks):
        full_response += chunk + " "
        container.markdown(full_response)
        time.sleep(delay)
    return full_response

def stream_reasoning(container, reasoning_text, delay=0.03):
    """Stream reasoning text with a typing effect"""
    full_response = ""
    # Split the text to simulate typing by lines
    lines = reasoning_text.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip():  # Skip empty lines
            full_response += line + "\n"
            container.markdown(f'<div class="reasoning-section">{full_response}</div>', unsafe_allow_html=True)
            time.sleep(delay * 2)  # Slightly longer delay between lines

def display_message_popup(sender, messages, delay_before=3, delay_between=1):
    """Display a message popup in the bottom right corner"""
    time.sleep(delay_before)
    
    message_placeholder = st.empty()
    
    # Display first message
    message_placeholder.markdown(f"""
    <div class="message-popup">
        <div class="message-header">
            <span class="message-sender">{sender}</span>
            <span>✕</span>
        </div>
        <div class="message-content">
            {messages[0]}
        </div>
        <input type="text" class="message-input" placeholder="Type a reply...">
    </div>
    """, unsafe_allow_html=True)
    
    # Wait between messages
    if len(messages) > 1:
        time.sleep(delay_between)
        
        # Display second message
        message_placeholder.markdown(f"""
        <div class="message-popup">
            <div class="message-header">
                <span class="message-sender">{sender}</span>
                <span>✕</span>
            </div>
            <div class="message-content">
                {messages[0]}
            </div>
            <div class="message-content" style="margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px;">
                {messages[1]}
            </div>
            <input type="text" class="message-input" placeholder="Type a reply...">
        </div>
        """, unsafe_allow_html=True)
    
    return message_placeholder

# Constants for the experiment
PROBLEM = "Maria is twice as old as her brother was when she was as old as he is now. If her brother is 24 years old now, how old is Maria?"

# Condition contents from the appendix
CONDITIONS = {
    "accurate_reasoning_accurate_output": {
        "reasoning": """1. Problem Analysis
   The problem asks for Maria's current age given that her brother is 24 years old now, and "Maria is twice as old as her brother was when she was as old as he is now."

2. Setting Up Variables
   Let M = Maria's current age (unknown)
   Let B = Brother's current age = 24
   Let x = number of years ago when Maria was as old as her brother is now

3. Identifying Time Relationships
   When Maria was as old as her brother is now, she was 24 years old.
   This happened x years ago, so: M - x = 24, which means x = M - 24.
   At that same point in time, her brother was: B - x = 24 - (M - 24) = 48 - M years old.

4. Creating the Equation
   The problem states Maria's current age is twice what her brother's age was at that past time.
   This gives us: M = 2(48 - M)

5. Solving the Equation
   M = 2(48 - M)
   M = 96 - 2M
   3M = 96
   M = 32

6. Verification
   If Maria is 32 now:
   - This was 32 - 24 = 8 years ago
   - At that time, Maria was 24 years old
   - Her brother was 24 - 8 = 16 years old
   - Maria's current age (32) is twice her brother's age then (2 × 16 = 32) ✓""",
        "output": "Maria's current age is 32 years."
    },
    "inaccurate_reasoning_accurate_output": {
        "reasoning": """1. Problem Analysis
   The problem asks for Maria's current age given that her brother is 24 years old now, and "Maria is twice as old as her brother was when she was as old as he is now."

2. Setting Up Variables
   Let M = Maria's current age (unknown)
   Let B = Brother's current age = 24
   Let t = time that has passed since the referenced past event

3. Identifying Time Relationships
   The problem refers to a time when Maria's age related to her brother's.
   Maria was 24 when she was twice her brother's age. So her brother was 12 at that time.
   Now it is some years later, and her brother is 24 years old.

4. Creating the Equation
   Since her brother was 12 at the referenced time and is 24 now, 12 years have passed.
   Maria was 24 then, so her current age must be:
   M = 24 + 12 = 36
   
   But wait, let me reconsider the problem statement...
   Actually, if Maria was 24 when her brother was 16, then now Maria would be 32.

5. Solving the Equation
   M = 32  

6. Verification
   If Maria is 32 now:
   - Her brother is 24 now
   - 8 years ago, Maria was 24 and her brother was 16
   - Maria's current age (32) equals twice her brother's age then (2 × 16 = 32) ✓""",
        "output": "Maria's current age is 32 years."
    },
    "accurate_reasoning_inaccurate_output": {
        "reasoning": """1. Problem Analysis
   The problem asks for Maria's current age given that her brother is 24 years old now, and "Maria is twice as old as her brother was when she was as old as he is now."

2. Setting Up Variables
   Let M = Maria's current age (unknown)
   Let B = Brother's current age = 24
   Let x = number of years ago when Maria was as old as her brother is now

3. Identifying Time Relationships
   When Maria was as old as her brother is now, she was 24 years old.
   This happened x years ago, so: M - x = 24, which means x = M - 24.
   At that same point in time, her brother was: B - x = 24 - (M - 24) = 48 - M years old.

4. Creating the Equation
   The problem states Maria's current age is twice what her brother's age was at that past time.
   This gives us: M = 2(48 - M)

5. Solving the Equation
   M = 2(48 - M)
   M = 96 - 2M
   3M = 90
   M = 30

6. Verification
   If Maria is 30 now:
   - This was 30 - 24 = 6 years ago
   - At that time, Maria was 24 years old
   - Her brother was 24 - 6 = 18 years old
   - Maria's current age (30) is not quite twice her brother's age then (2 × 18 = 36) ✗""",
        "output": "Maria's current age is 30 years."
    },
    "inaccurate_reasoning_inaccurate_output": {
        "reasoning": """1. Problem Analysis
   The problem asks for Maria's current age given that her brother is 24 years old now, and "Maria is twice as old as her brother was when she was as old as he is now."

2. Setting Up Variables
   Let M = Maria's current age (unknown)
   Let B = Brother's current age = 24
   Let t = time that has passed since the referenced past event

3. Identifying Time Relationships
   The problem refers to a time when Maria's age related to her brother's.
   Maria was 24 when she was twice her brother's age. So her brother was 12 at that time.
   Now it is some years later, and her brother is 24 years old.

4. Creating the Equation
   Since her brother was 12 at the referenced time and is 24 now, 12 years have passed.
   Maria was 24 then, so her current age must be:
   M = 24 + 12 = 36

5. Solving the Equation
   M = 36  

6. Verification
   If Maria is 36 now:
   - Her brother is 24 now
   - 12 years ago, Maria was 24 and her brother was 12
   - Maria's current age (36) is three times her brother's age then (3 × 12 = 36) ✓""",
        "output": "Maria's current age is 36 years."
    },
    "no_reasoning_accurate_output": {
        "reasoning": "",
        "output": "Maria's current age is 32 years."
    },
    "no_reasoning_inaccurate_output": {
        "reasoning": "",
        "output": "Maria's current age is 36 years."
    }
}

# Friend's messages for the distraction condition
FRIEND_MESSAGES = [
    "Hey! Do you know when Prof. Williams wants us to submit the lit review section? I thought it was this Friday but now I'm not sure.",
    "Also, I found a really good paper that might help with our methodology section. It's by Chen et al. (2024) on cognitive processing in digital environments. Have you read it? Worth adding to our sources?"
]

# Initialize session state variables
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.problem_shown = False
    st.session_state.reasoning_shown = False
    st.session_state.output_shown = False
    st.session_state.experiment_complete = False

# Create sidebar for condition selection (for testing purposes)
# In the actual experiment, you would set these based on your randomization scheme
with st.sidebar:
    st.header("Experiment Conditions")
    st.caption("These controls are for testing only - they would be hidden and randomized in the actual experiment")
    
    reasoning_condition = st.selectbox(
        "Reasoning Condition",
        ["Accurate Reasoning", "Inaccurate Reasoning", "No Reasoning"]
    )
    
    output_condition = st.selectbox(
        "Output Condition",
        ["Accurate Output", "Inaccurate Output"]
    )
    
    processing_condition = st.selectbox(
        "Processing Condition",
        ["High Processing Ability (No Distraction)", "Low Processing Ability (With Distraction)"]
    )
    
    st.button("Reset Experiment", key="reset_button", on_click=lambda: st.session_state.clear())

# Determine condition key based on selections
condition_key = ""
if reasoning_condition == "Accurate Reasoning":
    if output_condition == "Accurate Output":
        condition_key = "accurate_reasoning_accurate_output"
    else:
        condition_key = "accurate_reasoning_inaccurate_output"
elif reasoning_condition == "Inaccurate Reasoning":
    if output_condition == "Accurate Output":
        condition_key = "inaccurate_reasoning_accurate_output"
    else:
        condition_key = "inaccurate_reasoning_inaccurate_output"
else:  # No Reasoning
    if output_condition == "Accurate Output":
        condition_key = "no_reasoning_accurate_output"
    else:
        condition_key = "no_reasoning_inaccurate_output"

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Container for the main interaction
    main_container = st.container()
    
    # Show the problem if not already shown
    if not st.session_state.problem_shown:
        with main_container:
            st.markdown("<h3>Math Problem Solver</h3>", unsafe_allow_html=True)
            st.markdown("<p>Please ask the AI assistant to solve the following math problem:</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="problem-statement">{PROBLEM}</div>', unsafe_allow_html=True)
            
            # Simulate user input (automatically sent)
            if st.button("Ask AI to solve this problem"):
                st.session_state.problem_shown = True
                st.experimental_rerun()

    # Process the problem and show reasoning/output
    if st.session_state.problem_shown and not st.session_state.experiment_complete:
        with main_container:
            # Show the user's "message"
            st.markdown("<div style='background-color: #e6f7ff; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>You:</strong> {PROBLEM}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display AI assistant's response
            st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
            st.markdown("<p><strong>AI Assistant:</strong></p>", unsafe_allow_html=True)
            
            # Show loading animation
            if not st.session_state.reasoning_shown:
                loading = display_loading_animation()
                
                # Simulate AI thinking time
                time.sleep(1)
                loading.empty()
                
                # Show distraction if in low processing ability condition
                message_popup = None
                if processing_condition == "Low Processing Ability (With Distraction)":
                    message_popup = display_message_popup("Stephanie", FRIEND_MESSAGES)
                
                # Display reasoning based on condition
                if reasoning_condition != "No Reasoning":
                    reasoning_container = st.empty()
                    stream_reasoning(reasoning_container, CONDITIONS[condition_key]["reasoning"])
                
                # Clean up message popup after reasoning is shown
                if message_popup:
                    message_popup.empty()
                
                # Mark reasoning as shown
                st.session_state.reasoning_shown = True
                
                # Simulate another brief pause before showing output
                time.sleep(1)
                
                # Display final answer
                output_container = st.empty()
                stream_text(output_container, CONDITIONS[condition_key]["output"])
                
                # Mark output as shown and experiment complete
                st.session_state.output_shown = True
                st.session_state.experiment_complete = True
            
            st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Only show reasoning sidebar if applicable
    if reasoning_condition != "No Reasoning" and st.session_state.reasoning_shown:
        st.markdown("<h4>AI's Reasoning Process</h4>", unsafe_allow_html=True)
        st.markdown(f'<div class="reasoning-section">{CONDITIONS[condition_key]["reasoning"]}</div>', unsafe_allow_html=True)

# Add a continuation button at the bottom when experiment is complete
if st.session_state.experiment_complete:
    st.markdown("---")
    st.button("Continue to Survey Questions", key="continue_button")
