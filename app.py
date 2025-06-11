import streamlit as st
import mido
import os
import json
import base64
from enhanced_morse_music import (
    generate_enhanced_files_from_text, 
    INSTRUMENT_PRESETS, 
    KEY_PRESETS,
    SCALES,
    CHORD_PROGRESSIONS
)

# Morse code dictionary for decoding
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': '/'
}
REVERSE_MORSE = {v: k for k, v in MORSE_CODE_DICT.items()}

st.set_page_config(page_title="Enhanced Morse Melody Studio", layout="wide")

st.title("🎵 Enhanced Morse Melody Studio")
st.caption("Create rich, musical compositions while encoding secret messages in Morse code")

def midi_to_json(midi_path):
    """Convert MIDI file to JSON for web audio playback"""
    try:
        mid = mido.MidiFile(midi_path)
        notes = []
        
        for i, track in enumerate(mid.tracks):
            current_time = 0
            active_notes = {}
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = {
                        'start': current_time / mid.ticks_per_beat,
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'track': i
                    }
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        note_info = active_notes[msg.note]
                        note_info['duration'] = (current_time / mid.ticks_per_beat) - note_info['start']
                        notes.append(note_info)
                        del active_notes[msg.note]
        
        return json.dumps(notes)
    except:
        return "[]"

def create_audio_player(midi_json_data, tempo=120):
    """Create a web audio player for MIDI data"""
    audio_html = f"""
    <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h4>🎧 Audio Player</h4>
        <button id="playBtn" onclick="togglePlay()" style="
            background: #ff6b6b; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        ">▶️ Play</button>
        <button onclick="stopAudio()" style="
            background: #666; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
        ">⏹️ Stop</button>
        <div id="progress" style="
            width: 100%; 
            height: 10px; 
            background: #ddd; 
            border-radius: 5px; 
            margin: 10px 0;
            overflow: hidden;
        ">
            <div id="progressBar" style="
                width: 0%; 
                height: 100%; 
                background: #ff6b6b; 
                transition: width 0.1s;
            "></div>
        </div>
        <span id="timeDisplay">0:00 / 0:00</span>
    </div>

    <script>
    let audioContext;
    let isPlaying = false;
    let startTime;
    let pauseTime = 0;
    let scheduledNotes = [];
    let totalDuration = 0;
    
    const midiData = {midi_json_data};
    const tempo = {tempo};
    
    // Calculate total duration
    if (midiData.length > 0) {{
        totalDuration = Math.max(...midiData.map(note => note.start + note.duration)) * (60 / tempo);
    }}
    
    function midiToFreq(midiNote) {{
        return 440 * Math.pow(2, (midiNote - 69) / 12);
    }}
    
    function formatTime(seconds) {{
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
    }}
    
    function updateProgress() {{
        if (isPlaying && startTime) {{
            const elapsed = (audioContext.currentTime - startTime + pauseTime) * (tempo / 60);
            const progress = Math.min(elapsed / Math.max(...midiData.map(note => note.start + note.duration)) * 100, 100);
            document.getElementById('progressBar').style.width = progress + '%';
            
            const currentTime = elapsed * (60 / tempo);
            document.getElementById('timeDisplay').textContent = 
                `${{formatTime(currentTime)}} / ${{formatTime(totalDuration)}}`;
            
            if (progress < 100) {{
                requestAnimationFrame(updateProgress);
            }} else {{
                stopAudio();
            }}
        }}
    }}
    
    function playNote(frequency, startTime, duration, velocity = 80) {{
        if (!audioContext) return;
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'triangle';
        
        const volume = (velocity / 127) * 0.1;
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
        
        return oscillator;
    }}
    
    async function togglePlay() {{
        if (!audioContext) {{
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }}
        
        if (audioContext.state === 'suspended') {{
            await audioContext.resume();
        }}
        
        if (!isPlaying) {{
            startTime = audioContext.currentTime;
            isPlaying = true;
            document.getElementById('playBtn').innerHTML = '⏸️ Pause';
            
            // Schedule all notes
            midiData.forEach(note => {{
                const frequency = midiToFreq(note.note);
                const startTime = audioContext.currentTime + (note.start - pauseTime) * (60 / tempo);
                const duration = note.duration * (60 / tempo);
                
                if (startTime >= audioContext.currentTime) {{
                    const oscillator = playNote(frequency, startTime, duration, note.velocity);
                    scheduledNotes.push(oscillator);
                }}
            }});
            
            updateProgress();
        }} else {{
            pauseTime += audioContext.currentTime - startTime;
            stopAudio();
        }}
    }}
    
    function stopAudio() {{
        isPlaying = false;
        document.getElementById('playBtn').innerHTML = '▶️ Play';
        
        scheduledNotes.forEach(oscillator => {{
            try {{
                oscillator.stop();
            }} catch(e) {{}}
        }});
        scheduledNotes = [];
        
        pauseTime = 0;
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('timeDisplay').textContent = `0:00 / ${{formatTime(totalDuration)}}`;
    }}
    
    // Initialize display
    document.getElementById('timeDisplay').textContent = `0:00 / ${{formatTime(totalDuration)}}`;
    </script>
    """
    
    return audio_html

tab1, tab2 = st.tabs(["🎼 Compose & Encode", "🔍 Decode & Analyze"])

# ---------------------- ENCODER TAB ----------------------
with tab1:
    st.header("🎹 Musical Composition Studio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_area(
            "Your Secret Message:", 
            value="Hope is the frequency",
            help="This message will be encoded in the melody line using Morse code"
        )
    
    with col2:
        st.info("💡 **How it works:**\nYour message becomes the melody while harmony, bass, and rhythm create a full musical arrangement!")
    
    # Musical Style Presets
    st.subheader("🎨 Musical Style Presets")
    style_cols = st.columns(4)
    
    with style_cols[0]:
        if st.button("🎹 Piano Ballad", use_container_width=True):
            st.session_state.update({
                'tempo': 80, 'melody_inst': 'Piano', 'harmony_inst': 'Strings',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'classic'
            })
            st.rerun()
    
    with style_cols[1]:
        if st.button("🎸 Folk Song", use_container_width=True):
            st.session_state.update({
                'tempo': 100, 'melody_inst': 'Acoustic Guitar', 'harmony_inst': 'Acoustic Guitar',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'folk'
            })
            st.rerun()
    
    with style_cols[2]:
        if st.button("🎺 Jazz Standard", use_container_width=True):
            st.session_state.update({
                'tempo': 120, 'melody_inst': 'Trumpet', 'harmony_inst': 'Electric Piano',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'major', 'chord_prog': 'pop'
            })
            st.rerun()
    
    with style_cols[3]:
        if st.button("🌙 Ambient", use_container_width=True):
            st.session_state.update({
                'tempo': 70, 'melody_inst': 'Pad', 'harmony_inst': 'Strings',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': False,
                'add_drums': False, 'scale_type': 'minor', 'chord_prog': 'minor'
            })
            st.rerun()
    
    # Musical configuration
    st.subheader("🎛️ Musical Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🎵 Basic Settings**")
        tempo = st.slider("Tempo (BPM)", 60, 180, st.session_state.get('tempo', 120), 5)
        key_center = st.selectbox("Key Center", list(KEY_PRESETS.keys()), index=0)
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
        add_harmony = st.checkbox("Add Harmony Chords", value=st.session_state.get('add_harmony', True))
        add_bass = st.checkbox("Add Bass Line", value=st.session_state.get('add_bass', True))
        add_drums = st.checkbox("Add Drum Track", value=st.session_state.get('add_drums', False))
        
        if add_harmony:
            chord_prog = st.selectbox("Chord Progression", list(CHORD_PROGRESSIONS.keys()), 
                                     index=list(CHORD_PROGRESSIONS.keys()).index(st.session_state.get('chord_prog', 'classic')))
        else:
            chord_prog = 'classic'
    
    # Generate button
    if st.button("🎵 Generate Musical Composition", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("🎼 Composing your musical masterpiece..."):
                musical_options = {
    'tempo': settings['tempo'],
    'key_root': KEY_PRESETS['C'],
    'scale_type': settings['scale_type'],
    'add_harmony': settings['add_harmony'],
    'add_bass': settings['add_bass'],
    'add_drums': settings['add_drums'],
    'chord_progression': settings['chord_prog'],
    'melody_instrument': INSTRUMENT_PRESETS[settings['melody_inst']],
    'harmony_instrument': INSTRUMENT_PRESETS[settings['harmony_inst']],
    'bass_instrument': INSTRUMENT_PRESETS[settings['bass_inst']],
    'style': preset,  # ADD THIS LINE
    'original_message': user_input  # ADD THIS LINE
}

try:
    midi_path, wav_path, morse_code = generate_enhanced_files_from_text(
        user_input, **musical_options
    )
                    
                    if midi_path and os.path.exists(midi_path):
                        st.success("✅ Musical Composition Complete!")
                        
                        # Display composition info
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**🔤 Encoded Message:**")
                            st.code(user_input.upper())
                            st.write("**📻 Morse Code:**")
                            st.code(morse_code)
                        
                        with col2:
                            st.write("**🎼 Musical Arrangement:**")
                            arrangement_info = [
                                f"🎹 Melody: {melody_inst}",
                                f"🎵 Key: {key_center} {scale_type}",
                                f"⏱️ Tempo: {tempo} BPM"
                            ]
                            if add_harmony:
                                arrangement_info.append(f"🎶 Harmony: {harmony_inst}")
                            if add_bass:
                                arrangement_info.append(f"🎸 Bass: {bass_inst}")
                            if add_drums:
                                arrangement_info.append("🥁 Drums: Standard Kit")
                            
                            for info in arrangement_info:
                                st.write(info)
                        
                        # Web Audio Player
                        st.subheader("🎧 Listen to Your Composition")
                        midi_json = midi_to_json(midi_path)
                        audio_player_html = create_audio_player(midi_json, tempo)
                        st.components.v1.html(audio_player_html, height=200)
                        
                        # Also show traditional audio player if WAV exists
                        if wav_path and os.path.exists(wav_path):
                            st.write("**Or use the built-in audio player:**")
                            st.audio(wav_path, format='audio/wav')
                        
                        # Download buttons
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
                            if wav_path and os.path.exists(wav_path):
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
                            else:
                                st.info("💡 MIDI files work in GarageBand, Logic, FL Studio, and many free music apps!")
                        
                        with col3:
                            info_text = f"""MORSE MELODY COMPOSITION
=========================

Original Message: {user_input}
Morse Code: {morse_code}
Musical Key: {key_center} {scale_type}
Tempo: {tempo} BPM

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

# ---------------------- DECODER TAB ----------------------
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
            
            # MIDI analysis
            ticks_per_beat = mid.ticks_per_beat
            note_events = []
            
            # Track information
            st.subheader("📊 MIDI File Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Number of Tracks", len(mid.tracks))
            with col2:
                st.metric("Ticks Per Beat", ticks_per_beat)
            with col3:
                total_time = sum(msg.time for track in mid.tracks for msg in track)
                st.metric("Total Ticks", total_time)
            
            # Extract melody track
            melody_track = None
            for i, track in enumerate(mid.tracks):
                has_notes = any(msg.type in ['note_on', 'note_off'] for msg in track)
                if has_notes:
                    melody_track = track
                    st.write(f"🎵 Using track {i} for melody analysis")
                    break
            
            if melody_track:
                # Extract note events
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
                    # Decode morse
                    durations = [dur for _, dur in note_durations]
                    min_duration = min(durations)
                    base_unit = min_duration
                    
                    morse_symbols = []
                    current_morse_letter = ""
                    
                    for i, (start_time, duration) in enumerate(note_durations):
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
                    
                    # Display results
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
                    
                    for word_morse in words:
                        letters = word_morse.strip().split(" ")
                        word_text = ""
                        for letter_morse in letters:
                            if letter_morse.strip():
                                decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                word_text += decoded_char
                        if word_text:
                            decoded_text += word_text + " "
                    
                    st.subheader("🎯 Hidden Message Revealed")
                    st.success(f"**{decoded_text.strip().upper()}**")
                    
                    # Web audio playback for uploaded file too
                    st.subheader("🎧 Listen to Uploaded Composition")
                    # Save uploaded file temporarily
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as tmp_file:
                        tmp_file.write(uploaded_midi.getvalue())
                        tmp_midi_path = tmp_file.name
                    
                    uploaded_midi_json = midi_to_json(tmp_midi_path)
                    uploaded_audio_player = create_audio_player(uploaded_midi_json, 120)  # Default tempo
                    st.components.v1.html(uploaded_audio_player, height=200)
                    
                    # Clean up temp file
                    try:
                        os.unlink(tmp_midi_path)
                    except:
                        pass
                    
                    # Detailed analysis
                    with st.expander("🔍 Detailed Analysis"):
                        st.write("**Note Statistics:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Notes", len(note_durations))
                        with col2:
                            st.metric("Shortest Note", f"{min(durations)} ticks")
                        with col3:
                            st.metric("Longest Note", f"{max(durations)} ticks")
                        
                        st.write("**Letter-by-letter Breakdown:**")
                        for i, word_morse in enumerate(words):
                            st.write(f"**Word {i+1}:** `{word_morse}`")
                            letters = word_morse.strip().split(" ")
                            for letter_morse in letters:
                                if letter_morse.strip():
                                    decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                    st.write(f"  `{letter_morse}` → **{decoded_char}**")
                else:
                    st.error("❌ No notes found in the melody track.")
            else:
                st.error("❌ No tracks with musical notes found in this MIDI file.")
        
        except Exception as e:
            st.error(f"❌ Error analyzing MIDI file: {str(e)}")

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.header("ℹ️ About This Tool")
    st.write("""
    This enhanced Morse melody studio allows you to:
    
    **🎵 Compose:**
    - Encode secret messages in musical melodies
    - Add harmony, bass lines, and drums
    - Choose from various instruments and scales
    - Control tempo and musical style
    
    **🔍 Decode:**
    - Upload MIDI files to reveal hidden messages
    - Analyze musical structure
    - View detailed morse code breakdown
    
    **🎼 Musical Features:**
    - Multiple instrument tracks
    - Chord progressions and harmony
    - Bass lines with musical patterns
    - Optional drum tracks
    - Multiple musical scales
    - Customizable tempo and key
    
    **🔒 Security:**
    - Messages are encoded in the melody timing
    - Additional musical elements don't affect the message
    - Only those who know the encoding can decode
    """)
    
    st.header("🎹 Quick Tips")
    st.write("""
    **For Best Results:**
    - Keep messages concise for better musical flow
    - Try different scales for various moods
    - Use harmony and bass for richer sound
    - Experiment with different instruments
    
    **Preset Suggestions:**
    - 🎹 **Piano Ballad**: Emotional, slow pieces
    - 🎸 **Folk Song**: Simple, acoustic feel  
    - 🎺 **Jazz Standard**: Complex, sophisticated
    - 🌙 **Ambient**: Atmospheric, spacey
    """)
    
    st.header("🎵 Morse Code Reference")
    with st.expander("View Morse Code Chart"):
        morse_chart = """
        A: .-    B: -...  C: -.-.  D: -..   E: .
        F: ..-.  G: --.   H: ....  I: ..    J: .---
        K: -.-   L: .-..  M: --    N: -.    O: ---
        P: .--.  Q: --.-  R: .-.   S: ...   T: -
        U: ..-   V: ...-  W: .--   X: -..-  Y: -.--
        Z: --..
        
        0: -----  1: .----  2: ..---  3: ...--  4: ....-
        5: .....  6: -....  7: --...  8: ---..  9: ----.
        """
        st.code(morse_chart)
    
    st.header("💡 Platform Notes")
    st.info("""
    **Enhanced Audio Playback:**
    - Web Audio API creates real-time synthesis
    - Works on all modern browsers
    - No additional software required
    - High-quality sound generation
    
    MIDI files also work in any music software!
    """)
    
    st.header("🚀 What's New")
    st.success("""
    **Enhanced Features:**
    - 🎧 **Web Audio Playback** - Listen in any browser
    - Multiple musical instrument tracks
    - Chord progressions and harmony
    - Bass lines with musical patterns
    - Customizable tempo and keys
    - Multiple musical scales
    - Cloud deployment ready
    """)
