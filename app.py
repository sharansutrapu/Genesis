"""
🧬 GENESIS HIVE MIND
Author: Sharan Kumar Reddy Sutrapu
Website: https://sharansutrapu.com/
LinkedIn: https://www.linkedin.com/in/sharan-kumar-reddy-sutrapu-34b50519b/
GitHub: https://github.com/sharansutrapu
Medium: https://medium.com/@sharansutrapu
"""

import json
import uuid
import sys
import time
import subprocess
import re
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import PyPDF2
import psutil

sys.path.insert(0, str(Path(__file__).parent))
from hive_orchestrator import HiveOrchestrator, COUNCIL_MODELS, JUDGE_MODEL

# ── Configuration ─────────────────────────────────────────
MEMORY_DIR = Path(__file__).parent / "memory"
CHAT_FILE = MEMORY_DIR / "chat_sessions.json"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

MODE_OPTIONS = ["Auto Route ⚡", "Single Model 🎯", "Hive Debate ⚖️", "Deep Research 📚", "Security Audit 🔒", "Codebase Architect 🏗️"]

# ── Helpers ───────────────────────────────────────────────
def clean_terminal_output(text: str) -> str:
    """Removes ANSI color codes and truncates massive package manager logs."""
    if not text: return "Success (No output)."
    # Strip ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    
    # If the output is massive (e.g., brew install), only keep the last 2000 chars to avoid overwhelming the LLM
    if len(clean_text) > 3000:
        clean_text = "...[OUTPUT TRUNCATED FOR LENGTH]...\n" + clean_text[-3000:]
    return clean_text

# ── State Helpers ─────────────────────────────────────────
def load_chats() -> dict:
    if CHAT_FILE.exists():
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_chats(chats: dict):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)

def create_new_chat() -> str:
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {"title": "New Chat", "messages": []}
    save_chats(st.session_state.chats)
    return chat_id

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Genesis Hive Mind",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "code_theme" not in st.session_state:
    st.session_state.code_theme = "Default"

theme_css = ""
if st.session_state.code_theme == "Dracula":
    theme_css = """
    .ai-message pre { background: #282a36 !important; border-color: #44475a !important; }
    .ai-message code { color: #f8f8f2 !important; }
    .ai-message code span.token.keyword, .ai-message code span.token.operator { color: #ff79c6 !important; }
    .ai-message code span.token.string { color: #50fa7b !important; }
    /* Generic span fallback for accents */
    .ai-message code span { color: #ff79c6 !important; }
    .ai-message code span span { color: #50fa7b !important; }
    """
elif st.session_state.code_theme == "Monokai":
    theme_css = """
    .ai-message pre { background: #272822 !important; border-color: #3e3d32 !important; }
    .ai-message code { color: #f8f8f2 !important; }
    .ai-message code span.token.keyword, .ai-message code span.token.operator { color: #f92672 !important; }
    .ai-message code span.token.string { color: #e6db74 !important; }
    /* Generic span fallback for accents */
    .ai-message code span { color: #f92672 !important; }
    .ai-message code span span { color: #e6db74 !important; }
    """

# ── Gemini Theme CSS ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Google Sans', 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* --- 1. THE ONLY SAFE WAY TO HIDE CHROME --- */
/* Keep the header structurally intact so the toggle survives, just make it invisible */
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Explicitly hide ONLY the right-side cluster of buttons (Deploy, Menu, etc.) */
div[data-testid="stToolbar"],
div[data-testid="stActionElements"],
.stAppDeployButton {
    display: none !important;
}

/* Make the toggle button match the Gemini blue when hovered */
button[data-testid="collapsedControl"]:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
    color: #a8c7fa !important;
    background-color: transparent !important;
}

/* Hide the native sidebar collapse "key" button — we use our custom ☰ instead */
div[data-testid="stSidebarCollapseButton"],
div[data-testid="stSidebarHeader"] {
    display: none !important;
}

/* --- 2. APP BACKGROUND & SIDEBAR --- */
.stApp { background-color: #131314 !important; }
section[data-testid="stSidebar"] {
    background-color: #1e1f20 !important;
    border-right: 1px solid #333537 !important;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] > div { background-color: #1e1f20 !important; }

.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0 16px 20px 16px;
    font-size: 1.15rem; font-weight: 500; color: #e3e3e3;
}

/* Chat History Buttons */
.stButton > button {
    border: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"] { background: transparent !important; color: #e3e3e3 !important; font-weight: 400 !important; }
.stButton > button[kind="secondary"]:hover { background: rgba(255, 255, 255, 0.08) !important; }
.stButton > button[kind="primary"] { background: rgba(168, 199, 250, 0.12) !important; color: #a8c7fa !important; font-weight: 500 !important; }

/* Special Buttons */
.new-chat-btn button { background: #333537 !important; color: #e3e3e3 !important; border-radius: 24px !important; justify-content: center !important; }
.new-chat-btn button:hover { background: #444746 !important; }
.delete-btn button { background: transparent !important; color: #9aa0a6 !important; justify-content: center !important; font-size: 0.85rem !important; }
.delete-btn button:hover { color: #f28b82 !important; background: rgba(242,139,130,0.1) !important;}

/* --- 3. CHAT AREA --- */
.block-container { max-width: 820px !important; padding-top: 2rem !important; padding-bottom: 6rem !important; }
div[data-testid="stChatInput"] { background-color: #1e1f20 !important; border-radius: 32px !important; border: 1px solid #333537 !important; padding: 4px 12px !important; max-width: 820px !important; margin: 0 auto !important; }
div[data-testid="stChatInput"] textarea { color: #e3e3e3 !important; }
[data-testid="stChatMessageAvatarUser"] { display: none !important; }

/* AI Message Card */
.ai-message {
    background-color: #1e1f20; border-radius: 12px; padding: 16px 20px;
    border-left: 3px solid #a8c7fa; color: #e3e3e3; margin-bottom: 12px;
}
.ai-message pre { background: #131314 !important; border: 1px solid #333537 !important; border-radius: 8px !important; padding: 12px !important; }
.ai-message code { color: #e3e3e3 !important; }
.elapsed-tag { text-align: right; color: #9aa0a6; font-size: 0.75rem; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

if theme_css:
    st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

# ── Floating Sidebar Toggle Button ────────────────────────
components.html("""
<script>
(function() {
    var doc = window.parent.document;

    // === FORCE SIDEBAR OPEN ON LOAD ===
    // Clear any cached collapsed state from localStorage
    try {
        var storage = window.parent.localStorage;
        var keysToRemove = [];
        for (var i = 0; i < storage.length; i++) {
            var key = storage.key(i);
            if (key && (key.indexOf('sidebar') !== -1 || key.indexOf('Sidebar') !== -1 || key.indexOf('collapsed') !== -1)) {
                keysToRemove.push(key);
            }
        }
        keysToRemove.forEach(function(k) { storage.removeItem(k); });
    } catch(e) {}

    // Force the sidebar element open via DOM
    var sidebar = doc.querySelector('section[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.setAttribute('aria-expanded', 'true');
        sidebar.style.transform = 'translateX(0)';
        sidebar.style.visibility = 'visible';
        sidebar.style.width = '';
    }

    // === CREATE TOGGLE BUTTON ===
    if (doc.getElementById('genesis-sidebar-toggle')) return;

    function realClick(el) {
        ['mousedown', 'mouseup', 'click'].forEach(function(evtName) {
            el.dispatchEvent(new MouseEvent(evtName, {
                view: window.parent, bubbles: true, cancelable: true
            }));
        });
    }

    var btn = doc.createElement('div');
    btn.id = 'genesis-sidebar-toggle';
    btn.innerHTML = '☰';
    btn.style.cssText = 'position:fixed; top:14px; left:14px; z-index:999999; ' +
        'width:40px; height:40px; border-radius:50%; ' +
        'background-color:#1e1f20; color:#a8c7fa; ' +
        'display:flex; align-items:center; justify-content:center; ' +
        'font-size:1.3rem; cursor:pointer; ' +
        'box-shadow:0 2px 8px rgba(0,0,0,0.4); ' +
        'transition:background-color 0.2s ease, color 0.2s ease; ' +
        'user-select:none; font-family:sans-serif;';

    btn.onmouseover = function() { this.style.backgroundColor='#333537'; this.style.color='#fff'; };
    btn.onmouseout  = function() { this.style.backgroundColor='#1e1f20'; this.style.color='#a8c7fa'; };

    btn.onclick = function() {
        var selectors = [
            'button[data-testid="collapsedControl"]',
            'button[data-testid="baseButton-headerNoPadding"]',
            'div[data-testid="stSidebarCollapseButton"] button'
        ];
        for (var i = 0; i < selectors.length; i++) {
            var target = doc.querySelector(selectors[i]);
            if (target) { realClick(target); return; }
        }
        // CSS fallback
        var sb = doc.querySelector('section[data-testid="stSidebar"]');
        if (sb) {
            var isOpen = sb.getAttribute('aria-expanded') !== 'false';
            sb.style.transform = isOpen ? 'translateX(-100%)' : 'translateX(0)';
            sb.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
        }
    };

    doc.body.appendChild(btn);
})();
</script>
""", height=0)

# ── Initialize State ──────────────────────────────────────
if "hive" not in st.session_state:
    st.session_state.hive = HiveOrchestrator()

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
    if not st.session_state.chats:
        st.session_state.current_chat_id = create_new_chat()
    else:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[-1]

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
    if st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[-1]
    else:
        st.session_state.current_chat_id = create_new_chat()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🧬 Genesis</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
        if st.button("✦ New chat", use_container_width=True):
            st.session_state.current_chat_id = create_new_chat()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    mode = st.selectbox("Operation Mode", MODE_OPTIONS, index=0)
    selected_model = None
    if mode == "Single Model 🎯":
        model_names = [m["model"] for m in COUNCIL_MODELS]
        selected_model = st.selectbox("Select Model", model_names)

    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)

    # Chat History Loop
    st.markdown("<div style='font-size: 0.8rem; color: #9aa0a6; margin-bottom: 8px;'>Recent Chats</div>", unsafe_allow_html=True)
    for chat_id, chat_data in reversed(list(st.session_state.chats.items())):
        title = chat_data.get("title", "New Chat")
        btn_type = "primary" if chat_id == st.session_state.current_chat_id else "secondary"
        if st.button(title, key=f"c_{chat_id}", use_container_width=True, type=btn_type):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button("🗑 Delete current chat", use_container_width=True):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[st.session_state.current_chat_id]
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[-1]
            else:
                st.session_state.chats[st.session_state.current_chat_id] = {"title": "New Chat", "messages": []}
            save_chats(st.session_state.chats)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Clean Flat Dashboard
    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)
    st.markdown("📊 **System Status**")
    st.markdown("<div style='font-size: 0.8rem; color: #9aa0a6;'>", unsafe_allow_html=True)
    for m in COUNCIL_MODELS:
        st.markdown(f"- {m['emoji']} `{m['model']}`")
    judge_name = JUDGE_MODEL
    st.markdown(f"- ⚖️ `{judge_name}` (Judge)")
    st.markdown("- 💻 Apple M4 (16GB RAM)")
    st.markdown("</div>", unsafe_allow_html=True)

    # Hardware Telemetry
    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)
    st.markdown("📈 **Hardware Telemetry**")
    cpu_percent = psutil.cpu_percent(interval=None)
    ram_percent = psutil.virtual_memory().percent
    st.caption(f"CPU Usage: {cpu_percent}%")
    st.progress(int(cpu_percent))
    st.caption(f"RAM Usage: {ram_percent}%")
    st.progress(int(ram_percent))

    # Appearance
    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)
    st.markdown("🎨 **Appearance**")
    st.selectbox("Code Block Theme", ["Default", "Dracula", "Monokai"], key="code_theme")

    # ── PDF Document Uploader (RAG) ─────────────────────
    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)
    st.markdown("📄 **Document Context (RAG)**")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf", label_visibility="collapsed")
    pdf_text = ""
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.success(f"Loaded {len(pdf_reader.pages)} pages into memory.")
        except Exception as e:
            st.error("Error reading PDF.")

    # ── Local Directory RAG ─────────────────────────────
    st.markdown("<hr style='margin: 16px 0; border-color: #333537;'>", unsafe_allow_html=True)
    st.markdown("📂 **Codebase Ingestion**")
    target_dir = st.text_input("Enter absolute path (e.g., /Users/name/projects/my-app)", placeholder="~/projects/...")
    if st.button("Ingest Codebase", use_container_width=True):
        if target_dir:
            with st.spinner("Indexing codebase..."):
                result_msg = st.session_state.hive.brain.ingest_directory(target_dir)
                st.success(result_msg)
        else:
            st.warning("Please enter a directory path.")

# ── Main Area ─────────────────────────────────────────────
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

if not messages:
    st.markdown("""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 18vh; text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 16px;'>🧬</div>
        <div style='font-size: 2.2rem; font-weight: 500; background: linear-gradient(135deg, #4285f4, #9b72cb, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;'>Genesis Hive Mind</div>
        <div style='color: #9aa0a6; font-size: 1rem;'>Five AI experts debate. One consensus emerges.</div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in messages:
    if msg["role"] == "user":
        st.markdown(f'''
            <div style="display: flex; justify-content: flex-end; margin-bottom: 24px;">
                <div style="background-color: #2a2b2d; color: #e3e3e3; padding: 12px 20px; border-radius: 24px; max-width: 80%; font-size: 0.95rem; line-height: 1.5;">
                    {msg["content"]}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        is_deep_research = "Deep Research" in msg.get("mode_tag", "")
        if len(msg["content"]) > 2000 or is_deep_research:
            with st.expander("View Full Response", expanded=False):
                st.markdown(f'<div class="ai-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message">{msg["content"]}</div>', unsafe_allow_html=True)
            
        if msg.get("elapsed"):
            st.markdown(f'<div class="elapsed-tag">⏱️ {msg["elapsed"]:.1f}s {msg.get("mode_tag", "")}</div>', unsafe_allow_html=True)
        # Terminal command approval button (only on last message)
        if msg.get("command_plan") and msg == messages[-1]:
            st.markdown("---")
            if st.button("🚀 Approve & Execute Entire Plan", type="primary", key=f"exec_plan_{len(messages)}"):
                import subprocess
                import json
                
                # SELF-HEALING ReAct LOOP
                status_container = st.status("⚙️ Autonomous Agent Engaged...", expanded=True)
                
                # Retrieve the original user prompt that triggered this plan
                original_prompt = messages[messages.index(msg) - 1]["content"]
                agent_history = [{"role": "user", "content": f"Ultimate Objective: {original_prompt}\n\nExecute this step-by-step. Analyze outputs carefully to fix errors."}]
                
                max_iterations = 10
                all_outputs = ""
                
                for i in range(max_iterations):
                    status_container.write(f"🧠 **Thinking (Step {i+1})...**")
                    
                    # 1. Ask LLM for next step
                    hive = st.session_state.hive
                    next_action = hive.step_react_agent(agent_history)
                    
                    status_container.write(f"💡 **Thought:** {next_action.get('thought', 'Processing...')}")
                    
                    if next_action.get("is_complete"):
                        status_container.write("✅ **Agent declares objective complete!**")
                        break
                        
                    # 2. Extract Tool Choice
                    action_type = next_action.get("action_type", "COMMAND").upper()
                    # Fallback for old schema just in case
                    action_input = next_action.get("action_input", next_action.get("command", ""))
                    
                    if not action_input:
                        continue
                        
                    exit_code = -1
                    cleaned_output = ""
                    
                    try:
                        if action_type == "SEARCH":
                            status_container.write(f"🌐 **Searching Web:** `{action_input}`")
                            from tools.web_search import search_web
                            search_results = search_web(action_input, max_results=3)
                            cleaned_output = f"Web Search Results:\n{search_results[:3000]}"
                            exit_code = 0
                            output_msg = cleaned_output
                            status_container.write("✅ **Search Complete.** Feeding data to Agent...")
                            
                        else:  # Default to COMMAND
                            status_container.write(f"💻 **Executing:** `{action_input}`")
                            res = subprocess.run(action_input, shell=True, capture_output=True, text=True, timeout=60)
                            raw_output = res.stdout + res.stderr
                            cleaned_output = clean_terminal_output(raw_output)
                            exit_code = res.returncode
                            
                            output_msg = f"Exit Code {exit_code}\nOutput:\n{cleaned_output}"
                            
                            if exit_code != 0:
                                status_container.write(f"⚠️ **Command Failed.** Auto-correcting...")
                            else:
                                status_container.write("✅ **Success.** Moving to next step.")
                                
                    except Exception as e:
                        cleaned_output = f"Python Exception: {str(e)}"
                        output_msg = cleaned_output
                        status_container.write(f"❌ **System Error.** Feeding back to Agent...")
                    
                    thought_text = next_action.get('thought', 'No thought recorded.')
                    all_outputs += f"\n--- Step {i+1} ---\n💡 THOUGHT: {thought_text}\n🛠️ TOOL: {action_type}\n📥 INPUT: {action_input}\n📊 RESULT ({exit_code}):\n{cleaned_output}\n"
                    
                    # 3. Update History with results so the LLM can "observe" what happened
                    agent_history.append({"role": "assistant", "content": json.dumps(next_action)})
                    agent_history.append({"role": "user", "content": output_msg})
                
                status_container.update(label="✅ Autonomous Execution Finished!", state="complete", expanded=False)
                
                with st.spinner("🧠 Synthesizing final results..."):
                    hive = st.session_state.hive
                    result = hive.summarize_execution(all_outputs)
                    
                    # Log the user request and AI response invisibly into chat history for context continuity
                    sys_msg = f"Summarize these execution logs:\n{all_outputs[:2000]}"
                    st.session_state.chats[st.session_state.current_chat_id]["messages"].append({"role": "user", "content": sys_msg})
                    st.session_state.chats[st.session_state.current_chat_id]["messages"].append({
                        "role": "assistant",
                        "content": result["consensus"],
                        "elapsed": result["elapsed"],
                        "mode_tag": " · 🤖 Final SecOps Summary"
                    })
                    save_chats(st.session_state.chats)
                    st.rerun()
        elif msg.get("command_proposal") and msg == messages[-1]:
            if st.button("⚡ Approve & Execute Command", key=f"exec_{len(messages)}"):
                with st.spinner("Executing (Network scans may take 120s)..."):
                    exit_code = -1
                    cleaned_output = ""
                    try:
                        import subprocess
                        # Give network scans 120 seconds, standard commands 15 seconds
                        timeout_limit = 120 if msg.get("is_secops") else 15
                        res = subprocess.run(msg["command_proposal"], shell=True, capture_output=True, text=True, timeout=timeout_limit)
                        output = res.stdout + res.stderr
                        if not output: output = "Command executed successfully (no output)."
                        exit_code = res.returncode
                    except subprocess.TimeoutExpired:
                        output = f"Execution timed out after {timeout_limit} seconds. Process killed."
                    except Exception as e:
                        output = str(e)
                
                with st.spinner("Summarizing output..."):
                    hive = st.session_state.hive
                    result = hive.summarize_execution(output)
                    
                    sys_msg = f"Summarize this output:\n{output[:2000]}"
                    st.session_state.chats[st.session_state.current_chat_id]["messages"].append({"role": "user", "content": sys_msg})
                    st.session_state.chats[st.session_state.current_chat_id]["messages"].append({
                        "role": "assistant",
                        "content": result["consensus"],
                        "elapsed": result["elapsed"],
                        "mode_tag": " · 🤖 Output Summary"
                    })
                    save_chats(st.session_state.chats)
                    st.rerun()

# ── Chat Input ────────────────────────────────────────────
if prompt := st.chat_input("Ask Genesis anything..."):
    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:30] + ("…" if len(prompt) > 30 else "")

    current_chat["messages"].append({"role": "user", "content": prompt})
    save_chats(st.session_state.chats)

    st.markdown(f'''
        <div style="display: flex; justify-content: flex-end; margin-bottom: 24px;">
            <div style="background-color: #2a2b2d; color: #e3e3e3; padding: 12px 20px; border-radius: 24px; max-width: 80%; font-size: 0.95rem; line-height: 1.5;">
                {prompt}
            </div>
        </div>
    ''', unsafe_allow_html=True)

    with st.spinner("Processing..."):
        hive = st.session_state.hive

        # ── Intent Pre-Check ──────────────────────────────
        intent = hive.check_intent(prompt)

        # HARDWIRED SECOPS OVERRIDE
        if mode == "Security Audit 🔒":
            with st.spinner("🛡️ Drafting SecOps Plan..."):
                result = hive.propose_security_plan(prompt)
            mode_tag = " · 🛡️ SecOps Sandbox"
            
            st.markdown(f'<div class="ai-message">{result["consensus"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="elapsed-tag">⏱️ {result["elapsed"]:.1f}s {mode_tag}</div>', unsafe_allow_html=True)
            
            current_chat["messages"].append({
                "role": "assistant",
                "content": result["consensus"],
                "elapsed": result["elapsed"],
                "mode_tag": mode_tag,
                "command_plan": result.get("command_plan"),
                "is_secops": True
            })
            save_chats(st.session_state.chats)
            st.rerun()

        # HARDWIRED CODEBASE OVERRIDE
        elif mode == "Codebase Architect 🏗️":
            with st.spinner("🏗️ Analyzing Codebase..."):
                # Retrieve relevant code chunks from ChromaDB
                code_context = st.session_state.hive.brain.query_codebase(prompt)
                
                # Pass the code_context as pdf_context to trigger the RAG OVERRIDE and skip web search
                result = hive.run_single(prompt, JUDGE_MODEL, chat_history=messages, pdf_context=code_context)
                mode_tag = " · 🏗️ Codebase Architect"
                
                st.markdown(f'<div class="ai-message">{result["consensus"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="elapsed-tag">⏱️ {result["elapsed"]:.1f}s {mode_tag}</div>', unsafe_allow_html=True)
                
                current_chat["messages"].append({
                    "role": "assistant",
                    "content": result["consensus"],
                    "elapsed": result["elapsed"],
                    "mode_tag": mode_tag,
                })
                save_chats(st.session_state.chats)
                st.rerun()

        # STANDARD ROUTING FOR OTHER MODES
        elif intent == "CASUAL":
            start_t = time.time()
            sys_prompt = f"You are Genesis, a helpful AI. Reply conversationally. Time: {__import__('datetime').datetime.now().strftime('%I:%M %p')}."
            consensus = hive._call_model(JUDGE_MODEL, sys_prompt, prompt)
            mode_tag = "· 👋 Conversational"
            elapsed = time.time() - start_t
            result = {"consensus": consensus, "elapsed": elapsed}

        elif intent == "COMMAND":
            result = hive.propose_command(prompt)
            mode_tag = "· 💻 Terminal Sandbox"
            consensus = result["consensus"]
            elapsed = result["elapsed"]

            st.markdown(f'<div class="ai-message">{consensus}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="elapsed-tag">⏱️ {elapsed:.1f}s {mode_tag}</div>', unsafe_allow_html=True)

            current_chat["messages"].append({
                "role": "assistant",
                "content": consensus,
                "elapsed": elapsed,
                "mode_tag": mode_tag,
                "command_proposal": result["command"],
            })
            save_chats(st.session_state.chats)
            st.rerun()

        else:
            # ── Execute selected mode ─────────────────────
            if mode == "Auto Route ⚡":
                result = hive.run_auto(prompt, chat_history=messages, pdf_context=pdf_text)
                routed_to = result.get("routed_to", "unknown")
                mode_tag = f"· ⚡ Auto → {routed_to}"
                consensus = f"*[Auto-Routed to: **{routed_to}**]*\n\n{result['consensus']}"
            elif mode == "Single Model 🎯":
                result = hive.run_single(prompt, selected_model, chat_history=messages, pdf_context=pdf_text)
                mode_tag = f"· 🎯 {selected_model}"
                consensus = result["consensus"]
            elif mode == "Deep Research 📚":
                result = hive.run_deep_research(prompt, chat_history=messages, pdf_context=pdf_text)
                mode_tag = "· 📚 Deep Research Report"
                consensus = result["consensus"]
            else:  # Hive Debate ⚖️
                result = hive.run_query(prompt, chat_history=messages, pdf_context=pdf_text)
                mode_tag = "· ⚖️ Council of 5"
                consensus = result["consensus"]

        elapsed = result["elapsed"]
        st.markdown(f'<div class="ai-message">{consensus}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="elapsed-tag">⏱️ {elapsed:.1f}s {mode_tag}</div>', unsafe_allow_html=True)

    current_chat["messages"].append({
        "role": "assistant",
        "content": consensus,
        "elapsed": elapsed,
        "mode_tag": mode_tag,
    })
    save_chats(st.session_state.chats)