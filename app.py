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

st.set_page_config(page_title="Ultra-Realistic Morse Melody Studio", layout="wide")

st.title("🎼 Ultra-Realistic Morse Melody Studio")
st.caption("Create sophisticated, human-like musical compositions while encoding secret messages")

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
    """Create enhanced web audio player with better sound synthesis"""
    audio_html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin: 15px 0; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 15px 0; color: white;">🎧 Professional Audio Player</h4>
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <button id="playBtn" onclick="togglePlay()" style="
                background: linear-gradient(45deg, #ff6b6b, #ee5a52); 
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 25px; 
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(255,107,107,0.4);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">▶️ Play</button>
            <button onclick="stopAudio()" style="
                background: #555; 
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 25px; 
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s ease;
            " onmouseover="this.style.backgroundColor='#666'" onmouseout="this.style.backgroundColor='#555'">⏹️ Stop</button>
            <span id="timeDisplay" style="color: white; font-weight: bold;">0:00 / 0:00</span>
        </div>
        <div id="progress" style="
            width: 100%; 
            height: 8px; 
            background: rgba(255,255,255,0.3); 
            border-radius: 10px; 
            overflow: hidden;
            cursor: pointer;
        " onclick="seekAudio(event)">
            <div id="progressBar" style="
                width: 0%; 
                height: 100%; 
                background: linear-gradient(90deg, #ff6b6b, #ffd93d);
                transition: width 0.1s;
                border-radius: 10px;
            "></div>
        </div>
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
    
    function seekAudio(event) {{
        if (totalDuration > 0) {{
            const rect = event.target.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = clickX / rect.width;
            pauseTime = (percentage * Math.max(...midiData.map(note => note.start + note.duration))) * (60 / tempo);
            
            if (isPlaying) {{
                stopAudio();
                togglePlay();
            }} else {{
                updateProgressDisplay();
            }}
        }}
    }}
    
    function updateProgress() {{
        if (isPlaying && startTime) {{
            const elapsed = (audioContext.currentTime - startTime + pauseTime) * (tempo / 60);
            const maxTime = Math.max(...midiData.map(note => note.start + note.duration));
            const progress = Math.min(elapsed / maxTime * 100, 100);
            
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
    
    function updateProgressDisplay() {{
        const currentTime = pauseTime;
        document.getElementById('timeDisplay').textContent = 
            `${{formatTime(currentTime)}} / ${{formatTime(totalDuration)}}`;
        const maxTime = Math.max(...midiData.map(note => note.start + note.duration)) * (60 / tempo);
        const progress = (pauseTime / maxTime) * 100;
        document.getElementById('progressBar').style.width = progress + '%';
    }}
    
    function createAdvancedOscillator(frequency, startTime, duration, velocity, track) {{
        if (!audioContext) return;
        
        // Create more sophisticated sound based on track
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        const filterNode = audioContext.createBiquadFilter();
        
        // Connect the audio graph
        oscillator.connect(filterNode);
        filterNode.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Configure oscillator based on track (instrument simulation)
        if (track === 0) {{ // Melody - more organic sound
            oscillator.type = 'triangle';
            filterNode.type = 'lowpass';
            filterNode.frequency.value = frequency * 2;
            filterNode.Q.value = 1;
        }} else if (track === 1) {{ // Harmony - warm pad sound
            oscillator.type = 'sawtooth';
            filterNode.type = 'lowpass';
            filterNode.frequency.value = frequency * 1.5;
            filterNode.Q.value = 0.5;
        }} else if (track === 2) {{ // Bass - rich low end
            oscillator.type = 'square';
            filterNode.type = 'lowpass';
            filterNode.frequency.value = frequency * 1.2;
            filterNode.Q.value = 2;
        }} else {{ // Drums - noise-based
            oscillator.type = 'square';
            filterNode.type = 'highpass';
            filterNode.frequency.value = frequency * 0.5;
        }}
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        
        // More natural volume envelope
        const volume = (velocity / 127) * 0.08; // Reduced overall volume
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(volume, startTime + Math.min(0.05, duration * 0.1));
        gainNode.gain.exponentialRampToValueAtTime(Math.max(0.001, volume * 0.3), startTime + duration * 0.7);
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
            
            // Schedule all notes with advanced synthesis
            midiData.forEach(note => {{
                const frequency = midiToFreq(note.note);
                const noteStartTime = audioContext.currentTime + (note.start - pauseTime * (tempo / 60)) * (60 / tempo);
                const duration = note.duration * (60 / tempo);
                
                if (noteStartTime >= audioContext.currentTime) {{
                    const oscillator = createAdvancedOscillator(
                        frequency, noteStartTime, duration, note.velocity, note.track
                    );
                    scheduledNotes.push(oscillator);
                }}
            }});
            
            updateProgress();
        }} else {{
            pauseTime += (audioContext.currentTime - startTime) * (tempo / 60);
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
        
        if (!isPlaying) {{
            updateProgressDisplay();
        }}
    }}
    
    // Initialize display
    document.getElementById('timeDisplay').textContent = `0:00 / ${{formatTime(totalDuration)}}`;
    </script>
    """
    
    return audio_html

tab1, tab2 = st.tabs(["🎼 Compose & Encode", "🔍 Decode & Analyze"])

# ---------------------- ENCODER TAB ----------------------
with tab1:
    st.header("🎹 Professional Musical Composition Studio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_input = st.text_area(
            "Your Secret Message:", 
            value="Revolution starts at dawn",
            help="This message will be encoded using advanced musical algorithms that create human-like compositions"
        )
    
    with col2:
        st.info("🎼 **Enhanced Realism:**\n\nThis version creates sophisticated musical compositions using:\n• Advanced voice leading\n• Musical phrase structure\n• Humanized timing\n• Sophisticated harmony\n• Intelligent bass lines")
    
    # Musical Style Presets with enhanced descriptions
    st.subheader("🎨 Professional Musical Styles")
    style_cols = st.columns(4)
    
    with style_cols[0]:
        if st.button("🎹 Concert Piano", use_container_width=True):
            st.session_state.update({
                'tempo': 72, 'melody_inst': 'Piano', 'harmony_inst': 'Piano',
                'bass_inst': 'Piano', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'classic'
            })
            st.rerun()
    
    with style_cols[1]:
        if st.button("🎸 Singer-Songwriter", use_container_width=True):
            st.session_state.update({
                'tempo': 95, 'melody_inst': 'Acoustic Guitar', 'harmony_inst': 'Acoustic Guitar',
                'bass_inst': 'Acoustic Guitar', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'major', 'chord_prog': 'folk'
            })
            st.rerun()
    
    with style_cols[2]:
        if st.button("🎺 Jazz Ensemble", use_container_width=True):
            st.session_state.update({
                'tempo': 110, 'melody_inst': 'Trumpet', 'harmony_inst': 'Electric Piano',
                'bass_inst': 'Bass', 'add_harmony': True, 'add_bass': True,
                'add_drums': True, 'scale_type': 'dorian', 'chord_prog': 'jazz'
            })
            st.rerun()
    
    with style_cols[3]:
        if st.button("🌌 Cinematic", use_container_width=True):
            st.session_state.update({
                'tempo': 65, 'melody_inst': 'Strings', 'harmony_inst': 'Pad',
                'bass_inst': 'Strings', 'add_harmony': True, 'add_bass': True,
                'add_drums': False, 'scale_type': 'minor', 'chord_prog': 'modern'
            })
            st.rerun()
    
    # Enhanced Musical configuration
    st.subheader("🎛️ Advanced Musical Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🎵 Core Settings**")
        tempo = st.slider("Tempo (BPM)", 50, 200, st.session_state.get('tempo', 110), 5)
        key_center = st.selectbox("Key Center", list(KEY_PRESETS.keys()), index=0)
        scale_type = st.selectbox("Musical Scale", list(SCALES.keys()), 
                                 index=list(SCALES.keys()).index(st.session_state.get('scale_type', 'major')))
        
    with col2:
        st.write("**🎹 Instrumentation**")
        melody_inst = st.selectbox("Lead Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                  index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('melody_inst', 'Piano')))
        harmony_inst = st.selectbox("Harmony Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                   index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('harmony_inst', 'Strings')))
        bass_inst = st.selectbox("Bass Instrument", list(INSTRUMENT_PRESETS.keys()), 
                                index=list(INSTRUMENT_PRESETS.keys()).index(st.session_state.get('bass_inst', 'Bass')))
    
    with col3:
        st.write("**🎶 Arrangement**")
        add_harmony = st.checkbox("Sophisticated Harmony", value=st.session_state.get('add_harmony', True))
        add_bass = st.checkbox("Musical Bass Line", value=st.session_state.get('add_bass', True))
        add_drums = st.checkbox("Realistic Drums", value=st.session_state.get('add_drums', False))
        
        if add_harmony:
            chord_prog = st.selectbox("Harmonic Style", list(CHORD_PROGRESSIONS.keys()), 
                                     index=list(CHORD_PROGRESSIONS.keys()).index(st.session_state.get('chord_prog', 'classic')))
        else:
            chord_prog = 'classic'
    
    # Generate button with enhanced styling
    if st.button("🎼 Generate Professional Composition", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("🎼 Composing with advanced musical AI..."):
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
                    'original_message': user_input
                }

                try:
                    midi_path, wav_path, morse_code = generate_enhanced_files_from_text(
                        user_input, **musical_options
                    )
                    
                    if midi_path and os.path.exists(midi_path):
                        st.success("✅ Professional Composition Complete!")
                        
                        # Enhanced composition info display
                        st.subheader("🎼 Composition Details")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**🔤 Original Message:**")
                            st.code(user_input.upper())
                            st.write("**📻 Morse Encoding:**")
                            st.code(morse_code)
                        
                        with col2:
                            st.write("**🎼 Musical Arrangement:**")
                            arrangement_info = [
                                f"🎹 Lead: {melody_inst}",
                                f"🎵 Key: {key_center} {scale_type.title()}",
                                f"⏱️ Tempo: {tempo} BPM",
                                f"🎶 Scale: {scale_type.title()}"
                            ]
                            if add_harmony:
                                arrangement_info.append(f"🎹 Harmony: {harmony_inst}")
                            if add_bass:
                                arrangement_info.append(f"🎸 Bass: {bass_inst}")
                            if add_drums:
                                arrangement_info.append("🥁 Drums: Professional Kit")
                            
                            for info in arrangement_info:
                                st.write(info)
                        
                        # Enhanced Web Audio Player
                        st.subheader("🎧 Professional Audio Preview")
                        midi_json = midi_to_json(midi_path)
                        audio_player_html = create_audio_player(midi_json, tempo)
                        st.components.v1.html(audio_player_html, height=150)
                        
                        # Show traditional audio player if WAV exists
                        if wav_path and os.path.exists(wav_path):
                            st.write("**Alternative Player (if available):**")
                            st.audio(wav_path, format='audio/wav')
                        
                        # Enhanced download section
                        st.subheader("📥 Download Professional Files")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with open(midi_path, "rb") as f:
                                midi_bytes = f.read()
                            filename = f"professional_morse_{user_input[:10].replace(' ', '_')}_{tempo}bpm.mid"
                            st.download_button(
                                "📄 Download MIDI",
                                midi_bytes,
                                file_name=filename,
                                mime="audio/midi",
                                use_container_width=True
                            )
                        
                        with col2:
                            if wav_path and os.path.exists(wav_path):
                                with open(wav_path, "rb") as f:
                                    wav_bytes = f.read()
                                filename = f"professional_morse_{user_input[:10].replace(' ', '_')}_{tempo}bpm.wav"
                                st.download_button(
                                    "🎵 Download Audio",
                                    wav_bytes,
                                    file_name=filename,
                                    mime="audio/wav",
                                    use_container_width=True
                                )
                            else:
                                st.info("💡 MIDI files work in all professional music software!")
                        
                        with col3:
                            info_text = f"""PROFESSIONAL MORSE COMPOSITION
================================

Original Message: {user_input}
Morse Code: {morse_code}
Musical Key: {key_center} {scale_type}
Tempo: {tempo} BPM
Lead Instrument: {melody_inst}
Harmonic Style: {chord_prog}

Generated by Ultra-Realistic Morse Melody Studio
Advanced Musical AI • Professional Quality
"""
                            st.download_button(
                                "📋 Download Info",
                                info_text,
                                file_name=f"composition_info_{user_input[:10].replace(' ', '_')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                    else:
                        st.error("❌ Error generating composition. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.write("Please check your settings and try again.")
        else:
            st.warning("⚠️ Please enter a message to encode.")

# ---------------------- DECODER TAB ----------------------  
with tab2:
    st.header("🔍 Advanced Message Decoder & Musical Analysis")
    
    uploaded_midi = st.file_uploader(
        "Upload MIDI File for Analysis", 
        type=["mid", "midi"],
        help="Upload any MIDI file to decode hidden messages and analyze musical structure"
    )
    
    if uploaded_midi is not None:
        st.info("🔬 Performing advanced musical analysis...")
        
        try:
            mid = mido.MidiFile(file=uploaded_midi)
            
            # Enhanced MIDI analysis
            ticks_per_beat = mid.ticks_per_beat
            note_events = []
            
            # Track information with better display
            st.subheader("📊 Advanced File Analysis")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tracks", len(mid.tracks))
            with col2:
                st.metric("Resolution", f"{ticks_per_beat} PPQ")
            with col3:
                total_time = sum(msg.time for track in mid.tracks for msg in track)
                st.metric("Total Ticks", f"{total_time:,}")
            with col4:
                estimated_duration = total_time / ticks_per_beat / 2  # Rough estimate
                st.metric("Est. Duration", f"{estimated_duration:.1f}s")
            
            # Extract melody track with better logic
            melody_track = None
            for i, track in enumerate(mid.tracks):
                note_count = sum(1 for msg in track if msg.type in ['note_on', 'note_off'])
                if note_count > 0:
                    melody_track = track
                    st.write(f"🎵 Analyzing track {i} ({note_count} note events)")
                    break
            
            if melody_track:
                # Enhanced note extraction
                current_time = 0
                for msg in melody_track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        note_events.append((msg.note, current_time, "on", msg.velocity))
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        note_events.append((msg.note, current_time, "off", 0))
                
                # Process note durations with enhanced logic
                active_notes = {}
                note_durations = []
                
                for note, time, state, velocity in note_events:
                    if state == "on":
                        active_notes[note] = (time, velocity)
                    elif state == "off" and note in active_notes:
                        start_time, vel = active_notes[note]
                        duration = time - start_time
                        note_durations.append((start_time, duration, note, vel))
                        del active_notes[note]
                
                note_durations.sort()
                
                if note_durations:
                    # Enhanced morse decoding with better algorithm
                    durations = [dur for _, dur, _, _ in note_durations]
                    if durations:
                        min_duration = min(durations)
                        base_unit = min_duration
                        
                        morse_symbols = []
                        current_morse_letter = ""
                        
                        for i, (start_time, duration, note, velocity) in enumerate(note_durations):
                            # Improved dot/dash detection
                            ratio = duration / base_unit
                            if ratio <= 2.0:
                                symbol = "."
                            elif ratio <= 5.0:
                                symbol = "-"
                            else:
                                symbol = "?"
                            
                            current_morse_letter += symbol
                            
                            # Enhanced gap detection for letter/word spacing
                            if i < len(note_durations) - 1:
                                note_end = start_time + duration
                                next_start = note_durations[i + 1][0]
                                gap = next_start - note_end
                                gap_ratio = gap / base_unit
                                
                                # Adaptive thresholds
                                letter_gap_threshold = base_unit * 2.0
                                word_gap_threshold = base_unit * 4.0
                                
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
                        
                        # Display enhanced results
                        morse_display = ""
                        for i, symbol in enumerate(morse_symbols):
                            if symbol == "/":
                                morse_display += " / "
                            else:
                                morse_display += symbol
                                if i < len(morse_symbols) - 1 and morse_symbols[i + 1] != "/":
                                    morse_display += " "
                        
                        st.subheader("📻 Decoded Morse Sequence")
                        st.code(morse_display.strip())
                        
                        # Enhanced text decoding
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
                        if decoded_text.strip():
                            st.success(f"**{decoded_text.strip().upper()}**")
                        else:
                            st.warning("No clear message could be decoded. This may not be a Morse-encoded file.")
                        
                        # Enhanced web audio playback
                        st.subheader("🎧 Advanced Audio Analysis")
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as tmp_file:
                            tmp_file.write(uploaded_midi.getvalue())
                            tmp_midi_path = tmp_file.name
                        
                        uploaded_midi_json = midi_to_json(tmp_midi_path)
                        uploaded_audio_player = create_audio_player(uploaded_midi_json, 120)
                        st.components.v1.html(uploaded_audio_player, height=150)
                        
                        # Clean up
                        try:
                            os.unlink(tmp_midi_path)
                        except:
                            pass
                        
                        # Enhanced detailed analysis
                        with st.expander("🔍 Professional Analysis Report"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**📈 Statistical Analysis:**")
                                st.metric("Total Notes Analyzed", len(note_durations))
                                st.metric("Shortest Duration", f"{min(durations)} ticks")
                                st.metric("Longest Duration", f"{max(durations)} ticks")
                                st.metric("Average Duration", f"{sum(durations)/len(durations):.1f} ticks")
                                
                                # Duration distribution
                                dots = sum(1 for _, dur, _, _ in note_durations if dur/base_unit <= 2.0)
                                dashes = sum(1 for _, dur, _, _ in note_durations if 2.0 < dur/base_unit <= 5.0)
                                st.metric("Dots Detected", dots)
                                st.metric("Dashes Detected", dashes)
                            
                            with col2:
                                st.write("**🎼 Musical Analysis:**")
                                notes_used = sorted(set(note for _, _, note, _ in note_durations))
                                st.write(f"**Note Range:** {min(notes_used)} - {max(notes_used)}")
                                st.write(f"**Pitch Span:** {max(notes_used) - min(notes_used)} semitones")
                                
                                velocities = [vel for _, _, _, vel in note_durations if vel > 0]
                                if velocities:
                                    st.metric("Avg Velocity", f"{sum(velocities)/len(velocities):.1f}")
                                    st.metric("Velocity Range", f"{min(velocities)}-{max(velocities)}")
                            
                            st.write("**🔤 Letter-by-Letter Breakdown:**")
                            for i, word_morse in enumerate(words):
                                if word_morse.strip():
                                    st.write(f"**Word {i+1}:** `{word_morse}`")
                                    letters = word_morse.strip().split(" ")
                                    for letter_morse in letters:
                                        if letter_morse.strip():
                                            decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                            confidence = "✅" if decoded_char != "?" else "❓"
                                            st.write(f"  {confidence} `{letter_morse}` → **{decoded_char}**")
                    else:
                        st.error("❌ No valid note durations found.")
                else:
                    st.error("❌ No musical notes detected in this file.")
            else:
                st.error("❌ No tracks with musical content found.")
        
        except Exception as e:
            st.error(f"❌ Error analyzing file: {str(e)}")
            st.write("This may not be a valid MIDI file or may have an unsupported format.")

# ---------------------- ENHANCED SIDEBAR ----------------------
with st.sidebar:
    st.header("🎼 Professional Features")
    st.write("""
    **🚀 Ultra-Realistic Engine:**
    - Advanced musical phrase generation
    - Sophisticated voice leading algorithms  
    - Humanized timing and expression
    - Professional harmonic progressions
    - Intelligent bass line composition
    
    **🎹 Musical Intelligence:**
    - Message-based musical variety
    - Scale-aware melody generation
    - Context-sensitive chord selection
    - Realistic drum programming
    - Advanced audio synthesis
    
    **🔒 Security Features:**
    - Encoding in melodic structure
    - Undetectable to casual listeners
    - Multiple tracks don't affect message
    - Professional music quality maintains cover
    """)
    
    st.header("🎨 Style Guide")
    st.write("""
    **🎹 Concert Piano:** Sophisticated classical style
    **🎸 Singer-Songwriter:** Intimate, acoustic feel
    **🎺 Jazz Ensemble:** Complex harmony, swing feel  
    **🌌 Cinematic:** Atmospheric, film score quality
    
    **🎵 Scale Personalities:**
    - **Major:** Bright, uplifting
    - **Minor:** Melancholic, dramatic
    - **Dorian:** Jazz, sophisticated
    - **Pentatonic:** Folk, simple
    - **Blues:** Soulful, expressive
    """)
    
    st.header("📻 Advanced Morse Reference")
    with st.expander("Professional Morse Chart"):
        morse_chart = """
        LETTERS:
        A: .-    N: -.    
        B: -...  O: ---   
        C: -.-.  P: .--.  
        D: -..   Q: --.-  
        E: .     R: .-.   
        F: ..-.  S: ...   
        G: --.   T: -     
        H: ....  U: ..-   
        I: ..    V: ...-  
        J: .---  W: .--   
        K: -.-   X: -..-  
        L: .-..  Y: -.--  
        M: --    Z: --..  
        
        NUMBERS:
        1: .----  6: -....
        2: ..---  7: --...
        3: ...--  8: ---..
        4: ....-  9: ----.
        5: .....  0: -----
        """
        st.code(morse_chart)
    
    st.header("🚀 What's Revolutionary")
    st.success("""
    **🧠 AI-Powered Composition:**
    - Message-aware musical variety
    - Advanced harmonic intelligence
    - Human-like phrase structure
    - Professional audio synthesis
    
    **🎧 Studio-Quality Output:**
    - Multi-track arrangements
    - Realistic instrument simulation
    - Professional mixing algorithms
    - Broadcast-ready audio quality
    """)
    
    st.header("💡 Pro Tips")
    st.info("""
    **For Maximum Realism:**
    - Use different scales for different moods
    - Vary tempo based on message urgency
    - Add harmony and bass for full arrangements
    - Export MIDI for professional refinement
    
    **For Your Novel:**
    - Messages stay hidden in musical structure
    - Multiple instruments mask the encoding
    - Professional quality maintains believability
    - Upload to any music platform without detection
    """)

# Add some custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .metric-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
