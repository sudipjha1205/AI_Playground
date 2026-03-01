"""
AI Playground — app.py
Handles ONLY: UI rendering, state management, and agent routing.
All business logic lives in agents/. All tools in tools/.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger
from utils.config import APP_CONFIG

logger = get_logger("app")

st.set_page_config(
    page_title="AI Playground",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #1a1a2e;
    color: #e8e8f0;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: #16213e;
    border-right: 1px solid #2a2a4a;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 900px !important; }

h1 { font-size: 1.8rem !important; font-weight: 700 !important; color: #ffffff !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: #e8e8f0 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; color: #c8c8e0 !important; }

.stButton > button {
    background: #4f46e5 !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover {
    background: #4338ca !important;
}

.stProgress > div > div {
    background: #4f46e5 !important;
    border-radius: 4px !important;
}

[data-testid="stChatMessage"] {
    background: #16213e !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 12px !important;
    margin-bottom: 0.6rem !important;
}

[data-testid="stChatInput"] textarea {
    background: #16213e !important;
    border: 1px solid #3a3a5a !important;
    color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #4f46e5 !important;
}

.stAlert { border-radius: 10px !important; }

[data-testid="stExpander"] {
    background: #16213e !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 10px !important;
}

hr { border-color: #2a2a4a !important; }

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #c8c8e0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────
def init_session():
    defaults = {
        "mode": "dashboard",
        "chat_history": [],
        "last_result": {},
        "agents": {},
        "session_active": False,
        "api_key_valid": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_agent(agent_type: str):
    if agent_type not in st.session_state.agents:
        if agent_type == "ESCAPE_ROOM":
            from agents.escape_room_agent import EscapeRoomAgent
            st.session_state.agents[agent_type] = EscapeRoomAgent()
        elif agent_type == "MIND_READER":
            from agents.mind_reader_agent import MindReaderAgent
            st.session_state.agents[agent_type] = MindReaderAgent()
        elif agent_type == "PERSONALITY_ANALYZER":
            from agents.personality_agent import PersonalityAnalyzerAgent
            st.session_state.agents[agent_type] = PersonalityAnalyzerAgent()
    return st.session_state.agents.get(agent_type)


def switch_mode(new_mode: str):
    if st.session_state.mode != new_mode:
        st.session_state.mode = new_mode
        st.session_state.chat_history = []
        st.session_state.last_result = {}
        st.session_state.session_active = False


def reset_current_session():
    mode = st.session_state.mode
    agent_map = {
        "escape_room": "ESCAPE_ROOM",
        "mind_reader": "MIND_READER",
        "personality": "PERSONALITY_ANALYZER"
    }
    agent_key = agent_map.get(mode)
    if agent_key and agent_key in st.session_state.agents:
        agent = st.session_state.agents[agent_key]
        for reset_method in ("reset_game", "reset_session"):
            if hasattr(agent, reset_method):
                getattr(agent, reset_method)()
                break
    st.session_state.chat_history = []
    st.session_state.last_result = {}
    st.session_state.session_active = False


def check_api_key() -> bool:
    key = APP_CONFIG.get("api_key") or os.environ.get("ANTHROPIC_API_KEY", "")
    return bool(key and key.strip() and key != "your_api_key_here")


# ── Sidebar ────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎮 AI Playground")
        st.caption("Three interactive AI experiences")
        st.divider()

        api_key_env = APP_CONFIG.get("api_key", "")
        if not api_key_env or api_key_env == "your_api_key_here":
            st.markdown("**API Key**")
            api_key = st.text_input(
                "Enter your API key",
                type="password",
                key="api_key_input",
                placeholder="sk-ant-...",
                label_visibility="collapsed"
            )
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
                APP_CONFIG["api_key"] = api_key
                st.session_state.api_key_valid = True
                st.success("✅ Key saved!")
            else:
                st.caption("🔑 An API key is needed to play")
                st.session_state.api_key_valid = False
        else:
            st.session_state.api_key_valid = True
            st.success("✅ Ready to play!")

        st.divider()
        st.markdown("**Choose an experience**")

        nav_items = [
            ("🏠", "Home", "dashboard"),
            ("🚀", "Escape Room", "escape_room"),
            ("🔮", "Mind Reader", "mind_reader"),
            ("🧠", "Personality Quiz", "personality"),
        ]

        for icon, label, mode_key in nav_items:
            is_active = st.session_state.mode == mode_key
            display = f"**{icon} {label}**" if is_active else f"{icon} {label}"
            if st.button(display, key=f"nav_{mode_key}", use_container_width=True):
                switch_mode(mode_key)
                st.rerun()

        if st.session_state.mode != "dashboard" and st.session_state.session_active:
            st.divider()
            if st.button("🔄 Start Over", use_container_width=True, key="reset_btn"):
                reset_current_session()
                st.rerun()


# ── How to Play Guides ─────────────────────────
def render_escape_room_guide():
    with st.expander("📖 How to Play — Escape Room", expanded=False):
        st.markdown("""
**Welcome to EREBUS-7, a derelict space station!**

You've woken up with life support failing. Your goal is to solve **5 riddles** to restore power and escape.

**How it works:**
- 🧩 Each riddle you solve repairs a critical system on the station
- 💨 Your oxygen level goes **up** when you answer correctly, and **down** when you're wrong
- 📉 If oxygen hits 0%, it's game over — so think carefully before answering!
- 🏆 Solve all 5 riddles to win and escape the station

**Tips for playing:**
- Read each riddle carefully before answering
- Type your answer in the chat box at the bottom and press Enter
- The answers are often simpler than they seem — think creatively!
- You can type **"hint"** if you're completely stuck
- Use **Start Over** in the sidebar to restart anytime
        """)


def render_mind_reader_guide():
    with st.expander("📖 How to Play — Mind Reader", expanded=False):
        st.markdown("""
**The AI will try to read your mind!**

Think of a **number between 1 and 100**, or any **object, animal, person, or thing** — and the AI will try to guess what you're thinking.

**How it works:**
- 🤔 Think of something and keep it firmly in your head
- ❓ The AI asks you up to **10 yes or no questions**
- ✅ Answer each question honestly with **Yes** or **No**
- 🎯 After gathering enough clues, the AI reveals its guess

**Tips for playing:**
- Be as honest as possible — the AI can only guess based on your answers
- You can pick absolutely anything: a colour, an animal, a country, a food, a celebrity
- Short answers work best: just type "Yes", "No", or "I'm not sure"
- Press **Start Over** in the sidebar to try with something new
        """)


def render_personality_guide():
    with st.expander("📖 How to Play — Personality Quiz", expanded=False):
        st.markdown("""
**Discover what makes you, you.**

Answer **5 open-ended questions** and receive a detailed personality profile based on psychology research.

**How it works:**
- 💬 You'll be asked 5 thoughtful questions, one at a time
- ✍️ Write your answer in the chat box and press Enter
- 🧬 After all 5 questions, you receive your full personality report

**Your report includes:**
- Your unique **personality archetype** (e.g. "The Visionary Architect")
- Scores across the **Big Five personality dimensions**
- A **Myers-Briggs type** suggestion
- Your **key strengths**, growth areas, and career insights
- A **famous personality match**

**Tips for best results:**
- There are no right or wrong answers — just be genuine
- The more detail you write in each answer, the more accurate your profile will be
- This quiz is for fun and reflection — treat it as a conversation, not a test
- Press **Start Over** in the sidebar to get a completely fresh analysis
        """)


# ── Dashboard ──────────────────────────────────
def render_dashboard():
    st.markdown("# 🎮 AI Playground")
    st.markdown("Three interactive AI experiences, ready to play. Pick one below to get started.")
    st.divider()

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div style="background:#16213e; border:1px solid #2a2a4a; border-radius:14px;
                    padding:1.5rem; min-height:200px;">
            <div style="font-size:2.2rem; margin-bottom:0.6rem;">🚀</div>
            <div style="font-size:1.05rem; font-weight:700; color:#fff; margin-bottom:0.5rem;">Escape Room</div>
            <div style="font-size:0.85rem; color:#9090b0; line-height:1.6;">
                Trapped on a broken space station. Solve 5 riddles before your oxygen runs out and escape.
            </div>
            <div style="margin-top:1rem; font-size:0.75rem; color:#5050a0;">
                🧩 5 riddles &nbsp;·&nbsp; 💨 Oxygen timer
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Play Escape Room", key="dash_escape", use_container_width=True):
            switch_mode("escape_room")
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:#16213e; border:1px solid #2a2a4a; border-radius:14px;
                    padding:1.5rem; min-height:200px;">
            <div style="font-size:2.2rem; margin-bottom:0.6rem;">🔮</div>
            <div style="font-size:1.05rem; font-weight:700; color:#fff; margin-bottom:0.5rem;">Mind Reader</div>
            <div style="font-size:0.85rem; color:#9090b0; line-height:1.6;">
                Think of anything — number, animal, object. The AI asks yes/no questions and guesses what it is.
            </div>
            <div style="margin-top:1rem; font-size:0.75rem; color:#5050a0;">
                ❓ Up to 10 questions &nbsp;·&nbsp; 🎯 AI guess
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Play Mind Reader", key="dash_mind", use_container_width=True):
            switch_mode("mind_reader")
            st.rerun()

    with col3:
        st.markdown("""
        <div style="background:#16213e; border:1px solid #2a2a4a; border-radius:14px;
                    padding:1.5rem; min-height:200px;">
            <div style="font-size:2.2rem; margin-bottom:0.6rem;">🧠</div>
            <div style="font-size:1.05rem; font-weight:700; color:#fff; margin-bottom:0.5rem;">Personality Quiz</div>
            <div style="font-size:0.85rem; color:#9090b0; line-height:1.6;">
                Answer 5 questions. Get your personality archetype, strengths, Myers-Briggs type, and more.
            </div>
            <div style="margin-top:1rem; font-size:0.75rem; color:#5050a0;">
                💬 5 questions &nbsp;·&nbsp; 📊 Full profile
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        if st.button("Take the Quiz", key="dash_personality", use_container_width=True):
            switch_mode("personality")
            st.rerun()

    st.divider()
    st.caption("Select any experience above to begin. No account or sign-up needed.")


# ── Escape Room Page ───────────────────────────
def render_escape_room():
    if st.button("← Back to Home", key="back_escape"):
        switch_mode("dashboard")
        st.rerun()
    st.markdown("# 🚀 Escape Room")
    st.markdown("You're aboard the derelict space station **EREBUS-7**. Solve the riddles. Escape before oxygen runs out.")

    render_escape_room_guide()
    st.divider()

    result = st.session_state.last_result

    if result:
        oxygen = result.get("oxygen_level", 23)
        puzzles = result.get("puzzles_solved", 0)
        game_status = result.get("game_status", "active")

        col1, col2, col3 = st.columns(3)
        with col1:
            o_label = "🟢" if oxygen > 50 else ("🟡" if oxygen > 25 else "🔴")
            st.metric(f"{o_label} Oxygen Level", f"{oxygen}%")
        with col2:
            st.metric("🧩 Puzzles Solved", f"{puzzles} / 5")
        with col3:
            current = result.get("current_puzzle", "POWER_GRID").replace("_", " ").title()
            st.metric("📍 Current Puzzle", current)

        st.caption("Oxygen remaining:")
        st.progress(max(0, oxygen) / 100)
        st.caption("Overall progress:")
        st.progress(puzzles / 5)

        solved_list = result.get("solved_list", [])
        if solved_list:
            st.caption("Solved: " + "  ·  ".join([f"✅ {p.replace('_', ' ').title()}" for p in solved_list]))

        st.divider()

        if game_status == "won":
            st.balloons()
            st.success("🎉 **You escaped EREBUS-7!** All systems restored. Congratulations!")
            return
        elif game_status == "lost":
            st.error("💀 **Oxygen depleted.** You didn't make it this time. Press **Start Over** in the sidebar to try again.")
            return

    render_chat_history()

    user_input = st.chat_input("Type your answer here...", key="escape_input")
    if user_input:
        handle_escape_room_input(user_input)

    if not st.session_state.session_active:
        st.info("Ready to begin? Click the button below to start the game.")
        if st.button("🚀 Start the Game", use_container_width=True, key="start_escape"):
            handle_escape_room_input("Start the game.")


def handle_escape_room_input(user_input: str):
    with st.spinner("Thinking..."):
        agent = get_agent("ESCAPE_ROOM")
        if not st.session_state.session_active:
            result = agent.initialize()
            st.session_state.session_active = True
        else:
            result = agent.process(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("narrative", "")})
        st.session_state.last_result = result
    st.rerun()


# ── Mind Reader Page ───────────────────────────
def render_mind_reader():
    if st.button("← Back to Home", key="back_mind"):
        switch_mode("dashboard")
        st.rerun()
    st.markdown("# 🔮 Mind Reader")
    st.markdown("Think of something — a number, animal, object, anything — and the AI will guess it.")

    render_mind_reader_guide()
    st.divider()

    result = st.session_state.last_result

    if result:
        q_asked = result.get("questions_asked", 0)
        confidence = result.get("confidence", 0)
        phase = result.get("phase", "thinking")
        category = result.get("category", "unknown").title()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("❓ Questions Asked", f"{q_asked} / 10")
        with col2:
            st.metric("🎯 AI Confidence", f"{confidence}%")
        with col3:
            st.metric("📂 Category", category)

        # Step tracker
        st.caption("Question progress:")
        step_cols = st.columns(10)
        for i, scol in enumerate(step_cols):
            with scol:
                if i < q_asked:
                    st.markdown("🟣")
                else:
                    st.markdown("⚪")

        st.caption("AI confidence level:")
        st.progress(confidence / 100)

        known_facts = result.get("known_facts", [])
        if known_facts:
            st.caption("Clues gathered: " + "  ·  ".join(known_facts))

        final_guess = result.get("final_guess")
        if final_guess and phase in ("guessing", "revealed"):
            st.divider()
            st.success(f"🔮 **The AI guesses: {final_guess.upper()}**")
            if phase == "revealed":
                st.balloons()

        st.divider()

    render_chat_history()

    user_input = st.chat_input("Answer with Yes or No...", key="mind_input")
    if user_input:
        handle_mind_reader_input(user_input)

    if not st.session_state.session_active:
        st.info("Think of something, then click below when you're ready.")
        if st.button("🔮 Start — Read My Mind", use_container_width=True, key="start_mind"):
            handle_mind_reader_input("I'm ready. Start the mind reading game.")


def handle_mind_reader_input(user_input: str):
    with st.spinner("Sensing your thoughts..."):
        agent = get_agent("MIND_READER")
        if not st.session_state.session_active:
            result = agent.initialize()
            st.session_state.session_active = True
        else:
            result = agent.process(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("narrative", "")})
        st.session_state.last_result = result
    st.rerun()


# ── Personality Page ───────────────────────────
def render_personality():
    if st.button("← Back to Home", key="back_personality"):
        switch_mode("dashboard")
        st.rerun()
    st.markdown("# 🧠 Personality Quiz")
    st.markdown("Answer 5 honest questions to receive your personal psychology profile.")

    render_personality_guide()
    st.divider()

    result = st.session_state.last_result

    if result:
        q_asked = result.get("questions_asked", 0)
        report_ready = result.get("report_ready", False)
        archetype = result.get("archetype")
        mbti = result.get("mbti_type")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Questions Answered", f"{q_asked} / 5")
        with col2:
            st.metric("🌟 Archetype", archetype if archetype else "Analyzing...")

        st.caption("Interview progress:")
        st.progress(q_asked / 5)

        step_cols = st.columns(5)
        for i, scol in enumerate(step_cols):
            with scol:
                if i < q_asked:
                    st.caption(f"✅ Q{i+1}")
                elif i == q_asked and not report_ready:
                    st.caption(f"▶️ Q{i+1}")
                else:
                    st.caption(f"⬜ Q{i+1}")

        # Full report section
        formatted_traits = result.get("formatted_traits", [])
        if formatted_traits and report_ready:
            st.divider()
            st.markdown("### Your Personality Profile")
            if mbti:
                st.markdown(f"**Myers-Briggs Type:** `{mbti}`")
            if archetype:
                st.markdown(f"**Your Archetype:** {archetype}")
            st.markdown("")
            st.markdown("**The Big Five Personality Dimensions:**")
            for trait in formatted_traits:
                score = trait.get("score", 0)
                st.caption(f"{trait['emoji']} **{trait['trait']}** — {trait['description']}")
                st.progress(score / 100)
            st.balloons()
            st.success("✨ Your personality report is complete! Read the full analysis in the chat above.")

        st.divider()

    render_chat_history()

    user_input = st.chat_input("Write your answer here...", key="personality_input")
    if user_input:
        handle_personality_input(user_input)

    if not st.session_state.session_active:
        st.info("Click below to start your 5-question personality quiz.")
        if st.button("🧠 Start My Personality Quiz", use_container_width=True, key="start_personality"):
            handle_personality_input("I'm ready to begin.")


def handle_personality_input(user_input: str):
    with st.spinner("Analyzing..."):
        agent = get_agent("PERSONALITY_ANALYZER")
        if not st.session_state.session_active:
            result = agent.initialize()
            st.session_state.session_active = True
        else:
            result = agent.process(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("narrative", "")})
        st.session_state.last_result = result
    st.rerun()


# ── Shared Chat ────────────────────────────────
def render_chat_history():
    for msg in st.session_state.chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if not content:
            continue
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)


# ── Main ───────────────────────────────────────
def main():
    init_session()
    render_sidebar()

    mode = st.session_state.mode

    if mode != "dashboard" and not check_api_key():
        st.markdown("# 🎮 AI Playground")
        st.warning("⚠️ Please enter your API key in the sidebar on the left to start playing.")
        st.info("Once your key is entered, you'll have access to all three games.")
        return

    if mode == "dashboard":
        render_dashboard()
    elif mode == "escape_room":
        render_escape_room()
    elif mode == "mind_reader":
        render_mind_reader()
    elif mode == "personality":
        render_personality()


if __name__ == "__main__":
    main()
