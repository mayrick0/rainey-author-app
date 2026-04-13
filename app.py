import streamlit as st
import google.generativeai as genai
import docx

# 1. BRAIN SETUP
# Replace with your actual key from Google AI Studio
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-pro')

# Helper function to read Word files
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
uploaded_file = st.file_uploader("Upload Manuscript (.docx or .txt)", type=['docx', 'txt'])

if uploaded_file:
    # Read the file
    if uploaded_file.name.endswith('.docx'):
        text_to_edit = read_docx(uploaded_file)
    else:
        text_to_edit = uploaded_file.read().decode("utf-8")

    # Show the stats/cost (using the total tokens)
    token_count = model.count_tokens(text_to_edit).total_tokens
    st.info(f"📊 Manuscript Stats: {token_count:,} tokens identified.")

    target_lang = st.selectbox("Translate to:", ["No Translation", "English", "American English", "British English", "Canadian English","Spanish", "French", "German", "Italian", "Portuguese", "Dutch", "Japanese", "Chinese", "Korean", "Arabic"])

    if st.button("🚀 Start Professional Edit"):
        with st.spinner("Processing your book..."):
            # This is where we plug in the Sidebar settings
            prompt = f"""
            Act as a professional book editor and polyglot. 
            
            1. Identify the source language of the text.
            2. Edit for flow, grammar, and style using the {writing_tone} tone.
            3. Use {english_type} English conventions unless a different target language is selected.
            4. If the user selected a target language ({target_lang}) other than 'No Translation', 
               translate the final polished version into that language.
            
            Special Instructions: {special_notes}

            Manuscript:
            {text_to_edit}
        # Calculate Stats
        word_count = len(text_to_edit.split())
        reading_time = word_count // 250  # Average reading speed
    
        # Display Stats in three nice columns
        col1, col2, col3 = st.columns(3)
        col1.metric("Word Count", f"{word_count:,}")
        col2.metric("Est. Reading Time", f"{reading_time} min")
        col3.metric("Tokens", f"{token_count:,}")
            """
            
            response = model.generate_content(prompt)
            st.subheader("Edited Preview:")
            st.write(response.text)
            
            st.download_button("Download Finished Work", response.text, file_name="edited_manuscript.txt")