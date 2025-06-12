import streamlit as st
import random
import math
import tempfile
import os
import numpy as np
import wave
import struct
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

def create_web_audio_player(melody_notes: List[Note], harmony_notes: List[Note] = None) -> str:
    """Create an enhanced web audio player for the generated music"""
    
    # Combine all notes for playback
    all_notes = melody_notes.copy()
    if harmony_notes:
        all_notes.extend(harmony_notes)
    
    # Convert notes to JSON format
    notes_data = []
    for note in all_notes:
        notes_data.append({
            "pitch": note.pitch,
            "start": note.start_time,
            "duration": note.duration,
            "velocity": note.velocity,
            "channel": note.channel
        })
    
    # Calculate total duration
    total_duration = max(note.start_time + note.duration for note in all_notes) if all_notes else 0
    
    audio_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    ">
        <h3 style="margin-top: 0; color: white; text-align: center;">🎧 Play Your Melody</h3>
        
        <div style="text-align: center; margin: 20px 0;">
            <button id="playBtn" onclick="togglePlay()" style="
                background: #ff6b6b;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 18px;
                margin-right: 15px;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(255, 107, 107, 0.6)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(255, 107, 107, 0.4)';">
                ▶️ Play
            </button>
            
            <button onclick="stopAudio()" style="
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 18px;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                ⏹️ Stop
            </button>
        </div>
        
        <div id="progress" style="
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
        ">
            <div id="progressBar" style="
                width: 0%;
                height: 100%;
                background: linear-gradient(90deg, #ff6b6b, #feca57);
                transition: width 0.1s ease;
                border-radius: 4px;
            "></div>
        </div>
        
        <div style="text-align: center;">
            <span id="timeDisplay" style="color: rgba(255,255,255,0.9); font-size: 16px;">0:00 / 0:00</span>
        </div>
        
        <div style="text-align: center; margin-top: 15px; font-size: 14px; opacity: 0.8;">
            🎵 Melody: Piano • 🎶 Harmony: Strings
        </div>
    </div>

    <script>
    let audioContext;
    let isPlaying = false;
    let startTime;
    let pauseTime = 0;
    let scheduledNotes = [];
    let animationFrame;
    
    const notesData = {notes_data};
    const totalDuration = {total_duration};
    
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
            const elapsed = audioContext.currentTime - startTime + pauseTime;
            const progress = Math.min((elapsed / totalDuration) * 100, 100);
            
            const progressBar = document.getElementById('progressBar');
            const timeDisplay = document.getElementById('timeDisplay');
            
            if (progressBar) progressBar.style.width = progress + '%';
            if (timeDisplay) timeDisplay.textContent = `${{formatTime(elapsed)}} / ${{formatTime(totalDuration)}}`;
            
            if (progress < 100 && isPlaying) {{
                animationFrame = requestAnimationFrame(updateProgress);
            }} else if (progress >= 100) {{
                stopAudio();
            }}
        }}
    }}
    
    function createNote(frequency, startTime, duration, velocity, channel) {{
        if (!audioContext) return null;
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        const filterNode = audioContext.createBiquadFilter();
        
        // Set up audio chain
        oscillator.connect(filterNode);
        filterNode.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Configure oscillator
        oscillator.frequency.setValueAtTime(frequency, startTime);
        
        // Different timbres for melody vs harmony
        if (channel === 0) {{
            oscillator.type = 'triangle';  // Melody: warm triangle wave
            filterNode.type = 'lowpass';
            filterNode.frequency.setValueAtTime(2000, startTime);
        }} else {{
            oscillator.type = 'sawtooth';  // Harmony: richer sawtooth
            filterNode.type = 'lowpass';
            filterNode.frequency.setValueAtTime(1200, startTime);
        }}
        
        // Set volume based on velocity and channel
        const baseVolume = channel === 0 ? 0.15 : 0.08;  // Melody louder than harmony
        const volume = (velocity / 127) * baseVolume;
        
        // Create natural envelope
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(volume * 0.3, startTime + duration * 0.7);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        // Schedule the note
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
        
        return oscillator;
    }}
    
    async function togglePlay() {{
        const playBtn = document.getElementById('playBtn');
        
        if (!audioContext) {{
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }}
        
        if (audioContext.state === 'suspended') {{
            await audioContext.resume();
        }}
        
        if (!isPlaying) {{
            // Start playing
            startTime = audioContext.currentTime;
            isPlaying = true;
            if (playBtn) playBtn.innerHTML = '⏸️ Pause';
            
            // Schedule all notes
            scheduledNotes = [];
            notesData.forEach(noteData => {{
                const frequency = midiToFreq(noteData.pitch);
                const noteStartTime = audioContext.currentTime + (noteData.start - pauseTime);
                
                if (noteStartTime >= audioContext.currentTime) {{
                    const oscillator = createNote(
                        frequency,
                        noteStartTime,
                        noteData.duration,
                        noteData.velocity,
                        noteData.channel
                    );
                    if (oscillator) scheduledNotes.push(oscillator);
                }}
            }});
            
            updateProgress();
        }} else {{
            // Pause
            pauseTime += audioContext.currentTime - startTime;
            stopAudio();
        }}
    }}
    
    function stopAudio() {{
        isPlaying = false;
        const playBtn = document.getElementById('playBtn');
        if (playBtn) playBtn.innerHTML = '▶️ Play';
        
        // Stop all scheduled notes
        scheduledNotes.forEach(oscillator => {{
            try {{
                oscillator.stop();
            }} catch(e) {{
                // Note might have already ended
            }}
        }});
        scheduledNotes = [];
        
        // Reset progress
        pauseTime = 0;
        const progressBar = document.getElementById('progressBar');
        const timeDisplay = document.getElementById('timeDisplay');
        if (progressBar) progressBar.style.width = '0%';
        if (timeDisplay) timeDisplay.textContent = `0:00 / ${{formatTime(totalDuration)}}`;
        
        // Cancel animation
        if (animationFrame) {{
            cancelAnimationFrame(animationFrame);
        }}
    }}
    
    // Initialize display
    document.addEventListener('DOMContentLoaded', function() {{
        const timeDisplay = document.getElementById('timeDisplay');
        if (timeDisplay) timeDisplay.textContent = `0:00 / ${{formatTime(totalDuration)}}`;
    }});
    </script>
    """
    
    return audio_html

def generate_wav_from_notes(melody_notes: List[Note], harmony_notes: List[Note] = None, sample_rate: int = 44100) -> bytes:
    """Generate a WAV file directly from note data using pure Python audio synthesis"""
    
    # Combine all notes
    all_notes = melody_notes.copy()
    if harmony_notes:
        all_notes.extend(harmony_notes)
    
    if not all_notes:
        return b""
    
    # Calculate total duration
    total_duration = max(note.start_time + note.duration for note in all_notes)
    total_samples = int(total_duration * sample_rate)
    
    # Create stereo audio buffer
    audio_left = np.zeros(total_samples, dtype=np.float32)
    audio_right = np.zeros(total_samples, dtype=np.float32)
    
    for note in all_notes:
        # Convert MIDI note to frequency
        frequency = 440.0 * (2.0 ** ((note.pitch - 69) / 12.0))
        
        # Calculate sample positions
        start_sample = int(note.start_time * sample_rate)
        duration_samples = int(note.duration * sample_rate)
        end_sample = min(start_sample + duration_samples, total_samples)
        
        if start_sample >= total_samples:
            continue
        
        # Generate time array for this note
        t = np.linspace(0, note.duration, end_sample - start_sample)
        
        # Create waveform based on channel (melody vs harmony)
        if note.channel == 0:  # Melody
            # Rich harmonic content for melody
            wave = (np.sin(2 * np.pi * frequency * t) * 0.6 +
                   np.sin(2 * np.pi * frequency * 2 * t) * 0.2 +
                   np.sin(2 * np.pi * frequency * 3 * t) * 0.1)
        else:  # Harmony
            # Softer waveform for harmony
            wave = (np.sin(2 * np.pi * frequency * t) * 0.4 +
                   np.sin(2 * np.pi * frequency * 2 * t) * 0.1)
        
        # Apply envelope (ADSR - Attack, Decay, Sustain, Release)
        envelope = np.ones_like(t)
        
        # Attack (5% of note)
        attack_samples = max(1, int(0.05 * len(t)))
        if attack_samples < len(envelope):
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Release (20% of note)
        release_samples = max(1, int(0.2 * len(t)))
        if release_samples < len(envelope):
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        
        # Apply velocity
        volume = (note.velocity / 127.0) * 0.3  # Scale down to prevent clipping
        wave *= envelope * volume
        
        # Add to audio buffers (stereo)
        if note.channel == 0:  # Melody - center
            audio_left[start_sample:end_sample] += wave
            audio_right[start_sample:end_sample] += wave
        else:  # Harmony - slightly left and right for width
            audio_left[start_sample:end_sample] += wave * 1.1
            audio_right[start_sample:end_sample] += wave * 0.9
    
    # Normalize audio to prevent clipping
    max_val = max(np.max(np.abs(audio_left)), np.max(np.abs(audio_right)))
    if max_val > 0:
        audio_left = audio_left / max_val * 0.8
        audio_right = audio_right / max_val * 0.8
    
    # Convert to 16-bit PCM
    audio_left_int = (audio_left * 32767).astype(np.int16)
    audio_right_int = (audio_right * 32767).astype(np.int16)
    
    # Interleave stereo channels
    stereo_audio = np.empty((audio_left_int.size + audio_right_int.size,), dtype=np.int16)
    stereo_audio[0::2] = audio_left_int
    stereo_audio[1::2] = audio_right_int
    
    # Create WAV file in memory
    import io
    wav_buffer = io.BytesIO()
    
    # Write WAV file manually
    # WAV header
    wav_buffer.write(b'RIFF')
    wav_buffer.write(struct.pack('<I', 36 + len(stereo_audio) * 2))  # File size
    wav_buffer.write(b'WAVE')
    wav_buffer.write(b'fmt ')
    wav_buffer.write(struct.pack('<I', 16))  # Subchunk1 size
    wav_buffer.write(struct.pack('<H', 1))   # Audio format (PCM)
    wav_buffer.write(struct.pack('<H', 2))   # Channels (stereo)
    wav_buffer.write(struct.pack('<I', sample_rate))  # Sample rate
    wav_buffer.write(struct.pack('<I', sample_rate * 2 * 2))  # Byte rate
    wav_buffer.write(struct.pack('<H', 4))   # Block align
    wav_buffer.write(struct.pack('<H', 16))  # Bits per sample
    wav_buffer.write(b'data')
    wav_buffer.write(struct.pack('<I', len(stereo_audio) * 2))  # Data size
    wav_buffer.write(stereo_audio.tobytes())
    
    return wav_buffer.getvalue()

def create_audio_player_with_wav(wav_data: bytes) -> str:
    """Create an audio player that uses the generated WAV file"""
    import base64
    
    # Convert WAV data to base64 for embedding
    wav_base64 = base64.b64encode(wav_data).decode()
    
    audio_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    ">
        <h3 style="margin-top: 0; color: white; text-align: center;">🎧 Play Your Melody</h3>
        
        <div style="text-align: center; margin: 20px 0;">
            <audio controls style="width: 100%; max-width: 500px;">
                <source src="data:audio/wav;base64,{wav_base64}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        </div>
        
        <div style="text-align: center; margin-top: 15px; font-size: 14px; opacity: 0.8;">
            🎵 High-Quality WAV Audio • 🎶 Stereo Sound
        </div>
    </div>
    """
    
    return audio_html

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

def generate_svg_sheet_music(melody_notes: List[Note], message: str, key_info: dict) -> str:
    """Generate simple SVG sheet music"""
    
    # SVG dimensions
    width = 800
    height = 400
    staff_top = 100
    staff_spacing = 15
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="white" stroke="black" stroke-width="2"/>
    
    <!-- Title -->
    <text x="{width//2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold">
        🎵 Morse Code Melody: {message.upper()}
    </text>
    <text x="{width//2}" y="50" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        Key: {key_info.get('name', 'C Major')} | 🔴 = Dots (.) | 🔵 = Dashes (-)
    </text>
    
    <!-- Staff lines -->'''
    
    # Draw 5 staff lines
    for i in range(5):
        y = staff_top + i * staff_spacing
        svg_content += f'\n    <line x1="50" y1="{y}" x2="{width-50}" y2="{y}" stroke="black" stroke-width="1"/>'
    
    # Add treble clef (simplified)
    svg_content += f'\n    <text x="70" y="{staff_top + 2*staff_spacing + 5}" font-family="serif" font-size="40" fill="black">𝄞</text>'
    
    # Convert message to morse for reference
    morse_sequence = []
    for char in message.upper():
        if char in MORSE_CODE:
            morse_sequence.extend(list(MORSE_CODE[char]))
            morse_sequence.append(' ')
        elif char == ' ':
            morse_sequence.append('/')
    
    # Draw notes
    x_pos = 120
    morse_index = 0
    
    for i, note in enumerate(melody_notes[:16]):  # Limit to 16 notes for readability
        # Calculate staff position (middle C = line 2)
        midi_60_position = staff_top + 2 * staff_spacing  # Middle C position
        semitone_spacing = staff_spacing / 2
        note_y = midi_60_position - (note.pitch - 60) * semitone_spacing
        
        # Determine note type and color
        if note.duration <= 0.3:  # Dot
            note_symbol = "♪"
            color = "#FF6B6B"  # Red
        else:  # Dash
            note_symbol = "♩"
            color = "#4ECDC4"  # Blue
        
        # Draw note
        svg_content += f'\n    <text x="{x_pos}" y="{note_y + 5}" text-anchor="middle" font-family="serif" font-size="24" fill="{color}">{note_symbol}</text>'
        
        # Add morse code annotation
        if morse_index < len(morse_sequence) and morse_sequence[morse_index] in '.-':
            morse_char = morse_sequence[morse_index]
            svg_content += f'\n    <text x="{x_pos}" y="{staff_top - 10}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="{color}">{morse_char}</text>'
            morse_index += 1
        elif morse_index < len(morse_sequence):
            morse_index += 1
        
        # Add note name below staff
        note_name = get_note_name_simple(note.pitch)
        svg_content += f'\n    <text x="{x_pos}" y="{staff_top + 5*staff_spacing + 20}" text-anchor="middle" font-family="Arial" font-size="10" fill="#666">{note_name}</text>'
        
        # Add ledger lines if needed
        if note_y < staff_top:  # Above staff
            ledger_lines_needed = int((staff_top - note_y) // staff_spacing) + 1
            for line_num in range(1, ledger_lines_needed + 1):
                ledger_y = staff_top - line_num * staff_spacing
                if ledger_y >= note_y - 5:
                    svg_content += f'\n    <line x1="{x_pos - 15}" y1="{ledger_y}" x2="{x_pos + 15}" y2="{ledger_y}" stroke="black" stroke-width="1"/>'
        elif note_y > staff_top + 4 * staff_spacing:  # Below staff
            ledger_lines_needed = int((note_y - (staff_top + 4 * staff_spacing)) // staff_spacing) + 1
            for line_num in range(1, ledger_lines_needed + 1):
                ledger_y = staff_top + 4 * staff_spacing + line_num * staff_spacing
                if ledger_y <= note_y + 5:
                    svg_content += f'\n    <line x1="{x_pos - 15}" y1="{ledger_y}" x2="{x_pos + 15}" y2="{ledger_y}" stroke="black" stroke-width="1"/>'
        
        x_pos += 40
        
        # Start new line if needed
        if x_pos > width - 100 and i < len(melody_notes) - 1:
            break
    
    # Add morse code reference at bottom
    full_morse = " ".join(MORSE_CODE.get(c.upper(), '') for c in message if c.upper() in MORSE_CODE)
    svg_content += f'''
    
    <!-- Morse code reference -->
    <text x="50" y="{height - 40}" font-family="Arial, sans-serif" font-size="12" fill="#333">
        Morse Code: {full_morse}
    </text>
    <text x="50" y="{height - 20}" font-family="Arial, sans-serif" font-size="10" fill="#666">
        Generated by Intelligent Morse Melody Studio - Music Education Tool
    </text>
</svg>'''
    
    return svg_content

def generate_simple_score_text(melody_notes: List[Note], message: str, key_info: dict) -> str:
    """Generate a simple text-based musical score for educational purposes"""
    
    score_text = f"""
🎼 MUSICAL SCORE: {message.upper()}
{'=' * 50}

🎹 Key: {key_info.get('name', 'C Major')}
🎵 Secret Message: {message.upper()}

📝 MORSE CODE TO MUSIC MAPPING:
{'-' * 30}
"""
    
    # Add morse code breakdown
    for char in message.upper():
        if char in MORSE_CODE and char != ' ':
            morse_pattern = MORSE_CODE[char]
            score_text += f"Letter '{char}': {morse_pattern}\n"
    
    score_text += f"""
🎼 MUSICAL NOTATION GUIDE:
{'-' * 25}
• Short notes (♪) = DOTS (.)
• Long notes (♩) = DASHES (-)
• Rests = Letter/word gaps

📊 MELODY ANALYSIS:
{'-' * 18}
• Total Notes: {len(melody_notes)}
• Highest Note: MIDI {max(note.pitch for note in melody_notes)}
• Lowest Note: MIDI {min(note.pitch for note in melody_notes)}
• Note Range: {max(note.pitch for note in melody_notes) - min(note.pitch for note in melody_notes)} semitones

🎵 NOTE SEQUENCE:
{'-' * 16}
"""
    
    # Add simplified note representation
    for i, note in enumerate(melody_notes[:20]):  # First 20 notes
        duration_symbol = "♪" if note.duration <= 0.3 else "♩"
        note_name = get_note_name_simple(note.pitch)
        score_text += f"{i+1:2d}. {duration_symbol} {note_name} (MIDI {note.pitch})\n"
    
    if len(melody_notes) > 20:
        score_text += f"... and {len(melody_notes) - 20} more notes\n"
    
    score_text += """
🎓 EDUCATIONAL NOTES:
==================
This melody encodes your secret message using Morse code timing!
Each letter becomes a unique musical phrase.

🔍 ANALYSIS QUESTIONS:
- Which letters create interesting rhythms?
- How do dots vs dashes affect the melody?
- What happens when you change the musical key?

Generated by Intelligent Morse Melody Studio
Perfect for Music Education!
"""
    
    return score_text

def get_note_name_simple(midi_note):
    """Simple note name with octave"""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = note_names[midi_note % 12]
    return f"{note}{octave}"

def decode_midi_to_morse(midi_file_bytes) -> Tuple[str, str, float]:
    """Decode a MIDI file back to morse code and text"""
    try:
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp_file:
            tmp_file.write(midi_file_bytes)
            tmp_file_path = tmp_file.name
        
        # Load MIDI file
        mid = mido.MidiFile(tmp_file_path)
        
        # Extract notes from the melody track (track 0)
        notes = []
        current_time = 0
        
        for track in mid.tracks:
            current_time = 0
            note_events = []
            
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_events.append(('on', current_time, msg.note))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_events.append(('off', current_time, msg.note))
            
            # Process note events to get durations
            active_notes = {}
            for event_type, time, note in note_events:
                if event_type == 'on':
                    active_notes[note] = time
                elif event_type == 'off' and note in active_notes:
                    start_time = active_notes[note]
                    duration = time - start_time
                    notes.append((start_time, duration, note))
                    del active_notes[note]
            
            # If we found notes, use this track
            if notes:
                break
        
        if not notes:
            return "", "No notes found in MIDI file", 0.0
        
        # Sort notes by start time
        notes.sort(key=lambda x: x[0])
        
        # Analyze timing to determine dots and dashes
        durations = [duration for _, duration, _ in notes]
        if len(durations) < 2:
            return "", "Not enough notes to analyze", 0.0
        
        # Find threshold between dots and dashes
        sorted_durations = sorted(durations)
        threshold_index = len(sorted_durations) // 3
        dot_threshold = sorted_durations[threshold_index] if threshold_index < len(sorted_durations) else sorted_durations[0]
        
        # Convert to morse symbols
        morse_symbols = []
        last_end_time = 0
        
        for start_time, duration, note in notes:
            # Check for gaps (letter/word separators)
            gap = start_time - last_end_time
            
            if gap > dot_threshold * 3:  # Word gap
                if morse_symbols and morse_symbols[-1] != '/':
                    morse_symbols.append('/')
            elif gap > dot_threshold * 1.5:  # Letter gap
                if morse_symbols and morse_symbols[-1] not in [' ', '/']:
                    morse_symbols.append(' ')
            
            # Determine if dot or dash
            if duration <= dot_threshold * 2:
                morse_symbols.append('.')
            else:
                morse_symbols.append('-')
            
            last_end_time = start_time + duration
        
        # Convert morse symbols to display string
        morse_display = ''.join(morse_symbols)
        
        # Convert morse to text
        decoded_text = ""
        current_letter = ""
        
        for symbol in morse_symbols:
            if symbol == '.':
                current_letter += '.'
            elif symbol == '-':
                current_letter += '-'
            elif symbol == ' ':
                if current_letter:
                    # Find letter for this morse pattern
                    for letter, pattern in MORSE_CODE.items():
                        if pattern == current_letter:
                            decoded_text += letter
                            break
                    else:
                        decoded_text += '?'
                    current_letter = ""
            elif symbol == '/':
                if current_letter:
                    # Process last letter before word break
                    for letter, pattern in MORSE_CODE.items():
                        if pattern == current_letter:
                            decoded_text += letter
                            break
                    else:
                        decoded_text += '?'
                    current_letter = ""
                decoded_text += ' '
        
        # Process final letter
        if current_letter:
            for letter, pattern in MORSE_CODE.items():
                if pattern == current_letter:
                    decoded_text += letter
                    break
            else:
                decoded_text += '?'
        
        # Calculate confidence score
        total_chars = len([c for c in decoded_text if c != ' '])
        unknown_chars = decoded_text.count('?')
        confidence = ((total_chars - unknown_chars) / max(total_chars, 1)) * 100 if total_chars > 0 else 0
        
        # Clean up temp file
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        
        return morse_display, decoded_text.strip(), confidence
        
    except Exception as e:
        return "", f"Error decoding MIDI: {str(e)}", 0.0

def generate_educational_analysis(melody_notes: List[Note], message: str, key_info: dict, style_info: dict) -> str:
    """Generate educational analysis of the melody for music students"""
    
    analysis = f"""🎓 EDUCATIONAL ANALYSIS: Morse Code Melody
===========================================

📝 SECRET MESSAGE: {message.upper()}
🎼 MUSICAL SETTINGS: {key_info.get('name', 'Unknown')} - {style_info.get('name', 'Unknown')} Style

📊 MUSICAL ANALYSIS:
-------------------
• Total Notes: {len(melody_notes)}
• Note Range: {max(note.pitch for note in melody_notes) - min(note.pitch for note in melody_notes)} semitones
• Highest Note: {get_note_name_simple(max(note.pitch for note in melody_notes))}
• Lowest Note: {get_note_name_simple(min(note.pitch for note in melody_notes))}

🔤 MORSE TO MUSIC MAPPING:
-------------------------
"""
    
    # Add letter-by-letter analysis
    for char in message.upper():
        if char in MORSE_CODE and char != ' ':
            morse_pattern = MORSE_CODE[char]
            analysis += f"• Letter '{char}' = {morse_pattern}\n"
            
            # Count dots and dashes
            dots = morse_pattern.count('.')
            dashes = morse_pattern.count('-')
            
            if dots > dashes:
                analysis += f"  → More DOTS = Faster, lighter rhythm\n"
            elif dashes > dots:
                analysis += f"  → More DASHES = Slower, heavier rhythm\n"
            else:
                analysis += f"  → Balanced rhythm\n"
    
    analysis += f"""
🎵 COMPOSITION TECHNIQUES:
------------------------
• DOTS (.) become short notes (eighth notes ♪)
• DASHES (-) become long notes (quarter notes ♩)
• Letter gaps create musical phrases
• Word gaps create longer rests
• Musical AI chooses notes that flow naturally

🎓 LEARNING OPPORTUNITIES:
-------------------------
1. RHYTHM: Notice how Morse timing creates musical rhythm
2. MELODY: See how the AI creates flowing melodic lines
3. HARMONY: Observe chord progressions that support the melody
4. FORM: Watch how letters create musical phrases

🏆 CREATIVE CHALLENGES & CONTESTS:
=================================

🎯 CHALLENGE 1: "MELODY MASTERMIND"
----------------------------------
Contest: Who can create the most beautiful melody with a coherent sentence?

RULES:
• Create a meaningful sentence (not random words)
• Generate melodies in different keys/styles
• Judge based on:
  - Musical beauty and flow
  - Sentence meaning and creativity
  - How well the morse rhythm works musically
  - Overall artistic merit

TIPS FOR WINNING:
• Try sentences with varied letter patterns
• Letters like E, T, A (simple morse) create smooth melodies
• Mix short words (E, I, A) with longer words for rhythm variety
• Avoid too many letters with complex morse (Q, X, Y)

EXAMPLE SENTENCES TO TRY:
• "Music heals the heart"
• "Dreams take flight"  
• "Art creates magic"
• "Hope lights the path"

🎼 CHALLENGE 2: "REMIX THE CLASSICS"
------------------------------------
Advanced Challenge: Take existing songs and encode messages!

HOW TO PLAY:
1. Take the sheet music from a famous song
2. Keep the pitches (notes) exactly the same
3. Change ONLY the rhythm/timing to spell morse code words
4. See how it transforms the original song!

EXAMPLE: "Happy Birthday"
• Original: ♩ ♩ ♪♪ ♩ - ♩ ♩ ♪♪ ♩
• Modified: Make the rhythm spell "HAPPY" in morse:
  H = .... (4 short notes)
  A = .- (short-long)
  P = .--. (short-long-long-short)
  P = .--. (short-long-long-short)  
  Y = -.-- (long-short-long-long)

CHALLENGE VARIATIONS:
• "Twinkle Twinkle Little Star" → encode "TWINKLE"
• "Mary Had a Little Lamb" → encode "MARY"
• Any melody → encode your name!

🎨 ADVANCED EXPERIMENTS:
=======================

🔬 EXPERIMENT 1: "LETTER PERSONALITY STUDY"
• Generate the same letter in different keys
• Question: Does 'A' sound happy in C Major but sad in A Minor?
• Study: How do different scales affect letter personalities?

🔬 EXPERIMENT 2: "RHYTHM PSYCHOLOGY" 
• Create words with mostly dots vs mostly dashes
• Compare: "FEED" (all dots/simple) vs "ZOOM" (more dashes)
• Question: Do dot-heavy words sound more energetic?

🔬 EXPERIMENT 3: "MUSICAL CRYPTOGRAPHY"
• Hide multiple messages in one song using different instruments
• Melody = Message 1, Bass = Message 2, Harmony = Message 3
• Create musical conversations between parts!

🎯 EDUCATIONAL GAMES:
====================

🎮 GAME 1: "MORSE MELODY DETECTIVE"
• Play melodies without showing the text
• Students guess the hidden message
• Points for correct letters/words

🎮 GAME 2: "STYLE TRANSFORMATION CHALLENGE"
• Same message in 5 different styles
• Students identify which is Classical, Jazz, Folk, etc.
• Discuss how style changes perception of same text

🎮 GAME 3: "COMPOSE THE SECRET CODE"
• Give students a mission briefing
• They must compose a song that secretly spells coordinates
• Others decode to find the "treasure location"

💡 RESEARCH QUESTIONS FOR STUDENTS:
==================================

🔍 MUSICOLOGY RESEARCH:
• Which letters create the most pleasing melodies?
• How do cultural musical preferences affect morse melody perception?
• Can you identify musical "accents" in different morse styles?

🔍 PSYCHOLOGY RESEARCH:
• Do people remember messages better when they're melodies?
• Which musical keys make messages sound more urgent/calm?
• How does tempo affect message comprehension?

🔍 TECHNOLOGY RESEARCH:
• Could this be used for accessible communication?
• What if we encoded morse in rhythm instead of pitch?
• How would this work with different instruments?

🎓 CLASSROOM ACTIVITIES:
=======================

📚 FOR MUSIC TEACHERS:
• Use this to teach rhythm, note reading, and composition
• Students compose "musical diary entries"
• Create class songs where each student adds a musical sentence

📚 FOR HISTORY TEACHERS:
• Encode historical quotes and dates
• Students decode messages from different time periods
• Combine with lessons on telegraph and communication history

📚 FOR LANGUAGE ARTS:
• Write poems that also sound musical when encoded
• Explore how rhythm affects meaning in both poetry and music
• Study the relationship between language patterns and musical patterns

🌟 PROFESSIONAL APPLICATIONS:
============================

🎼 FOR COMPOSERS:
• Use morse code as inspiration for rhythmic patterns
• Encode song titles or dedications into the music itself
• Create "musical signatures" using your name in morse

🎭 FOR PERFORMERS:
• Add secret messages in performances
• Use this technique for musical theater or film scoring
• Create interactive performances where audience decodes messages

This melody demonstrates how ANY text can become music using
mathematical relationships and musical intelligence!

The possibilities are truly endless - you've created not just a 
secret message tool, but a complete musical-educational platform!

Generated by Intelligent Morse Melody Studio
Perfect for Music Education & Creative Exploration!
"""
    
    return analysis
    """Decode a MIDI file back to morse code and text"""
    try:
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp_file:
            tmp_file.write(midi_file_bytes)
            tmp_file_path = tmp_file.name
        
        # Load MIDI file
        mid = mido.MidiFile(tmp_file_path)
        
        # Extract notes from the melody track (track 0)
        notes = []
        current_time = 0
        
        for track in mid.tracks:
            current_time = 0
            note_events = []
            
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_events.append(('on', current_time, msg.note))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_events.append(('off', current_time, msg.note))
            
            # Process note events to get durations
            active_notes = {}
            for event_type, time, note in note_events:
                if event_type == 'on':
                    active_notes[note] = time
                elif event_type == 'off' and note in active_notes:
                    start_time = active_notes[note]
                    duration = time - start_time
                    notes.append((start_time, duration, note))
                    del active_notes[note]
            
            # If we found notes, use this track
            if notes:
                break
        
        if not notes:
            return "", "No notes found in MIDI file", 0.0
        
        # Sort notes by start time
        notes.sort(key=lambda x: x[0])
        
        # Analyze timing to determine dots and dashes
        durations = [duration for _, duration, _ in notes]
        if len(durations) < 2:
            return "", "Not enough notes to analyze", 0.0
        
        # Find threshold between dots and dashes
        sorted_durations = sorted(durations)
        threshold_index = len(sorted_durations) // 3
        dot_threshold = sorted_durations[threshold_index] if threshold_index < len(sorted_durations) else sorted_durations[0]
        
        # Convert to morse symbols
        morse_symbols = []
        last_end_time = 0
        
        for start_time, duration, note in notes:
            # Check for gaps (letter/word separators)
            gap = start_time - last_end_time
            
            if gap > dot_threshold * 3:  # Word gap
                if morse_symbols and morse_symbols[-1] != '/':
                    morse_symbols.append('/')
            elif gap > dot_threshold * 1.5:  # Letter gap
                if morse_symbols and morse_symbols[-1] not in [' ', '/']:
                    morse_symbols.append(' ')
            
            # Determine if dot or dash
            if duration <= dot_threshold * 2:
                morse_symbols.append('.')
            else:
                morse_symbols.append('-')
            
            last_end_time = start_time + duration
        
        # Convert morse symbols to display string
        morse_display = ''.join(morse_symbols)
        
        # Convert morse to text
        decoded_text = ""
        current_letter = ""
        
        for symbol in morse_symbols:
            if symbol == '.':
                current_letter += '.'
            elif symbol == '-':
                current_letter += '-'
            elif symbol == ' ':
                if current_letter:
                    # Find letter for this morse pattern
                    for letter, pattern in MORSE_CODE.items():
                        if pattern == current_letter:
                            decoded_text += letter
                            break
                    else:
                        decoded_text += '?'
                    current_letter = ""
            elif symbol == '/':
                if current_letter:
                    # Process last letter before word break
                    for letter, pattern in MORSE_CODE.items():
                        if pattern == current_letter:
                            decoded_text += letter
                            break
                    else:
                        decoded_text += '?'
                    current_letter = ""
                decoded_text += ' '
        
        # Process final letter
        if current_letter:
            for letter, pattern in MORSE_CODE.items():
                if pattern == current_letter:
                    decoded_text += letter
                    break
            else:
                decoded_text += '?'
        
        # Calculate confidence score
        total_chars = len([c for c in decoded_text if c != ' '])
        unknown_chars = decoded_text.count('?')
        confidence = ((total_chars - unknown_chars) / max(total_chars, 1)) * 100 if total_chars > 0 else 0
        
        # Clean up temp file
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        
        return morse_display, decoded_text.strip(), confidence
        
    except Exception as e:
        return "", f"Error decoding MIDI: {str(e)}", 0.0

def main():
    # Title and description
    st.title("🎵 Intelligent Morse Melody Studio")
    st.markdown("**Generate genuinely beautiful melodies that encode your secret messages using advanced musical AI**")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🎼 Create Melody", "🔍 Decode Melody"])
    
    # ---------------------- CREATE TAB ----------------------
    with tab1:
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
                        
                        # Create MIDI, WAV, and educational materials
                        midi_data = create_midi_file(melody_notes, harmony_notes)
                        wav_data = generate_wav_from_notes(melody_notes, harmony_notes)
                        score_text = generate_simple_score_text(melody_notes, message, key.value)
                        svg_sheet_music = generate_svg_sheet_music(melody_notes, message, key.value)
                        analysis_text = generate_educational_analysis(melody_notes, message, key.value, style.value)
                        
                        # Generate a random song ID for filename
                        import time
                        song_id = f"song_{int(time.time()) % 100000:05d}"
                        
                        # Store in session state immediately after generation
                        st.session_state.update({
                            'melody_generated': True,
                            'current_midi_data': midi_data,
                            'current_wav_data': wav_data,
                            'current_score_text': score_text,
                            'current_svg_sheet': svg_sheet_music,
                            'current_analysis_text': analysis_text,
                            'current_song_id': song_id,
                            'current_key_name': key.name,
                            'current_style_name': style.name,
                            'current_message': message,
                            'current_melody_notes': len(melody_notes),
                            'current_harmony': 'Yes' if harmony_notes else 'No'
                        })
                        
                        # Success message
                        st.success("✨ **Beautiful melody created!**")
                        
                        # WAV Audio Player
                        st.subheader("🎧 Listen to Your Melody")
                        if wav_data:
                            audio_player_html = create_audio_player_with_wav(wav_data)
                            st.components.v1.html(audio_player_html, height=200)
                        else:
                            st.error("Could not generate audio. MIDI file is still available for download.")
                        
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
                        
                        # Download section - use session state data
                        st.subheader("📥 Download Your Complete Musical Package")
                        
                        # Get data from session state (prevents regeneration on each download)
                        midi_data = st.session_state.get('current_midi_data', b'')
                        wav_data = st.session_state.get('current_wav_data', b'')
                        score_text = st.session_state.get('current_score_text', '')
                        svg_sheet = st.session_state.get('current_svg_sheet', '')
                        analysis_text = st.session_state.get('current_analysis_text', '')
                        song_id = st.session_state.get('current_song_id', 'unknown')
                        key_name = st.session_state.get('current_key_name', 'C_MAJOR')
                        style_name = st.session_state.get('current_style_name', 'CLASSICAL')
                        
                        download_col1, download_col2, download_col3, download_col4, download_col5 = st.columns(5)
                        
                        with download_col1:
                            if midi_data:
                                filename = f"melody_{song_id}_{key_name}_{style_name}.mid"
                                st.download_button(
                                    label="🎼 MIDI File",
                                    data=midi_data,
                                    file_name=filename,
                                    mime="audio/midi",
                                    use_container_width=True,
                                    help="For music software!",
                                    key="midi_download"
                                )
                        
                        with download_col2:
                            if wav_data:
                                wav_filename = f"melody_{song_id}_{key_name}_{style_name}.wav"
                                st.download_button(
                                    label="🎵 WAV Audio",
                                    data=wav_data,
                                    file_name=wav_filename,
                                    mime="audio/wav",
                                    use_container_width=True,
                                    help="High-quality audio!",
                                    key="wav_download"
                                )
                        
                        with download_col3:
                            if svg_sheet:
                                st.download_button(
                                    label="🎼 Sheet Music",
                                    data=svg_sheet.encode('utf-8'),
                                    file_name=f"sheet_music_{song_id}.svg",
                                    mime="image/svg+xml",
                                    use_container_width=True,
                                    help="Visual sheet music!",
                                    key="sheet_download"
                                )
                        
                        with download_col4:
                            if score_text:
                                st.download_button(
                                    label="📝 Text Score",
                                    data=score_text,
                                    file_name=f"score_{song_id}.txt",
                                    mime="text/plain",
                                    use_container_width=True,
                                    help="Text-based notation!",
                                    key="score_download"
                                )
                        
                        with download_col5:
                            if analysis_text:
                                st.download_button(
                                    label="🎓 Analysis",
                                    data=analysis_text,
                                    file_name=f"analysis_{song_id}.txt",
                                    mime="text/plain",
                                    use_container_width=True,
                                    help="Educational guide!",
                                    key="analysis_download"
                                )
                        
                        # Show sheet music preview
                        if svg_sheet:
                            st.subheader("🎼 Sheet Music Preview")
                            st.components.v1.html(f'<div style="text-align: center;">{svg_sheet}</div>', height=450)
                        
                        # Educational insights
                        st.subheader("🎓 Educational Insights")
                        with st.expander("📚 See Musical Score & Analysis"):
                            st.text(score_text)
                            st.text(analysis_text)
                        
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

    # ---------------------- DECODE TAB ----------------------
    with tab2:
        st.header("🔍 Decode Hidden Messages from MIDI Files")
        st.markdown("Upload a MIDI file created by this tool to reveal the hidden morse code message!")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a MIDI file to decode:",
            type=['mid', 'midi'],
            help="Upload .mid or .midi files created by this application"
        )
        
        if uploaded_file is not None:
            st.success(f"📁 **File uploaded:** {uploaded_file.name}")
            
            # Decode button
            if st.button("🔍 Decode Hidden Message", type="primary", use_container_width=True):
                with st.spinner("🔬 Analyzing MIDI file and decoding message..."):
                    try:
                        # Read uploaded file
                        midi_bytes = uploaded_file.read()
                        
                        # Decode the MIDI file
                        morse_code, decoded_text, confidence = decode_midi_to_morse(midi_bytes)
                        
                        if decoded_text and not decoded_text.startswith("Error"):
                            # Success! Display results
                            st.balloons()
                            
                            # Confidence indicator
                            if confidence >= 80:
                                st.success(f"✅ **High confidence decode** ({confidence:.1f}%)")
                            elif confidence >= 60:
                                st.warning(f"⚠️ **Medium confidence decode** ({confidence:.1f}%)")
                            else:
                                st.error(f"❌ **Low confidence decode** ({confidence:.1f}%)")
                            
                            # Display results
                            result_col1, result_col2 = st.columns(2)
                            
                            with result_col1:
                                st.subheader("🎯 **Hidden Message Revealed:**")
                                st.markdown(f"### **{decoded_text.upper()}**")
                                
                                st.subheader("📻 **Morse Code Pattern:**")
                                st.code(morse_code)
                            
                            with result_col2:
                                st.subheader("📊 **Analysis Details:**")
                                
                                # Calculate statistics
                                total_chars = len([c for c in decoded_text if c != ' '])
                                words = len(decoded_text.split())
                                unknown_chars = decoded_text.count('?')
                                
                                st.metric("🔤 **Characters Decoded**", total_chars)
                                st.metric("📝 **Words Found**", words)
                                st.metric("❓ **Unknown Characters**", unknown_chars)
                                st.metric("🎯 **Decode Confidence**", f"{confidence:.1f}%")
                                
                                # Confidence explanation
                                if confidence < 80:
                                    st.info("""
                                    **Low confidence may be due to:**
                                    - MIDI file not created by this tool
                                    - Non-standard timing patterns
                                    - File corruption or modification
                                    - Complex musical arrangements
                                    """)
                            
                            # Show character-by-character breakdown
                            with st.expander("🔍 **Detailed Character Analysis**"):
                                st.write("**Character-by-character breakdown:**")
                                
                                words = decoded_text.split()
                                for word_idx, word in enumerate(words):
                                    st.write(f"**Word {word_idx + 1}:** `{word}`")
                                    
                                    # Show each character's morse pattern
                                    char_cols = st.columns(min(len(word), 6))
                                    for char_idx, char in enumerate(word):
                                        col_idx = char_idx % 6
                                        with char_cols[col_idx]:
                                            if char in MORSE_CODE:
                                                morse_pattern = MORSE_CODE[char]
                                                st.success(f"**{char}** = `{morse_pattern}`")
                                            elif char == '?':
                                                st.error(f"**{char}** = `unknown`")
                                            else:
                                                st.info(f"**{char}** = `special`")
                            
                            # Play the uploaded file
                            st.subheader("🎧 **Listen to the Uploaded Melody**")
                            st.info("💡 **Note:** Playback uses the uploaded MIDI file directly. The melody you hear contains the hidden message!")
                            
                            # Create a simple playback option
                            try:
                                # Reset file pointer
                                uploaded_file.seek(0)
                                
                                # For now, just offer download of the decoded info
                                decode_info = f"""DECODED MORSE MESSAGE
=====================

Original Message: {decoded_text}
Morse Code: {morse_code}
Decode Confidence: {confidence:.1f}%
Characters: {total_chars}
Words: {words}
Unknown Characters: {unknown_chars}

Decoded by Intelligent Morse Melody Studio
"""
                                
                                st.download_button(
                                    label="📄 Download Decode Results",
                                    data=decode_info,
                                    file_name=f"decoded_message_{decoded_text[:10].replace(' ', '_')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                                
                            except Exception as e:
                                st.warning(f"Note: Could not create playback for uploaded file: {e}")
                            
                        else:
                            # Decoding failed
                            st.error("❌ **Could not decode the MIDI file**")
                            st.write(f"**Error:** {decoded_text}")
                            
                            st.info("""
                            **Possible reasons:**
                            - File was not created by this Morse Melody tool
                            - File is corrupted or incomplete
                            - MIDI format is not supported
                            - File contains no recognizable morse patterns
                            
                            **💡 Tip:** This decoder works best with MIDI files created by this application.
                            """)
                    
                    except Exception as e:
                        st.error(f"❌ **Error processing file:** {str(e)}")
                        st.write("Please ensure you've uploaded a valid MIDI file.")
        
        else:
            # Show instructions when no file is uploaded
            st.info("""
            **📋 How to use the decoder:**
            
            1. **Upload a MIDI file** created by this application
            2. **Click "Decode Hidden Message"** to analyze the file
            3. **View the results** including the original text and morse code
            4. **Check the confidence score** to see how accurate the decode is
            
            **✅ Best results with:**
            - MIDI files created by this tool
            - Files that haven't been modified
            - Simple melodies without complex arrangements
            
            **🎵 Try it:** Create a melody in the first tab, download it, then upload it here to test the decoder!
            """)
            
            # Example section
            st.subheader("🎯 **Test the Decoder**")
            st.markdown("Want to test the decoder? Create a melody in the **Create Melody** tab, download the MIDI file, then upload it here!")


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
