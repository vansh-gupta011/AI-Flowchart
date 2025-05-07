import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import os
import re
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# ---------------- Setup ---------------- #
st.set_page_config(page_title="Flowchart Generator", layout="wide")
st.markdown("<style>h1{color:#1f77b4;}</style>", unsafe_allow_html=True)
st.title("🧐 Flowchart Generator")

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ---------------- Utility Functions ---------------- #
def render_mermaid(code: str):
    if not code.strip().startswith("flowchart"):
        st.error("❌ Mermaid code must start with `flowchart TB` or `flowchart LR`.")
        return
    components.html(f"""
    <!DOCTYPE html>
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js"></script>
        <script>
          document.addEventListener("DOMContentLoaded", function() {{
            mermaid.initialize({{
              startOnLoad: true,
              theme: 'default',
              flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'linear' }}
            }});
          }});
        </script>
        <style>.mermaid {{ width: 100%; overflow: auto; font-family: sans-serif; }}</style>
      </head>
      <body><div class="mermaid">{code}</div></body>
    </html>
    """, height=600, scrolling=True)

# ---------------- Tabs ---------------- #
tab1, tab2, tab3, tab4 = st.tabs(["✨ AI Generator", "✍️ Paste MermaidJS", "📘 Symbol Legend", "🆚 Compare Mermaid & D2"])

# ---------------- Tab 1: AI Generator ---------------- #
with tab1:
    st.subheader("Describe your process below:")
    try:
        response = requests.get(f"{API_URL}")
        if response.status_code == 200:
            st.sidebar.success("✅ Connected to API")
        else:
            st.sidebar.error("❌ API returned an error")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Cannot connect to API")
        st.sidebar.info(f"Make sure API is running at {API_URL}")

    user_prompt = st.text_area("📝 What process should I visualize?", "Process for approving a loan application", height=150)
    direction = st.radio("📐 Flowchart Direction", ["Top-to-Bottom", "Left-to-Right"], horizontal=True)
    complexity = st.select_slider("🔄 Complexity", options=["Simple", "Medium", "Detailed"], value="Medium")

    if st.button("🚀 Generate Flowchart"):
        if user_prompt.strip():
            with st.spinner("Generating flowchart..."):
                try:
                    response = requests.post(f"{API_URL}/flowchart/mermaid", json={"prompt": user_prompt, "direction": direction, "complexity": complexity})
                    if response.status_code == 200:
                        data = response.json()
                        mermaid_code = data["mermaid_code"]
                        if not mermaid_code.startswith("flowchart") or any(bad in mermaid_code for bad in ["Syntax error", "```"]):
                            st.error("❌ MermaidJS returned invalid syntax. Please retry or simplify your input.")
                            st.code(mermaid_code, language="mermaid")
                        else:
                            st.success("✅ Flowchart generated!")
                            st.code(mermaid_code, language="mermaid")
                            st.subheader("📊 Flowchart Preview")
                            render_mermaid(mermaid_code)
                            st.download_button("📥 Download Mermaid Code", data=mermaid_code, file_name="flowchart.mmd", mime="text/plain", key="ai_tab_download")
                    else:
                        st.error(f"❌ API Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please enter a prompt first.")

# ---------------- Tab 2: Manual Mermaid ---------------- #
with tab2:
    st.subheader("Paste your MermaidJS code below:")
    example_code = """flowchart TB
start([Start]) --> process1[Receive Application]
process1 --> input1[/Review Documents/]
input1 --> decision1{Credit Score > 700?}
decision1 -->|Yes| process2[Approve Loan]
decision1 -->|No| process3[Additional Review]
process2 --> end([End])
process3 --> end"""
    code_input = st.text_area("💻 Mermaid Code", value=example_code, height=300)
    if code_input.strip():
        st.code(code_input, language="mermaid")
        st.subheader("📊 Flowchart Preview")
        try:
            render_mermaid(code_input)
            st.download_button("📥 Download Mermaid Code", data=code_input, file_name="flowchart.mmd", mime="text/plain", key="manual_tab_download")
        except Exception as e:
            st.error(f"❌ Error rendering flowchart: {str(e)}")

# ---------------- Tab 3: Symbol Legend ---------------- #
with tab3:
    st.subheader("📒 Flowchart Symbol Guide")
    col1, col2 = st.columns([3, 2])
    with col1:
        symbol_data = {
            "Symbol": ["Start/End", "Process", "Decision", "Input", "Output", "Connection", "Connection with Label"],
            "Shape": ["Oval/Rounded", "Rectangle", "Diamond", "Parallelogram (slant right)", "Parallelogram (slant left)", "Arrow", "Arrow with text"],
            "Mermaid Syntax": ["([Start]) or ([End])", "[Process step]", "{Decision question?}", "[/Input information/]", "[\\Output result\\]", "-->", "-->|Yes/No|"]
        }
        st.table(pd.DataFrame(symbol_data))
    with col2:
        st.subheader("Example Mermaid Code")
        st.code("""flowchart TB
start([Start]) --> input1[/Enter User Data/]
input1 --> process1[Validate Data]
process1 --> decision1{Is Valid?}
decision1 -->|Yes| output1[\\Show Success\\]
decision1 -->|No| input1
output1 --> end([End])
""", language="mermaid")
    st.subheader("Mermaid Flowchart Tips")
    st.markdown("""
    - **Node IDs** must be unique (e.g., `id1`, `process2`)
    - **Direction options**: TB (top-bottom), LR (left-right), RL, BT
    - **Subgraphs**: Use `subgraph title ... end` to group nodes
    - **Styling**: Add style with `style nodeId fill:#f9f,stroke:#333`
    - **Classes**: Define classes with `classDef className fill:#f9f,stroke:#333`
    - **Comments**: Use `%% This is a comment` for notes
    """)
    sample_code = """flowchart TB
start([Start]) --> process1[Process]
process1 --> decision{Decision?}
decision -->|Yes| input[/Input/]
decision -->|No| output[\\Output\\]
input --> end([End])
output --> end"""
    render_mermaid(sample_code)

# ---------------- Tab 4: Compare Mermaid & D2 ---------------- #
def render_d2(code: str):
    encoded = urllib.parse.quote(code)
    embed_url = f"https://play.d2lang.com/?embed=1&code={encoded}"
    st.components.v1.iframe(embed_url, height=600, scrolling=True)

with tab4:
    st.subheader("🧠 Compare Mermaid vs D2 with Images")
    prompt = st.text_area("Enter a prompt", "Process for handling customer support ticket with document upload")

    col1, col2 = st.columns(2)
    with col1:
        direction = st.radio("Flow Direction", ["Top-to-Bottom", "Left-to-Right"], horizontal=True, key="compare_direction")
    with col2:
        complexity = st.selectbox("Complexity", ["Simple", "Medium", "Detailed"], index=1, key="compare_complexity")

    if st.button("🔍 Generate Flowcharts with Images"):
        with st.spinner("Generating both diagrams with images in D2..."):
            try:
                m_res = requests.post(f"{API_URL}/flowchart/mermaid", json={"prompt": prompt, "direction": direction, "complexity": complexity})
                d_res = requests.post(f"{API_URL}/flowchart/d2", json={"prompt": prompt, "direction": direction, "complexity": complexity})

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🐟 Mermaid Flowchart")
                    if m_res.status_code == 200:
                        mermaid_code = m_res.json()["mermaid_code"]
                        st.code(mermaid_code, language="mermaid")
                        render_mermaid(mermaid_code)
                        st.download_button("📥 Download Mermaid Code", mermaid_code, "flowchart.mmd", "text/plain", key="compare_mermaid_download")
                    else:
                        st.error("Mermaid generation failed")

                with col2:
                    st.markdown("### 🖼️ D2 Flowchart (with Images)")
                    if d_res.status_code == 200:
                        d2_code = d_res.json()["d2_code"]
                        st.code(d2_code, language="plaintext")
                        render_d2(d2_code)
                        st.download_button("📥 Download D2 Code", d2_code, "flowchart.d2", "text/plain", key="compare_d2_download")
                    else:
                        st.error("D2 generation failed")

            except Exception as e:
                st.error(f"Error: {e}")


