import streamlit as st
import google.generativeai as genai
import docx

# 1. BRAIN SETUP
GEMINI_KEY = st.secrets["GEMINI_KEY"]

try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-pro')
except Exception as e:
    st.error(f"Setup Error: {e}")

# Helper for Word docs
def read_docx(file):
    doc = docx.Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])


# 2. SIDEBAR (The "Editor Settings")
with st.sidebar:
    st.header("🎨 Editor Personality")
    writing_tone = st.select_slider(
        "Manuscript Tone",
        options=["Raw & Gritty", "Balanced", "Poetic & Flowery"]
    )
    english_type = st.radio("English Dialect", ["American", "British", "Canadian"])

    st.divider()
    st.header("🎯 Custom Focus")
    special_notes = st.text_area(
        "Instructions for the AI",
        placeholder="e.g. 'Make the dialogue snappier' or 'Focus on suspense'"
    )


# 3. MAIN INTERFACE
st.title("✍️ Rainey's Author Suite")

# File Uploader
uploaded_file = st.file_uploader("Upload Manuscript", type=['docx', 'txt'])

if uploaded_file is not None:
    # Reset session state if a new file is uploaded
    if "manuscript_text" not in st.session_state or st.session_state.get("last_file") != uploaded_file.name:
        st.session_state.last_file = uploaded_file.name
        if uploaded_file.name.endswith('.docx'):
            st.session_state.manuscript_text = read_docx(uploaded_file)
        else:
            st.session_state.manuscript_text = uploaded_file.read().decode("utf-8")

    text_to_edit = st.session_state.manuscript_text

    # Calculate stats
    word_count = len(text_to_edit.split())

    try:
        token_count = model.count_tokens(text_to_edit).total_tokens
    except:
        token_count = "Calculated by AI"

    st.info(f"📊 Manuscript Stats: {word_count:,} words | Tokens: {token_count}")

    # Edit button
    if st.button("🚀 Start Professional Edit"):
        prompt = f"""
        Act as a professional book editor.

        1. Tone: {writing_tone}
        2. Dialect: {english_type} English
        3. Special Instructions: {special_notes}

        Please edit the following manuscript:
        {text_to_edit}
        """

        with st.spinner("Editing in progress..."):
            response = model.generate_content(prompt)

        st.subheader("Edited Preview")
        st.write(response.text)
        st.download_button("Download Finished Work", response.text, file_name="edited_manuscript.txt")