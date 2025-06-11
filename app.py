import streamlit as st
import base64
import mido
from morse_music import generate_files_from_text

# Morse code dictionary
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

st.set_page_config(page_title="Morse Melody Encoder & Player", layout="centered")
st.title("🎵 Morse Melody Encoder & Player")

tab1, tab2 = st.tabs(["🔐 Encode", "🔓 Decode"])

# ---------------------- ENCODER TAB ----------------------
with tab1:
    st.write("Turn your messages into beautiful, encrypted Morse code music.")
    user_input = st.text_area("Enter your message:", value="Hope is the frequency")

    if st.button("Generate Music"):
        with st.spinner("Encoding your message into music..."):
            midi_path, wav_path, morse_code = generate_files_from_text(user_input)

            if midi_path and wav_path:
                st.success("✅ Morse Code Melody Generated!")
                st.write(f"**Morse Code:** `{morse_code}`")
                st.audio(wav_path)

                with open(midi_path, "rb") as f:
                    midi_bytes = f.read()
                with open(wav_path, "rb") as f:
                    wav_bytes = f.read()

                st.download_button("Download MIDI", midi_bytes, file_name="message.mid")
                st.download_button("Download WAV", wav_bytes, file_name="message.wav")
            else:
                st.error("Something went wrong generating the files.")

# ---------------------- DECODER TAB ----------------------
with tab2:
    st.write("Upload a musical Morse melody (MIDI) and decode it back into text.")

    uploaded_midi = st.file_uploader("Upload MIDI File", type=["mid", "midi"])

    if uploaded_midi is not None:
        st.info("Analyzing uploaded MIDI...")

        try:
            mid = mido.MidiFile(file=uploaded_midi)
            
            # Get the ticks per beat to convert timing properly
            ticks_per_beat = mid.ticks_per_beat
            
            current_time = 0
            note_events = []

            # Extract all note events with proper timing
            for msg in mid:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_events.append((msg.note, current_time, "on"))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_events.append((msg.note, current_time, "off"))

            # Pair note_on with note_off events
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

            # Sort by start time
            note_durations.sort()

            if not note_durations:
                st.error("No notes found in MIDI file.")
            else:
                # Convert timing to match encoder parameters
                # Your encoder uses duration_unit = 0.25 (quarter note)
                # At 120 BPM: quarter note = 0.5 seconds
                # We need to convert MIDI ticks to seconds
                
                # Calculate base duration unit from the shortest notes
                durations = [dur for _, dur in note_durations]
                min_duration = min(durations)
                
                # Estimate the base unit (should be around dot duration)
                base_unit = min_duration
                
                # Build morse code string
                morse_symbols = []
                current_morse_letter = ""
                
                for i, (start_time, duration) in enumerate(note_durations):
                    # Determine if this is a dot or dash based on duration
                    if duration <= base_unit * 1.5:  # Allow some tolerance
                        symbol = "."
                    elif duration <= base_unit * 4:  # Dash should be ~3x dot duration
                        symbol = "-"
                    else:
                        symbol = "?"  # Unknown duration
                    
                    current_morse_letter += symbol
                    
                    # Calculate gap to next note (if there is one)
                    if i < len(note_durations) - 1:
                        note_end = start_time + duration
                        next_start = note_durations[i + 1][0]
                        gap = next_start - note_end
                        
                        # Gap thresholds based on your encoder:
                        # - Intra-symbol gap: duration_unit (same as dot)
                        # - Letter gap: duration_unit * 3
                        # - Word gap: duration_unit * 7
                        
                        letter_gap_threshold = base_unit * 2.5  # Between letters
                        word_gap_threshold = base_unit * 5.5    # Between words
                        
                        if gap >= word_gap_threshold:
                            # End of word
                            if current_morse_letter:
                                morse_symbols.append(current_morse_letter)
                                current_morse_letter = ""
                            morse_symbols.append("/")  # Word separator
                        elif gap >= letter_gap_threshold:
                            # End of letter
                            if current_morse_letter:
                                morse_symbols.append(current_morse_letter)
                                current_morse_letter = ""
                    else:
                        # Last note - add the final letter
                        if current_morse_letter:
                            morse_symbols.append(current_morse_letter)

                # Clean up the morse symbols and create display string
                morse_display = ""
                for i, symbol in enumerate(morse_symbols):
                    if symbol == "/":
                        morse_display += " / "
                    else:
                        morse_display += symbol
                        if i < len(morse_symbols) - 1 and morse_symbols[i + 1] != "/":
                            morse_display += " "

                st.write(f"**Raw Morse:** `{morse_display.strip()}`")

                # Decode the Morse to text
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

                st.success("🎯 Decoded Message:")
                st.code(decoded_text.strip().upper())
                
                # Show individual letter decoding for debugging
                with st.expander("🔍 Letter-by-letter breakdown"):
                    words = morse_display.strip().split(" / ")
                    for i, word_morse in enumerate(words):
                        st.write(f"**Word {i+1}:** `{word_morse}`")
                        letters = word_morse.strip().split(" ")
                        for letter_morse in letters:
                            if letter_morse.strip():
                                decoded_char = REVERSE_MORSE.get(letter_morse.strip(), "?")
                                st.write(f"  `{letter_morse}` → {decoded_char}")

        except Exception as e:
            st.error(f"Error reading MIDI file: {e}")
            st.write("Please make sure you uploaded a valid MIDI file generated by this tool.")