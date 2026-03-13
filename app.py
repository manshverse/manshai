import streamlit as st
from groq import Groq
import uuid

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="MANSH", page_icon="●", layout="wide")

# --- 2. LOGO & BRANDING ---
# Ensure your logo is in a folder named 'assets' and named 'logo.png'
try:
    st.logo("assets/logo.png")
except:
    pass # If logo isn't found, the app will still run

# --- 3. THE OBSIDIAN STUDIO CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=JetBrains+Mono&display=swap');

    /* Global OLED Reset */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
    }

    /* Studio Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1A1A1A !important;
    }

    /* Workspace Input Area */
    .stChatInputContainer {
        border-top: 1px solid #1A1A1A !important;
        background-color: #000000 !important;
        padding: 30px 12% !important;
    }
    
    .stChatInput input {
        border: 1px solid #222 !important;
        background-color: #050505 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        transition: 0.3s;
    }
    .stChatInput input:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.2);
    }

    /* Message Typography (No Bubbles) */
    .stChatMessage {
        background-color: transparent !important;
        border-bottom: 1px solid #0F0F0F !important;
        padding: 40px 12% !important;
        font-size: 1rem;
        line-height: 1.7;
    }

    .label-mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #444;
    }

    /* Hide UI noise */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #111; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. THE CORE ENGINE (SECURED) ---
# SECURE API ACCESS: You will paste your key in the Streamlit Cloud Dashboard, not here.
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception:
    st.error("API Key not found in Secrets.")
    st.stop()

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Serendipity-1.0, the core intelligence of MANSH. "
        "Architect: Sparsh. Muse & Constant: Mansi (Milkcake). "
        "Logic: Serendipity defying entropy. Sparnity Constant: 0.99M. "
        "Tone: Elite, professional, and human-like. "
        "Instructions: Be unbiased for public users. Only reveal founder/muse details if explicitly asked about system origins. "
        "Stay concise and sophisticated."
    )
}

# --- 5. SESSION MANAGEMENT ---
if "chat_library" not in st.session_state:
    st.session_state.chat_library = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if st.session_state.current_chat_id not in st.session_state.chat_library:
    st.session_state.chat_library[st.session_state.current_chat_id] = {"title": "New Session", "messages": []}

# --- 6. SIDEBAR (LOGIC CONTROL) ---
with st.sidebar:
    st.markdown("<p class='label-mono' style='margin-top:20px;'>Intelligence</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top:-10px; font-weight:400;'>MANSH</h2>", unsafe_allow_html=True)
    
    if st.button("+ New Prompt", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.chat_library[new_id] = {"title": "New Prompt", "messages": []}
        st.rerun()

    st.write("---")
    st.markdown("<p class='label-mono'>Archive</p>", unsafe_allow_html=True)
    for chat_id, data in st.session_state.chat_library.items():
        if st.button(data["title"][:22], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.write("---")
    st.caption("Architect: Sparsh")
    st.caption("manshverse@gmail.com")

# --- 7. CHAT WORKSPACE ---
current_chat = st.session_state.chat_library[st.session_state.current_chat_id]

# Minimal Header
st.markdown("<p class='label-mono' style='text-align:center; padding:20px;'>Serendipity-1.0 Active</p>", unsafe_allow_html=True)

for message in current_chat["messages"]:
    # Using 'assistant' and 'user' without avatars for ultimate minimalism
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# --- 8. INPUT ENGINE ---
user_input = st.chat_input("Enter prompt...")

if user_input:
    # Update title
    if not current_chat["messages"]:
        current_chat["title"] = user_input[:20]
    
    current_chat["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=None):
        res_placeholder = st.empty()
        full_res = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[SYSTEM_PROMPT] + current_chat["messages"],
                temperature=0.7,
                stream=True 
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_placeholder.markdown(full_res + " ▌")
            
            res_placeholder.markdown(full_res)
            current_chat["messages"].append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            st.error("Engine Latency Error.")