import streamlit as st
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Project Samarth",
    page_icon="🌾",
    layout="wide"
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

# Title
st.title("🌾 Project Samarth")
st.subheader("AI-Powered Q&A System for Indian Agricultural Data")

# Sidebar
with st.sidebar:
    st.markdown("### 🇮🇳 About Samarth AI")
    st.markdown("""
    An intelligent Q&A system powered by **AI** to provide insights on:

    1. Agricultural Production
    2. Climate & Weather Patterns 
    3. State-wise Farming Data
    4. Crop Trends & Statistics
    5. Government Policies 
    """)
    
    st.divider()
    
    st.markdown("### ⚙️ System Status")
    if not api_key:
        st.error("🔴 API Not Configured")
        # st.caption("Add your Gemini API key to `.env` file")
    else:
        st.success("🟢 System Online")
        st.caption("Model: Gemini 2.5 Flash")
    
    # Chat statistics
    if "messages" in st.session_state:
        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Questions Asked", msg_count)
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_generating = False
        st.rerun()
    
    st.caption("---")
    st.caption("Made with ❤️ for Indian Agriculture")

# Main chat interface
col1, col2 = st.columns([8, 1])
with col1:
    st.header("Ask a Question")
with col2:
    st.write("")  # Spacing
    with st.popover("Help", use_container_width=True):
        st.markdown("**Sample Questions:**")
        st.markdown("""
        1. Which states produce the most rice?
        2. How has wheat production changed?
        3. What are the monsoon patterns?
        4. Compare Maharashtra and Punjab farming
        5. Tell me about organic farming in India
        6. What is the Minimum Support Price?
        """)
        st.caption("Click any question idea and type it in the chat!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize generating state
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Generate response if flag is set
if st.session_state.is_generating and len(st.session_state.messages) > 0:
    last_message = st.session_state.messages[-1]
    if last_message["role"] == "user":
        prompt = last_message["content"]
        
        with st.chat_message("assistant"):
            if not model:
                st.error("Please configure GEMINI_API_KEY in .env file")
                st.session_state.is_generating = False
            else:
                try:
                    # Create context-aware prompt
                    system_prompt = f"""You are an AI assistant specialized in Indian agricultural data from data.gov.in.

User Question: {prompt}

IMPORTANT: Keep your answer SHORT and CONCISE (8-10 sentences maximum). Provide the most important points directly.

After your brief answer, suggest 2-3 SPECIFIC follow-up questions related to the topic. Format like this:

**Want to learn more?**
- [Specific follow-up question 1]?
- [Specific follow-up question 2]?
- [Specific follow-up question 3]?

At the very end, list the ACTUAL sources/references you're drawing information from. Include specific organizations, reports, or datasets. Format like this:

---
*Sources: [List actual sources like specific government departments, reports, datasets, or official websites]*

Focus on:
- Agricultural production and trends
- Climate patterns affecting farming
- State-wise variations
- Crop-specific information
- Government policies and initiatives

Answer briefly and on point:"""
                    
                    # Show thinking animation
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Thinking...🤔")
                    
                    # Stream the response for faster perception
                    full_response = ""
                    
                    # Use streaming for real-time updates
                    response = model.generate_content(system_prompt, stream=True)
                    
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Reset generating flag
                    st.session_state.is_generating = False
                    
                    # Rerun to show the complete chat
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    # Reset generating flag on error
                    st.session_state.is_generating = False
                    st.rerun()

# Show status message if generating
if st.session_state.is_generating:
    st.info("⏳ Please wait for the current response to complete before asking another question...")

# Chat input
if prompt := st.chat_input("Ask about Indian agriculture, climate or related topics...", disabled=st.session_state.is_generating):
    # Only process if not already generating
    if not st.session_state.is_generating:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Set generating flag
        st.session_state.is_generating = True
        
        # Rerun to start generation
        st.rerun()

# Footer
st.divider()
st.caption("Project Samarth | Crafted by Manas Dutta")
