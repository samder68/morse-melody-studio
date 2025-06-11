import streamlit as st
import base64
import mido
from enhanced_morse_music import (
    generate_enhanced_files_from_text, 
    INSTRUMENT_PRESETS, 
    KEY_PRESETS,
    SCALES,
    CHORD_PROGRESSIONS,
    MUSICAL_STYLES
)

# Morse code dictionary for decoding
MORSE_CODE_DICT = {
    'A': '.-',    'B': '-...',  'C': '-.-.', 'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',  'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',  'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',  'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',  'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',  'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ' ': '/'
}
REVERSE_MORSE = {v: k for k, v in MORSE_CODE_DICT.items()}

# Enhanced page configuration with mobile optimization
st.set_page_config(
    page_title="Enhanced Morse Melody Studio", 
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# Enhanced Morse Melody Studio\nCreate beautiful music with hidden morse code messages!"
    }
)

# Mobile-optimized CSS
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stSelectbox > div > div {
            font-size: 14px;
        }
        .stSlider > div > div {
            font-size: 12px;
        }
        .stButton > button {
            width: 100%;
            margin: 2px 0;
        }
        .stColumns > div {
            padding: 0 5px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
    }
    
    /* Enhanced styling */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .feature-box {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit branding on mobile */
    @media (max-width: 768px) {
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    }
</style>
""", unsafe_allow_html=True)

# PWA Meta Tags
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1f1f2e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Morse Studio">
""", unsafe_allow_html=True)

st.title("🎵 Enhanced Morse Melody Studio")
st.caption("Create rich, musical compositions while encoding secret messages in Morse code")

tab1, tab2 = st.tabs(["🎼 Compose & Encode", "🔍 Decode & Analyze"])

# ---------------------- ENHANCED ENCODER TAB ----------------------
with tab1:
    st.header("🎹 Musical Composition Studio")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_area(
            "Your Secret Message:", 
            value="Hope is the frequency",
            help="This message will be encoded in the melody line using Morse code"
        )
    
    with col2:
        st.info("💡 **How it works:**\nYour message becomes the melody while AI-enhanced harmony, bass, and rhythm create a full musical arrangement!")
    
    # Musical Style Presets (New Feature)
    st.subheader("🎨 Musical Style Presets")
    style_cols = st.columns(4)
    
    with style_cols[0]:
        if st.button("🎹 Piano Ballad", use_container_width=True):
            st.session_state.update({
                'tempo': 80, 'melody_inst': 'Piano', 'harmony_inst': 'Strings',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'classic',
                'style': 'ballad'
            })
            st.rerun()
    
    with style_cols[1]:
        if st.button("🎸 Folk Song", use_container_width=True):
            st.session_state.update({
                'tempo': 100, 'melody_inst': 'Acoustic Guitar', 'harmony_inst': 'Acoustic Guitar',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'folk',
                'style': 'folk'
            })
            st.rerun()
    
    with style_cols[2]:
        if st.button("🎺 Jazz Standard", use_container_width=True):
            st.session_state.update({
                'tempo': 120, 'melody_inst': 'Trumpet', 'harmony_inst': 'Electric Piano',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'major', 'chord_prog': 'pop',
                'style': 'jazz'
            })
            st.rerun()
    
    with style_cols[3]:
        if st.button("🌙 Ambient", use_container_width=True):
            st.session_state.update({
                'tempo': 70, 'melody_inst': 'Pad', 'harmony_inst': 'Strings',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': False,
                'add_drums': False, 'scale_type': 'minor', 'chord_prog': 'minor',
                'style': 'ambient'
            })
            st.rerun()
    
    # Musical configuration
    st.subheader("🎛️ Detailed Musical Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🎵 Basic Settings**")
        tempo = st.slider("Tempo (BPM)", 60, 180, 
                         st.session_state.get('tempo', 120), 5)
        key_center = st.selectbox("Key Center", list(KEY_PRESETS.keys()), 
                                 index=0)
        scale_type = st.selectbox("Scale Type", list(SCALES.keys()), 
                                 index=list(SCALES.keys()).index(st.session_state.get('scale_type', 'major')))
        
    with col2:
        st.write("**🎹 Instruments**")
        melody_inst = st.selectbox("Melody Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                  index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('melody_inst', 'Piano')))
        harmony_inst = st.selectbox("Harmony Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                   index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('harmony_inst', 'Strings')))
        bass_inst = st.selectbox("Bass Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('bass_inst', 'Bass')))
    
    with col3:
        st.write("**🎶 Arrangement**")
        add_harmony = st.checkbox("Add AI Harmony", 
                                 value=st.session_state.get('add_harmony', True))
        add_bass = st.checkbox("Add Bass Line", 
                              value=st.session_state.get('add_bass', True))
        add_drums = st.checkbox("Add Drum Track", 
                               value=st.session_state.get('add_drums', False))
        
        if add_harmony:
            chord_prog = st.selectbox("Chord Progression", list(CHORD_PROGRESSIONS.keys()), 
                                     index=list(CHORD_PROGRESSIONS.keys()).index(st.session_state.get('chord_prog', 'classic')))
        else:
            chord_prog = 'classic'
    
    # AI Enhancement Options
    st.subheader("🤖 AI Enhancement Options")
    col1, col2 = st.columns(2)
    
    with col1:
        ai_harmony = st.checkbox("Smart Harmony Following", value=True, 
                                help="AI analyzes melody to create better chord progressions")
        walking_bass = st.checkbox("Walking Bass Lines", value=True,
                                  help="Creates smoother, more musical bass movement")
    
    with col2:
        humanize = st.checkbox("Humanize Timing", value=True,
                              help="Adds subtle timing variations for more natural feel")
        smart_dynamics = st.checkbox("Dynamic Expression", value=True,
                                    help="Varies volume and intensity musically")
    
    # Generate button
    if st.button("🎵 Generate AI-Enhanced Musical Composition", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("🎼 Composing your AI-enhanced musical masterpiece..."):
                # Prepare musical options
                musical_options = {
                    'tempo': tempo,
                    'key_root': KEY_PRESETS[key_center],
                    'scale_type': scale_type,
                    'add_harmony': add_harmony,
                    'add_bass': add_bass,
                    'add_drums': add_drums,
                    'chord_progression': chord_prog,
                    'melody_instrument': INSTRUMENT_PRESETS[melody_inst],
                    'harmony_instrument': INSTRUMENT_PRESETS[harmony_inst],
                    'bass_instrument': INSTRUMENT_PRESETS[bass_inst],
                    'style': st.session_state.get('style', 'ballad'),
                    'ai_harmony': ai_harmony,
                    'walking_bass': walking_bass,
                    'humanize': humanize,
                    'smart_dynamics': smart_dynamics
                }
                
                try:
                    midi_path, wav_path, morse_code = generate_enhanced_files_from_text(
                        user_input, **musical_options
                    )
                    
                  # In the generate button section, around line where you handle downloads
if midi_path and wav_path:
    st.success("✅ AI-Enhanced Musical Composition Complete!")
    # ... existing code ...
    
    # Audio player - only show if WAV exists
    if wav_path and os.path.exists(wav_path):
        st.subheader("🎧 Listen to Your Composition")
        st.audio(wav_path, format='audio/wav')
    else:
        st.info("🎵 MIDI file generated successfully! WAV playback not available on this platform.")
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # MIDI download (this should always work)
        with open(midi_path, "rb") as f:
            midi_bytes = f.read()
        # ... rest of MIDI download code ...
    
    with col2:
        # WAV download - only show if file exists
        if wav_path and os.path.exists(wav_path):
            with open(wav_path, "rb") as f:
                wav_bytes = f.read()
            st.download_button(
                "🎵 Download Audio File",
                wav_bytes,
                file_name=filename,
                mime="audio/wav",
                use_container_width=True
            )
        else:
            st.info("WAV download not available - MIDI works on all platforms!")
                        
                        # Audio player with enhanced controls
                        st.subheader("🎧 Listen to Your Composition")
                        st.audio(wav_path, format='audio/wav')
                        
                        # Enhanced download section
                        st.subheader("📥 Download Your Files")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with open(midi_path, "rb") as f:
                                midi_bytes = f.read()
                            filename = f"morse_composition_{user_input[:10].replace(' ', '_')}_{tempo}bpm.mid"
                            st.download_button(
                                "📄 Download MIDI File",
                                midi_bytes,
                                file_name=filename,
                                mime="audio/midi",
                                use_container_width=True
                            )
                        
                        with col2:
                            with open(wav_path, "rb") as f:
                                wav_bytes = f.read()
                            filename = f"morse_composition_{user_input[:10].replace(' ', '_')}_{tempo}bpm.wav"
                            st.download_button(
                                "🎵 Download Audio File",
                                wav_bytes,
                                file_name=filename,
                                mime="audio/wav",
                                use_container_width=True
                            )
                        
                        with col3:
                            # Create a text file with the message and morse code
                            info_text = f"""MORSE MELODY COMPOSITION
=========================

Original Message: {user_input}
Morse Code: {morse_code}
Musical Key: {key_center} {scale_type}
Tempo: {tempo} BPM
Style: {st.session_state.get('style', 'Custom')}

Generated by Enhanced Morse Melody Studio
"""
                            st.download_button(
                                "📋 Download Info File",
                                info_text,
                                file_name=f"composition_info_{user_input[:10].replace(' ', '_')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                    
                    else:
                        st.error("❌ Error generating musical files. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.write("Please check your settings and try again.")
        
        else:
            st.warning("⚠️ Please enter a message to encode.")

# ---------------------- ENHANCED DECODER TAB ----------------------
with tab2:
    st.header("🔍 Message Decoder & Musical Analysis")
    
    uploaded_midi = st.file_uploader(
        "Upload MIDI File to Decode", 
        type=["mid", "midi"],
        help="Upload a MIDI file created by this tool to decode the hidden message"
    )
    
    if uploaded_midi is not None:
        st.info("🔬 Analyzing uploaded MIDI file...")
        
        try:
            mid = mido.MidiFile(file=uploaded_midi)
            
            # Enhanced MIDI analysis
            ticks_per_beat = mid.ticks_per_beat
            current_time = 0
            note_events = []
            
            # Track information
            st.subheader("📊 MIDI File Information")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Number of Tracks", len(mid.tracks))
            with col2:
                st.metric("Ticks Per Beat", ticks_per_beat)
            with col3:
                total_time = sum(msg.time for track in mid.tracks for msg in track)
                st.metric("Total Ticks", total_time)
            with col4:
                # Calculate estimated duration
                estimated_duration = total_time / ticks_per_beat / 2  # Rough estimate
                st.metric("Est. Duration", f"{estimated_duration:.1f}s")
            
            # Extract melody track (assumed to be first track with notes)
            melody_track = None
            for i, track in enumerate(mid.tracks):
                has_notes = any(msg.type in ['note_on', 'note_off'] for msg in track)
                if has_notes:
                    melody_track = track
                    st.write(f"🎵 Using track {i} for melody analysis")
                    break
            
            if melody_track:
                # Extract note events from melody track
                current_time = 0
                for msg in melody_track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        note_events.append((msg.note, current_time, "on"))
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        note_events.append((msg.note, current_time, "off"))
                
                # Process note durations
                active_notes = {}
                note_durations = []
                
                for note, time, state in note_events:
                    if state == "on":
                        active_notes[note] = time
                    elif state == "off" and note in active_notes:
                        start_time = active_notes[note]
                        duration = time - start_time
                        note_durations.append((start_time, duration))
                        del active_notes[note]
                
                note_durations.sort()
                
                if note_durations:
                    # Enhanced morse decoding with better analysis
                    durations = [dur for _, dur in note_durations]
                    min_duration = min(durations)
                    max_duration = max(durations)
                    avg_duration = sum(durations) / len(durations)
                    
                    # Dynamic threshold calculation
                    base_unit = min_duration
                    
                    # More sophisticated morse detection
                    morse_symbols = []
                    current_morse_letter = ""
                    
                    for i, (start_time, duration) in enumerate(note_durations):
                        # Improved dot/dash detection
                        if duration <= base_unit * 1.8:
                            symbol = "."
                        elif duration <= base_unit * 4.5:
                            symbol = "-"
                        else:
                            symbol = "?"
                        
                        current_morse_letter += symbol
                        
                        if i < len(note_durations) - 1:
                            note_end = start_time + duration
                            next_start = note_durations[i + 1][0]
                            gap = next_start - note_end
                            
                            # Adaptive gap thresholds
                            letter_gap_threshold = base_unit * 2.5
                            word_gap_threshold = base_unit * 5.5
                            
                            if gap >= word_gap_threshold:
                                if current_morse_letter:
                                    morse_symbols.append(current_morse_letter)
                                    current_morse_letter = ""
                                morse_symbols.append("/")
                            elif gap >= letter_gap_threshold:
                                if current_morse_letter:
                                    morse_symbols.append(current_morse_letter)
                                    current_morse_letter = ""
                        else:
                            if current_morse_letter:
                                morse_symbols.append(current_morse_letter)
                    
                    # Display results with enhanced formatting
                    morse_display = ""
                    for i, symbol in enumerate(morse_symbols):
                        if symbol == "/":
                            morse_display += " / "
                        else:
                            morse_display += symbol
                            if i < len(morse_symbols) - 1 and morse_symbols[i + 1] != "/":
                                morse_display += " "
                    
                    st.subheader("📻 Decoded Morse Code")
                    st.code(morse_display.strip())
                    
                    # Decode to text
                    decoded_text = ""
                    words = morse_display.strip().split(" / ")
                    
                    confidence_score = 0
                    total_letters = 0
                    
                    for word_morse in words:
                        letters = word_morse.strip().split(" ")
                        word_text = ""
                        for letter_morse in letters:
                            if letter_morse.strip():
                                decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                word_text += decoded_char
                                total_letters += 1
                                if decoded_char != "?":
                                    confidence_score += 1
                        if word_text:
                            decoded_text += word_text + " "
                    
                    # Calculate confidence
                    confidence = (confidence_score / total_letters * 100) if total_letters > 0 else 0
                    
                    st.subheader("🎯 Hidden Message Revealed")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.success(f"**{decoded_text.strip().upper()}**")
                    with col2:
                        st.metric("Confidence", f"{confidence:.1f}%")
                    
                    # Enhanced detailed analysis
                    with st.expander("🔍 Detailed Musical Analysis"):
                        analysis_col1, analysis_col2 = st.columns(2)
                        
                        with analysis_col1:
                            st.write("**Note Statistics:**")
                            st.metric("Total Notes", len(note_durations))
                            st.metric("Shortest Note", f"{min(durations)} ticks")
                            st.metric("Longest Note", f"{max(durations)} ticks")
                            st.metric("Average Duration", f"{avg_duration:.1f} ticks")
                        
                        with analysis_col2:
                            st.write("**Decoding Analysis:**")
                            dots = morse_display.count('.')
                            dashes = morse_display.count('-')
                            st.metric("Dots (.)", dots)
                            st.metric("Dashes (-)", dashes)
                            st.metric("Words Detected", len(words))
                        
                        st.write("**Letter-by-letter Breakdown:**")
                        for i, word_morse in enumerate(words):
                            with st.container():
                                st.write(f"**Word {i+1}:** `{word_morse}`")
                                letters = word_morse.strip().split(" ")
                                letter_cols = st.columns(min(len(letters), 6))
                                for j, letter_morse in enumerate(letters):
                                    if letter_morse.strip() and j < 6:
                                        decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                        color = "🟢" if decoded_char != "?" else "🔴"
                                        letter_cols[j].write(f"{color} `{letter_morse}` → **{decoded_char}**")
                
                else:
                    st.error("❌ No notes found in the melody track.")
            
            else:
                st.error("❌ No tracks with musical notes found in this MIDI file.")
        
        except Exception as e:
            st.error(f"❌ Error analyzing MIDI file: {str(e)}")
            st.write("Please ensure you've uploaded a valid MIDI file.")

# ---------------------- ENHANCED SIDEBAR INFO ----------------------
with st.sidebar:
    st.header("ℹ️ About This Enhanced Tool")
    st.write("""
    This AI-enhanced Morse melody studio allows you to:
    
    **🎵 Compose:**
    - Encode secret messages in musical melodies
    - AI-generated harmony that follows your melody
    - Walking bass lines with musical intelligence
    - Humanized timing and dynamic expression
    - Multiple musical styles and instruments
    
    **🔍 Decode:**
    - Upload MIDI files to reveal hidden messages
    - Enhanced analysis with confidence scoring
    - Detailed musical structure breakdown
    - Visual letter-by-letter decoding
    
    **🤖 AI Features:**
    - Smart chord progressions that follow melody
    - Musical context-aware note selection
    - Intelligent bass line generation
    - Natural timing variations
    - Dynamic expression control
    
    **🔒 Security:**
    - Messages encoded in melody timing remain intact
    - AI enhancements don't affect morse code
    - Multiple layers of musical camouflage
    """)
    
    st.header("🎹 Enhanced Quick Tips")
    st.write("""
    **For Best Musical Results:**
    - Enable "Smart Harmony Following" for better chords
    - Use "Walking Bass Lines" for smoother bass
    - Try "Humanize Timing" for natural feel
    - Enable "Dynamic Expression" for realism
    
    **Style Recommendations:**
    - 🎹 **Piano Ballad**: Emotional, expressive
    - 🎸 **Folk Song**: Simple, organic feel  
    - 🎺 **Jazz Standard**: Sophisticated harmony
    - 🌙 **Ambient**: Atmospheric, spacey
    """)
    
    st.header("📱 Mobile Features")
    st.write("""
    This app is optimized for mobile devices:
    - Responsive design for phones/tablets
    - Touch-friendly controls
    - Optimized layout for small screens
    - Works offline once loaded
    """)
    
    st.header("🎵 Morse Code Reference")
    with st.expander("View Complete Morse Code Chart"):
        morse_chart = """
        A: .-    B: -...  C: -.-.  D: -..   E: .
        F: ..-.  G: --.   H: ....  I: ..    J: .---
        K: -.-   L: .-..  M: --    N: -.    O: ---
        P: .--.  Q: --.-  R: .-.   S: ...   T: -
        U: ..-   V: ...-  W: .--   X: -..-  Y: -.--
        Z: --..
        
        0: -----  1: .----  2: ..---  3: ...--  4: ....-
        5: .....  6: -....  7: --...  8: ---..  9: ----.
        
        Space between letters: short pause
        Space between words: / (longer pause)
        """
        st.code(morse_chart)
    
    st.header("🚀 What's New")
    st.success("""
    **Latest Enhancements:**
    - 🤖 AI-powered chord progressions
    - 🎸 Walking bass line generation
    - 📱 Mobile-optimized interface
    - 🎯 Enhanced decoding accuracy
    - 💾 Better file management
    - 🎨 More musical style presets
    """)
