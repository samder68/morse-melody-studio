import streamlit as st
from enhanced_morse_music_randomized import generate_random_music
import os

st.set_page_config(page_title="Morse Melody Generator", layout="centered")
st.title("🎵 Morse Melody Generator")
st.markdown("Convert text to music using Morse code and a musical scale.")

# Input fields
text = st.text_input("Enter a phrase:", "Hope is the frequency")
tempo = st.slider("Tempo (BPM)", min_value=60, max_value=180, value=100, step=10)
key = st.selectbox("Key", options=['C', 'D', 'E', 'F', 'G', 'A', 'B'], index=0)
scale_type = st.selectbox("Scale Type", options=['major', 'minor'], index=0)

# Output file name
output_file = "morse_output.mid"

# Run button
if st.button("Generate Melody"):
    try:
        generate_random_music(text, output_file, tempo=tempo, key=key, scale_type=scale_type)
        st.success("""
✅ File created: morse_output.mid
🎧 Ready to play or download!
""")
        with open(output_file, "rb") as f:
            st.download_button(label="⬇️ Download morse_output.mid", data=f, file_name="morse_output.mid")
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.markdown("""
---
Made with 💡 and 🎶 by [Your Name]
""")
