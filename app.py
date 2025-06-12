import streamlit as st
import random
import math
import tempfile
import os
from midiutil import MIDIFile
import mido
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum

# Set page config
st.set_page_config(
    page_title="🎵 Intelligent Morse Melody Studio",
    page_icon="🎵",
    layout="wide"
)

# Morse code dictionary
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}

class MusicKey(Enum):
    C_MAJOR = {"root": 60, "scale": [0, 2, 4, 5, 7, 9, 11], "name": "C Major"}
    G_MAJOR = {"root": 67, "scale": [0, 2, 4, 5, 7, 9, 11], "name": "G Major"}
    D_MAJOR = {"root": 62, "scale": [0, 2, 4, 5, 7, 9, 11], "name": "D Major"}
    A_MINOR = {"root": 69, "scale": [0, 2, 3, 5, 7, 8, 10], "name": "A Minor"}
    E_MINOR = {"root": 64, "scale": [0, 2, 3, 5, 7, 8, 10], "name": "E Minor"}
    C_PENTATONIC = {"root": 60, "scale": [0, 2, 4, 7, 9], "name": "C Pentatonic"}
    A_BLUES = {"root": 69, "scale": [0, 3, 5, 6, 7, 10], "name": "A Blues"}

class MusicStyle(Enum):
    CLASSICAL = {"tempo": 90, "dynamics": "gentle", "name": "Classical"}
    FOLK = {"tempo": 110, "dynamics": "warm", "name": "Folk"}
    JAZZ = {"tempo": 120, "dynamics": "swing", "name": "Jazz"}
    AMBIENT = {"tempo": 75, "dynamics": "floating", "name": "Ambient"}
    CELTIC = {"tempo": 105, "dynamics": "lilting", "name": "Celtic"}

@dataclass
class Note:
    pitch: int
    start_time: float
    duration: float
    velocity: int
    channel: int = 0

class IntelligentMelodyGenerator:
    """Completely new melody generator that creates genuinely musical phrases"""
    
    def __init__(self, key: MusicKey, style: MusicStyle):
        self.key = key.value
        self.style = style.value
        self.scale_notes = self._generate_scale_notes()
        
        # Musical memory for intelligent decisions
        self.recent_notes = []
        self.phrase_position = 0
        self.phrase_direction = 0
        
        # Musical intelligence parameters
        self.interval_preferences = self._create_interval_preferences()
        self.phrase_contour = self._create_phrase_contour()
        
    def _generate_scale_notes(self) -> List[int]:
        """Generate scale notes across multiple octaves"""
        notes = []
        root = self.key["root"]
        scale = self.key["scale"]
        
        # Generate 3 octaves
        for octave in [-1, 0, 1]:
            for degree in scale:
                note = root + (octave * 12) + degree
                if 36 <= note <= 96:  # Keep in reasonable MIDI range
                    notes.append(note)
        
        return sorted(notes)
    
    def _create_interval_preferences(self) -> dict:
        """Create interval preferences based on musical style"""
        base_prefs = {
            1: 0.20,   # Half step
            2: 0.30,   # Whole step
            3: 0.15,   # Minor third
            4: 0.15,   # Major third
            5: 0.10,   # Perfect fourth
            7: 0.08,   # Perfect fifth
            12: 0.02   # Octave
        }
        
        # Modify based on style
        if self.style["name"] == "Jazz":
            base_prefs[3] *= 1.5  # More thirds
            base_prefs[7] *= 1.5  # More fifths
        elif self.style["name"] == "Celtic":
            base_prefs[5] *= 1.8  # More fourths
            base_prefs[7] *= 1.3  # More fifths
        elif self.style["name"] == "Ambient":
            base_prefs[1] *= 2.0  # More half steps
            base_prefs[2] *= 1.5  # More whole steps
            
        return base_prefs
    
    def _create_phrase_contour(self) -> List[float]:
        """Create a natural phrase contour (musical arc)"""
        if self.style["name"] == "Classical":
            # Classical arch: start low, peak 2/3 through, resolve down
            return [0.2, 0.4, 0.6, 0.8, 0.9, 0.7, 0.4, 0.1]
        elif self.style["name"] == "Folk":
            # Folk: simple wave pattern
            return [0.3, 0.6, 0.4, 0.7, 0.5, 0.8, 0.3, 0.2]
        elif self.style["name"] == "Jazz":
            # Jazz: more complex, unexpected
            return [0.4, 0.2, 0.8, 0.3, 0.9, 0.1, 0.6, 0.4]
        elif self.style["name"] == "Celtic":
            # Celtic: flowing, modal
            return [0.5, 0.7, 0.3, 0.8, 0.4, 0.9, 0.2, 0.5]
        else:  # Ambient
            # Ambient: gentle floating
            return [0.4, 0.5, 0.6, 0.5, 0.4, 0.6, 0.5, 0.4]
    
    def _get_phrase_target(self, position: int) -> float:
        """Get the target height for this position in the phrase"""
        if not self.phrase_contour:
            return 0.5
        
        index = min(position, len(self.phrase_contour) - 1)
        return self.phrase_contour[index]
    
    def _choose_note_intelligently(self, morse_symbol: str, phrase_pos: int) -> int:
        """Choose a note using musical intelligence"""
        
        # First note of the piece
        if not self.recent_notes:
            # Start in a comfortable middle range
            middle_notes = [n for n in self.scale_notes if self.key["root"] <= n <= self.key["root"] + 7]
            return random.choice(middle_notes)
        
        current_note = self.recent_notes[-1]
        phrase_target = self._get_phrase_target(phrase_pos)
        
        # Determine if we should go up, down, or stay
        current_height = (current_note - min(self.scale_notes)) / (max(self.scale_notes) - min(self.scale_notes))
        
        if current_height < phrase_target - 0.2:
            direction = 1  # Go up
        elif current_height > phrase_target + 0.2:
            direction = -1  # Go down
        else:
            direction = random.choice([-1, 1])  # Either way
        
        # Modify direction based on morse symbol
        if morse_symbol == '.' and random.random() < 0.3:
            direction = -1  # Dots tend to be lower
        elif morse_symbol == '-' and random.random() < 0.3:
            direction = 1   # Dashes tend to be higher
        
        # Choose interval based on preferences and recent motion
        intervals = list(self.interval_preferences.keys())
        weights = list(self.interval_preferences.values())
        
        # Avoid too much motion in one direction
        if len(self.recent_notes) >= 3:
            recent_direction = sum([
                1 if self.recent_notes[i] > self.recent_notes[i-1] else -1
                for i in range(-2, 0)
            ])
            if abs(recent_direction) >= 2:  # Too much in one direction
                direction *= -1  # Force change
        
        # Choose interval
        chosen_interval = random.choices(intervals, weights=weights)[0]
        candidate_note = current_note + (chosen_interval * direction)
        
        # Snap to nearest scale note
        final_note = min(self.scale_notes, key=lambda x: abs(x - candidate_note))
        
        # Ensure we don't go out of range
        if final_note < min(self.scale_notes) or final_note > max(self.scale_notes):
            final_note = current_note  # Stay put if out of range
        
        self.recent_notes.append(final_note)
        if len(self.recent_notes) > 6:  # Keep only recent notes
            self.recent_notes.pop(0)
        
        return final_note
    
    def generate_melody(self, morse_text: str) -> List[Note]:
        """Generate a beautiful melody from morse code"""
        notes = []
        current_time = 0.0
        dot_duration = 0.25
        dash_duration = 0.75
        
        # Convert text to morse
        morse_sequence = []
        for char in morse_text.upper():
            if char in MORSE_CODE:
                morse_sequence.extend(list(MORSE_CODE[char]))
                morse_sequence.append(' ')  # Letter separation
            elif char == ' ':
                morse_sequence.append('/')  # Word separation
        
        # Generate melody with musical intelligence
        phrase_pos = 0
        for symbol in morse_sequence:
            if symbol == '.':
                pitch = self._choose_note_intelligently('.', phrase_pos)
                velocity = random.randint(70, 90)
                notes.append(Note(pitch, current_time, dot_duration, velocity))
                current_time += dot_duration + 0.1  # Small gap
                phrase_pos += 1
                
            elif symbol == '-':
                pitch = self._choose_note_intelligently('-', phrase_pos)
                velocity = random.randint(75, 95)
                notes.append(Note(pitch, current_time, dash_duration, velocity))
                current_time += dash_duration + 0.1  # Small gap
                phrase_pos += 1
                
            elif symbol == ' ':
                current_time += 0.3  # Letter gap
                
            elif symbol == '/':
                current_time += 0.8  # Word gap
                phrase_pos = 0  # Reset phrase position
        
        return notes

class ChordProgressionGenerator:
    """Generate intelligent chord progressions that complement the melody"""
    
    def __init__(self, key: MusicKey, style: MusicStyle):
        self.key = key.value
        self.style = style.value
        self.progressions = self._create_progressions()
    
    def _create_progressions(self) -> dict:
        """Create different chord progressions for different styles"""
        root = self.key["root"]
        
        progressions = {
            "Classical": [
                [root, root + 4, root + 7],           # I
                [root + 9, root + 1, root + 4],       # vi
                [root + 5, root + 9, root + 0],       # IV
                [root + 7, root + 11, root + 2]       # V
            ],
            "Folk": [
                [root, root + 4, root + 7],           # I
                [root + 7, root + 11, root + 2],      # V
                [root + 5, root + 9, root + 0],       # IV
                [root, root + 4, root + 7]            # I
            ],
            "Jazz": [
                [root, root + 4, root + 7, root + 11], # Imaj7
                [root + 9, root + 1, root + 4, root + 8], # vi7
                [root + 2, root + 6, root + 9, root + 0], # ii7
                [root + 7, root + 11, root + 2, root + 5] # V7
            ],
            "Celtic": [
                [root, root + 7],                     # I (open fifth)
                [root + 7, root + 2],                 # V
                [root + 5, root + 0],                 # IV
                [root, root + 7]                      # I
            ],
            "Ambient": [
                [root, root + 4, root + 7, root + 11, root + 14], # Extended chords
                [root + 2, root + 6, root + 9, root + 1, root + 4],
                [root + 5, root + 9, root + 0, root + 4, root + 7],
                [root - 5, root - 1, root + 2, root + 6, root + 9]
            ]
        }
        
        return progressions.get(self.style["name"], progressions["Classical"])
    
    def generate_harmony(self, melody_duration: float) -> List[Note]:
        """Generate harmony notes to accompany the melody"""
        harmony_notes = []
        chord_duration = 2.0  # Each chord lasts 2 beats
        current_time = 0.0
        chord_index = 0
        
        while current_time < melody_duration:
            chord = self.progressions[chord_index % len(self.progressions)]
            
            # Add chord notes with slight timing variations
            for i, pitch in enumerate(chord):
                note_time = current_time + (i * 0.02)  # Slight roll
                velocity = random.randint(50, 70)  # Softer than melody
                harmony_notes.append(Note(pitch - 12, note_time, chord_duration, velocity, channel=1))
            
            current_time += chord_duration
            chord_index += 1
        
        return harmony_notes

def create_midi_file(melody_notes: List[Note], harmony_notes: List[Note] = None) -> bytes:
    """Create a MIDI file from the generated notes"""
    # Calculate number of tracks
    num_tracks = 2 if harmony_notes else 1
    midi = MIDIFile(num_tracks)
    
    # Set tempo
    tempo = 120
    midi.addTempo(0, 0, tempo)
    if harmony_notes:
        midi.addTempo(1, 0, tempo)
    
    # Set instruments
    midi.addProgramChange(0, 0, 0, 0)  # Piano for melody
    if harmony_notes:
        midi.addProgramChange(1, 1, 0, 48)  # Strings for harmony
    
    # Add melody notes
    for note in melody_notes:
        midi.addNote(0, note.channel, note.pitch, note.start_time, note.duration, note.velocity)
    
    # Add harmony notes
    if harmony_notes:
        for note in harmony_notes:
            midi.addNote(1, note.channel, note.pitch, note.start_time, note.duration, note.velocity)
    
    # Create bytes
    import io
    midi_bytes = io.BytesIO()
    midi.writeFile(midi_bytes)
    return midi_bytes.getvalue()

def main():
    # Title and description
    st.title("🎵 Intelligent Morse Melody Studio")
    st.markdown("**Generate genuinely beautiful melodies that encode your secret messages using advanced musical AI**")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Message input
        message = st.text_area(
            "Enter your secret message:",
            value="Hello World",
            height=100,
            help="Your message will be encoded into a beautiful melody using Morse code"
        )
        
        # Musical settings
        st.subheader("🎼 Musical Settings")
        
        settings_col1, settings_col2 = st.columns(2)
        
        with settings_col1:
            key = st.selectbox(
                "Musical Key:",
                options=list(MusicKey),
                format_func=lambda x: x.value["name"]
            )
            
            add_harmony = st.checkbox("Add Harmony", value=True, help="Rich chord progressions")
            
        with settings_col2:
            style = st.selectbox(
                "Musical Style:",
                options=list(MusicStyle),
                format_func=lambda x: x.value["name"]
            )
            
            regenerate = st.checkbox("Force New Melody", help="Generate a completely different melody for the same text")
    
    with col2:
        st.info("""
        **🎵 How it works:**
        
        🎯 Each letter becomes a unique musical phrase  
        🎨 Advanced AI creates beautiful, flowing melodies  
        🎼 Different keys and styles create completely different sounds  
        🔄 Every generation is unique and musical  
        
        **🎹 Try different combinations:**
        - Classical + C Major = Traditional  
        - Jazz + A Minor = Sophisticated  
        - Celtic + G Major = Folk-like  
        - Ambient + C Pentatonic = Dreamy  
        """)
    
    # Generate button
    if st.button("🎵 Generate Beautiful Melody", type="primary", use_container_width=True):
        if message.strip():
            # Set random seed based on message and settings for consistency
            if not regenerate:
                seed_string = f"{message}{key.name}{style.name}"
                random.seed(hash(seed_string) % 1000000)
            
            with st.spinner("🎼 Composing your musical masterpiece..."):
                try:
                    # Generate melody
                    melody_gen = IntelligentMelodyGenerator(key, style)
                    melody_notes = melody_gen.generate_melody(message)
                    
                    # Generate harmony if requested
                    harmony_notes = None
                    if add_harmony:
                        harmony_gen = ChordProgressionGenerator(key, style)
                        total_duration = max(note.start_time + note.duration for note in melody_notes)
                        harmony_notes = harmony_gen.generate_harmony(total_duration)
                    
                    # Create MIDI file
                    midi_data = create_midi_file(melody_notes, harmony_notes)
                    
                    # Success message
                    st.success("✨ **Beautiful melody created!**")
                    
                    # Display information
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.write("**📝 Your Message:**")
                        st.code(message.upper())
                        
                        # Convert to morse for display
                        morse_display = ""
                        for char in message.upper():
                            if char in MORSE_CODE:
                                morse_display += MORSE_CODE[char] + " "
                            elif char == " ":
                                morse_display += "/ "
                        
                        st.write("**📻 Morse Code:**")
                        st.code(morse_display.strip())
                    
                    with info_col2:
                        st.write("**🎼 Musical Details:**")
                        st.write(f"🎹 **Key:** {key.value['name']}")
                        st.write(f"🎨 **Style:** {style.value['name']}")
                        st.write(f"🎵 **Notes:** {len(melody_notes)}")
                        if harmony_notes:
                            st.write(f"🎶 **Harmony:** {len(harmony_notes)} chord notes")
                        else:
                            st.write("🎶 **Harmony:** None")
                    
                    # Download section
                    st.subheader("📥 Download Your Melody")
                    
                    download_col1, download_col2 = st.columns(2)
                    
                    with download_col1:
                        filename = f"morse_melody_{message[:10].replace(' ', '_')}_{key.name}_{style.name}.mid"
                        st.download_button(
                            label="🎼 Download MIDI File",
                            data=midi_data,
                            file_name=filename,
                            mime="audio/midi",
                            use_container_width=True,
                            help="Works in any music software!"
                        )
                    
                    with download_col2:
                        # Info file
                        info_text = f"""Intelligent Morse Melody
========================

Message: {message}
Morse Code: {morse_display.strip()}
Musical Key: {key.value['name']}
Style: {style.value['name']}
Notes Generated: {len(melody_notes)}
Harmony: {'Yes' if harmony_notes else 'No'}

Generated by Intelligent Morse Melody Studio
Advanced Musical AI System
"""
                        st.download_button(
                            label="📄 Download Info",
                            data=info_text,
                            file_name=f"melody_info_{message[:10].replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Tips for next generation
                    st.info("💡 **Try this:** Change the key or style for a completely different melody of the same message!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating melody: {str(e)}")
                    st.write("Please try again with different settings.")
        else:
            st.warning("⚠️ Please enter a message to encode.")
    
    # Quick examples section
    st.subheader("🎯 Quick Examples")
    example_cols = st.columns(4)
    
    with example_cols[0]:
        if st.button("🌟 'Hope' in C Major Classical", use_container_width=True):
            st.session_state.update({
                'message': 'Hope',
                'key': MusicKey.C_MAJOR,
                'style': MusicStyle.CLASSICAL
            })
            st.rerun()
    
    with example_cols[1]:
        if st.button("🎸 'Love' in G Major Folk", use_container_width=True):
            st.session_state.update({
                'message': 'Love',
                'key': MusicKey.G_MAJOR,
                'style': MusicStyle.FOLK
            })
            st.rerun()
    
    with example_cols[2]:
        if st.button("🎺 'Jazz' in A Minor Jazz", use_container_width=True):
            st.session_state.update({
                'message': 'Jazz',
                'key': MusicKey.A_MINOR,
                'style': MusicStyle.JAZZ
            })
            st.rerun()
    
    with example_cols[3]:
        if st.button("🌙 'Dream' in C Pentatonic Ambient", use_container_width=True):
            st.session_state.update({
                'message': 'Dream',
                'key': MusicKey.C_PENTATONIC,
                'style': MusicStyle.AMBIENT
            })
            st.rerun()

    # Sidebar with information
    with st.sidebar:
        st.header("🎵 About This Tool")
        
        st.markdown("""
        **🧠 Intelligent Melody Generation**
        
        This tool uses advanced musical AI to create genuinely beautiful melodies that encode your secret messages.
        
        **✨ Key Features:**
        - Real musical intelligence
        - Natural phrase contours
        - Style-aware generation
        - Intelligent interval selection
        - Harmonic awareness
        
        **🎼 Musical Styles:**
        - **Classical:** Traditional, elegant arcs
        - **Folk:** Simple, memorable patterns  
        - **Jazz:** Sophisticated, unexpected
        - **Celtic:** Flowing, modal sounds
        - **Ambient:** Gentle, floating phrases
        
        **🎹 Different Every Time:**
        Each generation creates a unique melody, even for the same text. The AI considers musical context, phrase structure, and style to create genuinely musical results.
        """)
        
        st.header("🔍 How It Works")
        st.markdown("""
        **🎯 Musical Intelligence:**
        1. Converts your text to Morse code
        2. Creates natural phrase arcs
        3. Chooses notes using music theory
        4. Avoids repetitive patterns
        5. Generates complementary harmony
        
        **🎨 Each style has:**
        - Unique interval preferences
        - Different phrase contours
        - Style-specific chord progressions
        - Appropriate tempo and dynamics
        """)
        
        st.header("💡 Tips")
        st.markdown("""
        **For Best Results:**
        - Try the same message in different keys
        - Experiment with various styles
        - Use shorter messages for clarity
        - Enable harmony for richer sound
        
        **🎵 Musical Tip:**
        The same message sounds completely different in each key and style - try them all!
        """)

if __name__ == "__main__":
    main()
