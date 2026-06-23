"""
components/chat_interface.py
──────────────────────────────
Renders the Strategist AI tab with a Claude-style inline input box.
Image upload is via the + button inside the chat input — not the sidebar.
"""

import re
import streamlit as st
import pandas as pd

from config.settings import COLORS
from core.prompt_builder import (
    build_text_prompt,
    build_vision_prompt,
    build_quick_prompt,
    get_quick_actions,
)
from services.gemini_service import is_configured, stream_report


# ── Chart extraction from AI response ────────────────────────────────────────

def _extract_intervention_chart(text: str) -> "pd.DataFrame | None":
    """
    Parse the AI's Policy Recommendations markdown table and extract
    intervention names + impact percentages → DataFrame for st.bar_chart().
    Returns None if no table found.
    """
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 2:
            continue
        intervention = cells[0]
        impact_raw   = cells[1] if len(cells) > 1 else ""
        # Skip header rows
        if any(h in intervention.lower() for h in ["intervention", "action", "policy"]):
            continue
        # Extract first numeric percentage from the impact column
        nums = re.findall(r"[-+]?\d+(?:\.\d+)?", impact_raw)
        if not nums:
            nums = re.findall(r"[-+]?\d+(?:\.\d+)?", line)
        if nums:
            pct = abs(float(nums[0]))
            if 0 < pct <= 100:
                label = intervention[:35] + ("…" if len(intervention) > 35 else "")
                rows.append({"Intervention": label, "Violation Reduction (%)": pct})
    if len(rows) < 2:
        return None
    return pd.DataFrame(rows).set_index("Intervention")


# ── Private Helpers ───────────────────────────────────────────────────────────

def _render_api_key_gate() -> None:


    st.html(f"""
    <div style="background:{COLORS['bg_secondary']}; border:1px solid {COLORS['border']};
                border-left:3px solid {COLORS['warning']}; border-radius:10px;
                padding:20px 22px; margin-top:8px;">
        <div style="font-size:0.9rem; font-weight:600; color:{COLORS['text_primary']};
                    margin-bottom:8px;">Groq API Key Required</div>
        <div style="font-size:0.82rem; color:{COLORS['text_muted']}; line-height:1.7;">
            1. Get your key at <span style="color:{COLORS['text_accent']};">console.groq.com/keys</span><br>
            2. Open <code style="background:{COLORS['bg_tertiary']};padding:1px 6px;border-radius:3px;">.env</code>
               and set <code style="background:{COLORS['bg_tertiary']};padding:1px 6px;border-radius:3px;">GROQ_API_KEY=gsk_...</code><br>
            3. Restart the app
        </div>
    </div>
    """)


def _render_welcome_panel(has_image: bool) -> None:
    img_status = (
        f'<span style="color:{COLORS["success"]}; font-weight:600;">CCTV frame attached</span> — vision analysis active.'
        if has_image else
        f'No image attached. Use the <b style="color:{COLORS["text_primary"]};">+</b> button in the input box to attach a CCTV frame.'
    )
    st.html(f"""
    <div style="background:{COLORS['bg_secondary']}; border:1px solid {COLORS['border']};
                border-radius:10px; padding:22px 24px; margin-bottom:16px;">
        <div style="font-size:1rem; font-weight:700; color:{COLORS['text_primary']};
                    margin-bottom:6px; display:flex; align-items:center; gap:10px;">
            RoadMind-X Strategist AI
            <span style="font-size:0.65rem; font-weight:600; padding:2px 10px;
                         border-radius:20px; background:rgba(47,129,247,0.1);
                         border:1px solid rgba(47,129,247,0.3); color:{COLORS['text_accent']};">
                groq · llama-3.3-70b
            </span>
        </div>
        <div style="font-size:0.82rem; color:{COLORS['text_muted']}; line-height:1.7; margin-bottom:10px;">
            Ask me anything about the current city traffic situation. I will analyze
            the live city intelligence and generate structured strategic reports.
        </div>
        <div style="font-size:0.78rem; color:{COLORS['text_muted']};">{img_status}</div>
    </div>
    """)


def _render_quick_actions(has_image: bool) -> str | None:
    actions = get_quick_actions()
    st.html(f"""<div style="font-size:0.68rem; font-weight:600; color:{COLORS['text_muted']};
                text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">
                Quick Actions</div>""")
    cols = st.columns(len(actions))
    clicked = None
    for col, action in zip(cols, actions):
        with col:
            if st.button(action["label"], key=f"quick_{action['key']}",
                         help=action["description"], use_container_width=True):
                clicked = build_quick_prompt(action["key"])
    if has_image and clicked:
        clicked = build_vision_prompt(clicked)
    return clicked


def _render_chat_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user" and msg.get("has_image"):
                st.markdown(
                    f"<span style='font-size:0.75rem;color:{COLORS['text_muted']};'>📸 CCTV image attached</span>",
                    unsafe_allow_html=True,
                )
            st.markdown(msg["content"])


def _run_analysis(system_prompt: str, user_prompt: str, image_bytes: bytes | None) -> None:
    st.session_state.messages.append({
        "role": "user", "content": user_prompt, "has_image": image_bytes is not None,
    })
    with st.chat_message("user"):
        if image_bytes:
            st.markdown(
                f"<span style='font-size:0.75rem;color:{COLORS['text_muted']};'>📸 CCTV image attached</span>",
                unsafe_allow_html=True,
            )
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        placeholder   = st.empty()
        full_response = ""
        try:
            with st.spinner("Strategist AI analyzing…"):
                for chunk in stream_report(system_prompt, user_prompt, image_bytes):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

            # ── Streamlit Hack: bar chart inside chat if policy table detected ──
            chart_df = _extract_intervention_chart(full_response)
            if chart_df is not None:
                st.markdown(
                    f"<div style='font-size:0.75rem; font-weight:600; "
                    f"color:{COLORS['text_muted']}; margin-top:12px; margin-bottom:4px;'>"
                    f"Predicted Violation Reduction by Intervention</div>",
                    unsafe_allow_html=True,
                )
                st.bar_chart(
                    chart_df,
                    color="#2F81F7",
                    height=200,
                )

        except EnvironmentError as exc:
            placeholder.error(str(exc))
            full_response = f"[Error] {exc}"
        except RuntimeError as exc:
            placeholder.error(f"**Groq API error.** {exc}")
            full_response = f"[Error] {exc}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})


# ── Public API ────────────────────────────────────────────────────────────────

def render_chat_interface(system_prompt: str) -> None:
    """Render the Strategist AI tab with Claude-style inline chat input."""

    if not is_configured():
        _render_api_key_gate()
        return

    # ── Inline image state ────────────────────────────────────────────────────
    if "inline_img" not in st.session_state:
        st.session_state.inline_img = None

    inline_img  = st.session_state.inline_img
    image_bytes: bytes | None = None
    if inline_img is not None:
        inline_img.seek(0)
        image_bytes = inline_img.read()
    has_image = image_bytes is not None

    # ── Welcome + quick actions ───────────────────────────────────────────────
    if not st.session_state.messages:
        _render_welcome_panel(has_image)

    quick_prompt = _render_quick_actions(has_image)

    st.markdown("<hr style='border:none;border-top:1px solid #21262D;margin:10px 0;'>",
                unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────────────
    _render_chat_history()

    if quick_prompt:
        _run_analysis(system_prompt, quick_prompt, image_bytes)
        st.session_state.inline_img = None
        st.rerun()

    # ── Attached image preview ────────────────────────────────────────────────
    if has_image:
        p1, p2 = st.columns([8, 1])
        with p1:
            st.image(image_bytes, width=100)
        with p2:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            if st.button("✕", key="rmx_clear_img", help="Remove image"):
                st.session_state.inline_img = None
                st.rerun()

    # ── Claude-style single-line input bar ───────────────────────────────────
    st.markdown("""
    <style>
    /* ═══ Unified dark input bar ═══════════════════════════════════════════ */
    div[data-testid="stForm"] {
        background: #1a1a1c !important;
        border: 1px solid #2a2a2e !important;
        border-radius: 12px !important;
        padding: 2px 10px 2px 4px !important;
        margin-top: 8px !important;
    }
    div[data-testid="stForm"]:focus-within {
        border-color: #3a3a3e !important;
    }
    /* Remove all column gaps */
    div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: center !important;
    }
    div[data-testid="stForm"] [data-testid="stColumn"] {
        padding: 0 !important;
        min-width: 0 !important;
    }
    /* ── Text input: transparent, no border ── */
    div[data-testid="stForm"] input[type="text"] {
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        color: #e5e5e7 !important;
        font-size: 0.9rem !important;
        padding: 11px 6px !important;
        caret-color: #2F81F7 !important;
        font-family: -apple-system, 'Inter', sans-serif !important;
    }
    div[data-testid="stForm"] input[type="text"]::placeholder {
        color: #555560 !important;
        font-weight: 400 !important;
    }
    div[data-testid="stForm"] [data-testid="stTextInput"] > div > div,
    div[data-testid="stForm"] [data-testid="stTextInput"] > div,
    div[data-testid="stForm"] [data-testid="stTextInputRootElement"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    div[data-testid="stForm"] [data-testid="stTextInput"] label { display: none !important; }
    /* ── + button: plain text, no background, no border ── */
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
    div[data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"] {
        all: unset !important;
        color: #888890 !important;
        font-size: 1.3rem !important;
        font-weight: 300 !important;
        line-height: 1 !important;
        padding: 4px 12px 4px 10px !important;
        cursor: pointer !important;
        border-radius: 6px !important;
        transition: color 0.15s !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover,
    div[data-testid="stForm"] button[data-testid="baseButton-secondaryFormSubmit"]:hover {
        color: #e5e5e7 !important;
    }
    /* ── Send ↑ button: pill, blue, tight ── */
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"] {
        all: unset !important;
        background: #2F81F7 !important;
        color: #fff !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background 0.15s !important;
        line-height: 1 !important;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
    div[data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"]:hover {
        background: #1a6fe0 !important;
    }
    /* ── Vertical divider ── */
    .rmx-vdivider {
        width: 1px; height: 16px;
        background: #2e2e32;
        display: block;
        margin: 0 2px;
    }
    </style>
    """, unsafe_allow_html=True)


    with st.form("rmx_chat_form", clear_on_submit=True, border=False):
        col_plus, col_div, col_text, col_send = st.columns([0.6, 0.05, 10, 0.8])

        with col_plus:
            plus_hit = st.form_submit_button("+", type="secondary", use_container_width=True)

        with col_div:
            st.html('<div class="rmx-vdivider"></div>')

        with col_text:
            user_text = st.text_input(
                "msg",
                placeholder="Ask anything",
                label_visibility="collapsed",
            )

        with col_send:
            sent = st.form_submit_button("↑", type="primary", use_container_width=True)

    # ── Toggle uploader when + is pressed ────────────────────────────────────
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    if plus_hit:
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()

    if st.session_state.show_uploader:
        img_upload = st.file_uploader(
            "Attach CCTV frame",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="rmx_inline_uploader",
        )
        if img_upload is not None:
            st.session_state.inline_img = img_upload
            st.session_state.show_uploader = False
            st.rerun()


    # ── Handle ↑ send ─────────────────────────────────────────────────────────
    if sent and user_text.strip():
        prompt = (
            build_vision_prompt(user_text.strip())
            if has_image else
            build_text_prompt(user_text.strip())
        )
        _run_analysis(system_prompt, prompt, image_bytes)
        st.session_state.inline_img = None
        st.rerun()

    # ── Clear history ─────────────────────────────────────────────────────────

    if st.session_state.messages:
        _, col_clear = st.columns([7, 1])
        with col_clear:
            if st.button("Clear", key="rmx_clear_chat"):
                st.session_state.messages = []
                st.rerun()
