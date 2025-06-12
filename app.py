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

st.set_page_config(
    page_title="🎵 Enhanced Morse Melody Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .preset-button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 20px;
        border-radius: 10px;
        margin: 5px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .preset-button:hover {
        transform: translateY(-2px);
    }
    .music-tip {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4ecdc4;
        margin: 10px 0;
    }
    .scale-info {
        background: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown('<h1 class="main-header">🎵 Enhanced Morse Melody Studio</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create beautiful, musical compositions while encoding secret messages in Morse code</p>', unsafe_allow_html=True)

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
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 10px 0; color: white;">
        <h4 style="margin-top: 0; color: white;">🎧 Enhanced Audio Player</h4>
        <button id="playBtn" onclick="togglePlay()" style="
            background: #ff6b6b; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">▶️ Play</button>
        <button onclick="stopAudio()" style="
            background: rgba(255,255,255,0.2); 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">⏹️ Stop</button>
        <div id="progress" style="
            width: 100%; 
            height: 8px; 
            background: rgba(255,255,255,0.3); 
            border-radius: 4px; 
            margin: 15px 0;
            overflow: hidden;
        ">
            <div id="progressBar" style="
                width: 0%; 
                height: 100%; 
                background: linear-gradient(90deg, #ff6b6b, #feca57); 
                transition: width 0.1s;
                border-radius: 4px;
            "></div>
        </div>
        <span id="timeDisplay" style="color: rgba(255,255,255,0.9);">0:00 / 0:00</span>
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
        const filterNode = audioContext.createBiquadFilter();
        
        oscillator.connect(filterNode);
        filterNode.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'triangle';
        
        // Enhanced audio with filter
        filterNode.type = 'lowpass';
        filterNode.frequency.setValueAtTime(2000, startTime);
        filterNode.Q.setValueAtTime(1, startTime);
        
        const volume = (velocity / 127) * 0.15;
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

# Scale information for educational purposes
SCALE_INFO = {
    'major': "Happy, bright sound. Most familiar Western scale.",
    'minor': "Sad, melancholy sound. Natural minor scale.",
    'pentatonic': "Simple, folk-like sound. Used in many world music traditions.",
    'blues': "Soulful, expressive sound with characteristic 'blue notes'.",
    'dorian': "Medieval sound, neither major nor minor. Used in Celtic music.",
    'mixolydian': "Major scale with a lowered 7th. Common in rock and folk.",
    'lydian': "Dreamy, ethereal sound with raised 4th degree.",
    'phrygian': "Exotic, Spanish/Middle Eastern sound.",
    'harmonic_minor': "Dramatic, classical sound with raised 7th.",
    'melodic_minor': "Jazz favorite with raised 6th and 7th ascending.",
    'whole_tone': "Dreamy, impressionistic sound (think Debussy).",
    'diminished': "Tense, symmetrical scale used in jazz.",
    'japanese': "Traditional Japanese pentatonic scale.",
    'arabic': "Middle Eastern sound with quarter-tone feel.",
    'gypsy': "Exotic, Romanian/Hungarian folk sound."
}

tab1, tab2 = st.tabs(["🎼 Compose & Encode", "🔍 Decode & Analyze"])

# ---------------------- ENCODER TAB ----------------------
with tab1:
    st.header("🎹 Musical Composition Studio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_area(
            "Your Secret Message:", 
            value="Hope is the frequency",
            help="This message will be encoded in the melody line using Morse code",
            height=100
        )
    
    with col2:
        st.markdown("""
        <div class="music-tip">
        <h4>💡 How it works:</h4>
        <p>Your message becomes a beautiful melody using advanced musical AI that follows music theory principles!</p>
        <ul>
        <li>Dots (.) = shorter, lower notes</li>
        <li>Dashes (-) = longer, higher notes</li>
        <li>Phrases follow natural musical arcs</li>
        <li>Scale notes create harmonic consistency</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Musical Style Presets
    st.subheader("🎨 Quick Style Presets")
    st.markdown("*Click a preset to instantly configure all musical settings:*")
    
    preset_cols = st.columns(4)
    
    with preset_cols[0]:
        if st.button("🎹 **Classical Piano**\n*Elegant & Traditional*", use_container_width=True):
            st.session_state.update({
                'tempo': 90, 'melody_inst': 'Piano', 'harmony_inst': 'Strings',
                'bass_inst': 'Cello', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'classic',
                'key_center': 'C'
            })
            st.rerun()
    
    with preset_cols[1]:
        if st.button("🎸 **Folk Acoustic**\n*Warm & Natural*", use_container_width=True):
            st.session_state.update({
                'tempo': 110, 'melody_inst': 'Acoustic Guitar', 'harmony_inst': 'Acoustic Guitar',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'pentatonic', 'chord_prog': 'folk',
                'key_center': 'G'
            })
            st.rerun()
    
    with preset_cols[2]:
        if st.button("🎺 **Jazz Ensemble**\n*Sophisticated & Smooth*", use_container_width=True):
            st.session_state.update({
                'tempo': 125, 'melody_inst': 'Trumpet', 'harmony_inst': 'Electric Piano',
                'bass_inst': 'Electric Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'dorian', 'chord_prog': 'jazz',
                'key_center': 'F'
            })
            st.rerun()
    
    with preset_cols[3]:
        if st.button("🌙 **Ambient Pad**\n*Dreamy & Ethereal*", use_container_width=True):
            st.session_state.update({
                'tempo': 75, 'melody_inst': 'Pad', 'harmony_inst': 'Strings',
                'bass_inst': 'Bass Synth', 'add_harmony': True, 'add_bass': False,
                'add_drums': False, 'scale_type': 'lydian', 'chord_prog': 'modal',
                'key_center': 'D'
            })
            st.rerun()
    
    # Additional preset row
    preset_cols2 = st.columns(4)
    
    with preset_cols2[0]:
        if st.button("🎸 **Blues Rock**\n*Soulful & Gritty*", use_container_width=True):
            st.session_state.update({
                'tempo': 95, 'melody_inst': 'Electric Guitar', 'harmony_inst': 'Electric Piano',
                'bass_inst': 'Electric Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'blues', 'chord_prog': 'blues',
                'key_center': 'E'
            })
            st.rerun()
    
    with preset_cols2[1]:
        if st.button("🌸 **World Music**\n*Exotic & Mystical*", use_container_width=True):
            st.session_state.update({
                'tempo': 100, 'melody_inst': 'Sitar', 'harmony_inst': 'Pad',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'phrygian', 'chord_prog': 'modal',
                'key_center': 'A'
            })
            st.rerun()
    
    with preset_cols2[2]:
        if st.button("🎻 **Orchestra**\n*Grand & Cinematic*", use_container_width=True):
            st.session_state.update({
                'tempo': 80, 'melody_inst': 'Violin', 'harmony_inst': 'String Ensemble',
                'bass_inst': 'Cello', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'harmonic_minor', 'chord_prog': 'classic',
                'key_center': 'D'
            })
            st.rerun()
    
    with preset_cols2[3]:
        if st.button("⚡ **Electronic**\n*Modern & Synthetic*", use_container_width=True):
            st.session_state.update({
                'tempo': 128, 'melody_inst': 'Lead', 'harmony_inst': 'Pad',
                'bass_inst': 'Bass Synth', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'minor', 'chord_prog': 'pop',
                'key_center': 'C'
            })
            st.rerun()
    
    st.markdown("---")
    
    # Enhanced Musical configuration
    st.subheader("🎛️ Advanced Musical Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎵 Core Settings**")
        tempo = st.slider("Tempo (BPM)", 60, 180, st.session_state.get('tempo', 120), 5)
        key_center = st.selectbox("Key Center", list(KEY_PRESETS.keys()), 
                                 index=list(KEY_PRESETS.keys()).index(st.session_state.get('key_center', 'C')))
        
        scale_type = st.selectbox("Musical Scale", list(SCALES.keys()), 
                                 index=list(SCALES.keys()).index(st.session_state.get('scale_type', 'major')))
        
        # Show scale information
        if scale_type in SCALE_INFO:
            st.markdown(f'<div class="scale-info"><small><strong>{scale_type.title()}:</strong> {SCALE_INFO[scale_type]}</small></div>', 
                       unsafe_allow_html=True)
        
    with col2:
        st.markdown("**🎹 Instruments**")
        melody_inst = st.selectbox("Melody Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                  index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('melody_inst', 'Piano')))
        harmony_inst = st.selectbox("Harmony Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                   index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('harmony_inst', 'Strings')))
        bass_inst = st.selectbox("Bass Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('bass_inst', 'Bass')))
    
    with col3:
        st.markdown("**🎶 Arrangement**")
        add_harmony = st.checkbox("Add Harmony Chords", value=st.session_state.get('add_harmony', True),
                                 help="Rich chord progressions that complement the melody")
        add_bass = st.checkbox("Add Bass Line", value=st.session_state.get('add_bass', True),
                              help="Foundation bass notes and patterns")
        add_drums = st.checkbox("Add Rhythm Section", value=st.session_state.get('add_drums', False),
                               help="Drums and percussion for groove")
        
        if add_harmony:
            chord_prog = st.selectbox("Chord Progression", list(CHORD_PROGRESSIONS.keys()), 
                                     index=list(CHORD_PROGRESSIONS.keys()).index(st.session_state.get('chord_prog', 'classic')),
                                     help="Different harmonic progressions for various moods")
        else:
            chord_prog = 'classic'
    
    # Generate button with enhanced styling
    st.markdown("---")
    if st.button("🎵 **Generate Musical Composition**", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("🎼 Composing your musical masterpiece with AI melody generation..."):
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
                    'bass_instrument': INSTRUMENT_PRESETS[bass_inst]
                }
                
                try:
                    midi_path, wav_path, morse_code = generate_enhanced_files_from_text(
                        user_input, **musical_options
                    )
                    
                    if midi_path and os.path.exists(midi_path):
                        st.balloons()  # Celebration!
                        st.success("✅ **Musical Composition Complete!** Your message has been beautifully encoded.")
                        
                        # Display composition info with enhanced styling
                        info_col1, info_col2 = st.columns(2)
                        
                        with info_col1:
                            st.markdown("### 🔤 **Encoded Message**")
                            st.code(user_input.upper(), language=None)
                            st.markdown("### 📻 **Morse Code Pattern**")
                            st.code(morse_code, language=None)
                        
                        with info_col2:
                            st.markdown("### 🎼 **Musical Arrangement**")
                            arrangement_info = [
                                f"🎹 **Melody:** {melody_inst}",
                                f"🎵 **Key:** {key_center} {scale_type.title()}",
                                f"⏱️ **Tempo:** {tempo} BPM"
                            ]
                            if add_harmony:
                                arrangement_info.append(f"🎶 **Harmony:** {harmony_inst}")
                            if add_bass:
                                arrangement_info.append(f"🎸 **Bass:** {bass_inst}")
                            if add_drums:
                                arrangement_info.append("🥁 **Drums:** Standard Kit")
                            
                            for info in arrangement_info:
                                st.markdown(info)
                            
                            # Scale information
                            st.markdown(f"**Scale Character:** {SCALE_INFO.get(scale_type, 'Classic sound')}")
                        
                        # Enhanced Web Audio Player
                        st.markdown("---")
                        st.subheader("🎧 Listen to Your Composition")
                        midi_json = midi_to_json(midi_path)
                        audio_player_html = create_audio_player(midi_json, tempo)
                        st.components.v1.html(audio_player_html, height=180)
                        
                        # Fallback audio player if WAV exists
                        if wav_path and os.path.exists(wav_path):
                            st.markdown("**Alternative player (if needed):**")
                            st.audio(wav_path, format='audio/wav')
                        
                        # Download section with enhanced styling
                        st.markdown("---")
                        st.subheader("📥 Download Your Musical Files")
                        
                        download_col1, download_col2, download_col3 = st.columns(3)
                        
                        with download_col1:
                            with open(midi_path, "rb") as f:
                                midi_bytes = f.read()
                            filename = f"morse_melody_{user_input[:10].replace(' ', '_')}_{scale_type}_{tempo}bpm.mid"
                            st.download_button(
                                "🎼 **Download MIDI File**",
                                midi_bytes,
                                file_name=filename,
                                mime="audio/midi",
                                use_container_width=True,
                                help="MIDI file works in any music software!"
                            )
                        
                        with download_col2:
                            if wav_path and os.path.exists(wav_path):
                                with open(wav_path, "rb") as f:
                                    wav_bytes = f.read()
                                filename = f"morse_melody_{user_input[:10].replace(' ', '_')}_{scale_type}_{tempo}bpm.wav"
                                st.download_button(
                                    "🎵 **Download Audio File**",
                                    wav_bytes,
                                    file_name=filename,
                                    mime="audio/wav",
                                    use_container_width=True,
                                    help="High-quality audio file"
                                )
                            else:
                                st.info("💡 **MIDI files work in:**\n- GarageBand, Logic Pro\n- FL Studio, Ableton\n- MuseScore (free!)")
                        
                        with download_col3:
                            info_text = f"""🎵 MORSE MELODY COMPOSITION
=====================================

📝 Original Message: {user_input}
📻 Morse Code: {morse_code}
🎼 Musical Key: {key_center} {scale_type.title()}
⏱️ Tempo: {tempo} BPM
🎹 Melody: {melody_inst}
🎶 Harmony: {harmony_inst if add_harmony else 'None'}
🎸 Bass: {bass_inst if add_bass else 'None'}
🥁 Drums: {'Yes' if add_drums else 'No'}
🎵 Chord Progression: {chord_prog.title()}

🎨 Scale Character: {SCALE_INFO.get(scale_type, 'Classic sound')}

Generated by Enhanced Morse Melody Studio
Advanced AI Melody Generation System
"""
                            st.download_button(
                                "📋 **Download Info Sheet**",
