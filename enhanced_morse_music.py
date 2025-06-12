from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess
import math
from collections import deque

# Morse code dictionary (unchanged)
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', 
    '0': '-----', ' ': '/'
}

# IMPROVED: More musical scales with authentic intervals
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues': [0, 3, 5, 6, 7, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
    'whole_tone': [0, 2, 4, 6, 8, 10],
    'diminished': [0, 2, 3, 5, 6, 8, 9, 11],
    'japanese': [0, 1, 5, 7, 8],
    'arabic': [0, 1, 4, 5, 7, 8, 11],
    'gypsy': [0, 2, 3, 6, 7, 8, 11]
}

# Enhanced chord progressions
CHORD_PROGRESSIONS = {
    'classic': [0, 5, 3, 4],     # I-vi-IV-V
    'pop': [0, 3, 5, 4],         # I-IV-vi-V
    'folk': [0, 4, 0, 4],        # I-V-I-V
    'minor': [0, 6, 3, 4],       # i-VII-IV-V
    'jazz': [0, 5, 1, 4],        # I-vi-ii-V
    'blues': [0, 0, 4, 0, 5, 4, 0, 5],  # 12-bar blues pattern
    'modal': [0, 2, 4, 0],       # I-iii-V-I
    'descending': [0, 10, 8, 6], # I-♭VII-♭VI-♭V
    'circle': [0, 4, 1, 5]       # I-V-ii-vi
}

# Musical styles with AI parameters
MUSICAL_STYLES = {
    'ballad': {
        'tempo_range': (70, 90),
        'chord_rhythm': 'slow',
        'bass_style': 'simple',
        'melody_range': 'mid'
    },
    'folk': {
        'tempo_range': (90, 120),
        'chord_rhythm': 'medium',
        'bass_style': 'alternating',
        'melody_range': 'full'
    },
    'jazz': {
        'tempo_range': (110, 140),
        'chord_rhythm': 'syncopated',
        'bass_style': 'walking',
        'melody_range': 'extended'
    },
    'ambient': {
        'tempo_range': (60, 80),
        'chord_rhythm': 'sustained',
        'bass_style': 'minimal',
        'melody_range': 'wide'
    }
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root_pitch, scale_type):
    """Generate notes for a given scale across multiple octaves"""
    scale_intervals = SCALES[scale_type]
    notes = []
    # Generate 3 octaves of the scale
    for octave in range(3):
        for interval in scale_intervals:
            note = root_pitch + (octave * 12) + interval - 12  # Start one octave below
            if 36 <= note <= 96:  # Keep within MIDI range
                notes.append(note)
    return sorted(notes)

def get_chord_notes(root_pitch, chord_type='major'):
    """Generate chord notes with more variety"""
    if chord_type == 'major':
        return [root_pitch, root_pitch + 4, root_pitch + 7]
    elif chord_type == 'minor':
        return [root_pitch, root_pitch + 3, root_pitch + 7]
    elif chord_type == 'dim':
        return [root_pitch, root_pitch + 3, root_pitch + 6]
    elif chord_type == 'major7':
        return [root_pitch, root_pitch + 4, root_pitch + 7, root_pitch + 11]
    elif chord_type == 'minor7':
        return [root_pitch, root_pitch + 3, root_pitch + 7, root_pitch + 10]
    elif chord_type == 'dom7':
        return [root_pitch, root_pitch + 4, root_pitch + 7, root_pitch + 10]
    else:
        return [root_pitch, root_pitch + 4, root_pitch + 7]

class ImprovedMelodyGenerator:
    """VASTLY IMPROVED melody generator that creates beautiful, musical melodies"""
    
    def __init__(self, key_root, scale_type='major'):
        self.key_root = key_root
        self.scale_type = scale_type
        self.scale_notes = get_scale_notes(key_root, scale_type)
        
        # Musical memory and context
        self.last_notes = deque(maxlen=6)  # Remember last 6 notes
        self.phrase_direction = 0  # -1 down, 0 neutral, 1 up
        self.phrase_position = 0
        self.phrase_peak_reached = False
        
        # Musical intelligence parameters
        self.preferred_intervals = self._get_interval_preferences()
        self.tendency_notes = self._get_tendency_notes()
        
    def _get_interval_preferences(self):
        """Define preferred intervals for melodic movement"""
        if self.scale_type in ['major', 'minor']:
            # Classical preferences: steps and thirds favored
            return {
                1: 0.25,   # Half step
                2: 0.30,   # Whole step (most common)
                3: 0.15,   # Minor third
                4: 0.12,   # Major third
                5: 0.08,   # Perfect fourth
                7: 0.06,   # Perfect fifth
                12: 0.04   # Octave
            }
        elif self.scale_type == 'pentatonic':
            # Pentatonic prefers larger, more open intervals
            return {
                2: 0.25,   # Whole step
                3: 0.20,   # Minor third
                4: 0.20,   # Major third
                5: 0.15,   # Perfect fourth
                7: 0.15,   # Perfect fifth
                9: 0.05    # Major sixth
            }
        elif self.scale_type == 'blues':
            # Blues loves bends and blue notes
            return {
                1: 0.15,   # Half step (blue notes)
                2: 0.25,   # Whole step
                3: 0.20,   # Minor third (blue note)
                4: 0.15,   # Major third
                5: 0.10,   # Perfect fourth
                7: 0.10,   # Perfect fifth
                10: 0.05   # Minor seventh
            }
        else:
            # Default to balanced intervals
            return {
                1: 0.20, 2: 0.25, 3: 0.15, 4: 0.15, 
                5: 0.10, 7: 0.10, 12: 0.05
            }
    
    def _get_tendency_notes(self):
        """Define notes that have strong tendencies to resolve"""
        # Scale degree tendencies (relative to key_root)
        return {
            11: 0,   # Leading tone resolves to tonic
            6: 7,    # 6th degree often moves to 7th
            4: 3,    # 4th degree often resolves down to 3rd
            1: 0,    # 2nd degree resolves to tonic
        }
    
    def _calculate_phrase_arc(self, position_in_phrase, total_length):
        """Calculate where melody should go based on phrase structure"""
        if total_length <= 1:
            return 0
            
        # Create natural phrase arc: start mid, rise to peak, then fall
        progress = position_in_phrase / max(total_length - 1, 1)
        
        if progress < 0.3:
            return 0.3  # Gentle rise
        elif progress < 0.7:
            return 0.8  # Approach peak
        else:
            return -0.5  # Fall to resolution
    
    def _get_melodic_context(self):
        """Analyze recent melodic context for better decisions"""
        if len(self.last_notes) < 2:
            return {'direction': 0, 'range_used': 12, 'last_interval': 0}
        
        # Calculate recent direction
        recent_direction = 0
        for i in range(1, min(4, len(self.last_notes))):
            if self.last_notes[-i] > self.last_notes[-i-1]:
                recent_direction += 1
            elif self.last_notes[-i] < self.last_notes[-i-1]:
                recent_direction -= 1
        
        # Calculate range used
        notes_range = max(self.last_notes) - min(self.last_notes)
        
        # Last interval
        last_interval = abs(self.last_notes[-1] - self.last_notes[-2]) if len(self.last_notes) >= 2 else 0
        
        return {
            'direction': recent_direction,
            'range_used': notes_range,
            'last_interval': last_interval
        }
    
    def _choose_interval_direction(self, target_direction, context):
        """Intelligently choose interval direction"""
        # Avoid monotonous motion
        if abs(context['direction']) >= 3:
            # Force change of direction
            return -1 if context['direction'] > 0 else 1
        
        # Large interval should be followed by step in opposite direction
        if context['last_interval'] >= 5:
            last_direction = 1 if self.last_notes[-1] > self.last_notes[-2] else -1
            return -last_direction
        
        # Follow target direction with some variation
        if target_direction > 0.5:
            return 1 if random.random() < 0.8 else -1
        elif target_direction < -0.3:
            return -1 if random.random() < 0.8 else 1
        else:
            return random.choice([-1, 1])
    
    def _apply_interval_with_direction(self, current_note, interval, direction):
        """Apply interval in the specified direction"""
        candidate = current_note + (interval * direction)
        
        # Keep within reasonable range
        if candidate < min(self.scale_notes):
            candidate = current_note + interval  # Force upward
        elif candidate > max(self.scale_notes):
            candidate = current_note - interval  # Force downward
        
        # Snap to nearest scale note
        return min(self.scale_notes, key=lambda x: abs(x - candidate))
    
    def _apply_tendency_resolution(self, note):
        """Apply music theory tendency resolutions"""
        scale_degree = (note - self.key_root) % 12
        
        if scale_degree in self.tendency_notes and random.random() < 0.4:
            target_degree = self.tendency_notes[scale_degree]
            octave = (note - self.key_root) // 12
            return self.key_root + target_degree + (octave * 12)
        
        return note
    
    def generate_melodic_note(self, morse_symbol, phrase_position, phrase_length):
        """Generate a musically intelligent note"""
        # First note: start in comfortable mid-range
        if not self.last_notes:
            comfortable_notes = [n for n in self.scale_notes 
                               if self.key_root <= n <= self.key_root + 12]
            if morse_symbol == '.':
                return random.choice(comfortable_notes[:len(comfortable_notes)//2])
            else:  # dash
                return random.choice(comfortable_notes[len(comfortable_notes)//2:])
        
        current_note = self.last_notes[-1]
        context = self._get_melodic_context()
        
        # Calculate phrase arc target
        arc_target = self._calculate_phrase_arc(phrase_position, phrase_length)
        
        # Choose interval direction
        direction = self._choose_interval_direction(arc_target, context)
        
        # Choose interval size based on preferences and symbol
        intervals = list(self.preferred_intervals.keys())
        weights = list(self.preferred_intervals.values())
        
        # Modify weights based on morse symbol
        if morse_symbol == '.':
            # Dots prefer smaller intervals
            for i, interval in enumerate(intervals):
                if interval <= 3:
                    weights[i] *= 1.5
        else:  # dash
            # Dashes prefer slightly larger intervals
            for i, interval in enumerate(intervals):
                if interval >= 3:
                    weights[i] *= 1.3
        
        # Choose interval
        chosen_interval = random.choices(intervals, weights=weights)[0]
        
        # Apply interval with direction
        candidate_note = self._apply_interval_with_direction(current_note, chosen_interval, direction)
        
        # Apply tendency resolution
        final_note = self._apply_tendency_resolution(candidate_note)
        
        # Ensure it's in scale (90% of the time)
        if random.random() < 0.9:
            final_note = min(self.scale_notes, key=lambda x: abs(x - final_note))
        
        # Remember this note
        self.last_notes.append(final_note)
        
        return final_note
    
    def create_phrase_ending(self):
        """Create a satisfying phrase ending"""
        if not self.last_notes:
            return self.key_root
        
        current_note = self.last_notes[-1]
        
        # Strong preference for ending on stable tones
        stable_notes = [
            self.key_root,           # Tonic
            self.key_root + 4,       # Third
            self.key_root + 7,       # Fifth
        ]
        
        # Find closest stable note
        target = min(stable_notes, key=lambda x: abs(x - current_note))
        
        # Move stepwise toward target if possible
        if abs(current_note - target) <= 2:
            self.last_notes.append(target)
            return target
        else:
            # Take one step toward target
            step = 2 if target > current_note else -2
            intermediate = current_note + step
            # Snap to scale
            intermediate = min(self.scale_notes, key=lambda x: abs(x - intermediate))
            self.last_notes.append(intermediate)
            return intermediate

def morse_to_enhanced_midi(morse_code, output_file, **kwargs):
    """
    Enhanced MIDI generator with VASTLY IMPROVED melody generation
    """
    # Extract parameters with defaults
    tempo = kwargs.get('tempo', 120)
    key_root = kwargs.get('key_root', 60)  # C4
    scale_type = kwargs.get('scale_type', 'major')
    add_harmony = kwargs.get('add_harmony', True)
    add_bass = kwargs.get('add_bass', True)
    add_drums = kwargs.get('add_drums', False)
    chord_progression = kwargs.get('chord_progression', 'classic')
    melody_instrument = kwargs.get('melody_instrument', 0)  # Piano
    harmony_instrument = kwargs.get('harmony_instrument', 48)  # Strings
    bass_instrument = kwargs.get('bass_instrument', 32)  # Bass
    
    duration_unit = 0.25  # base duration for a dot
    time = 0
    
    # Initialize IMPROVED melody generator
    melody_ai = ImprovedMelodyGenerator(key_root, scale_type)
    
    # Create MIDI file with multiple tracks
    num_tracks = 1
    if add_harmony: num_tracks += 1
    if add_bass: num_tracks += 1
    if add_drums: num_tracks += 1
    
    midi = MIDIFile(num_tracks)
    
    # Set up tracks
    melody_track = 0
    harmony_track = 1 if add_harmony else None
    bass_track = (2 if add_harmony else 1) if add_bass else None
    drum_track = num_tracks - 1 if add_drums else None
    
    # Add tempo to all tracks
    for track in range(num_tracks):
        midi.addTempo(track, 0, tempo)
    
    # Set instruments
    midi.addProgramChange(melody_track, 0, 0, melody_instrument)
    if add_harmony:
        midi.addProgramChange(harmony_track, 1, 0, harmony_instrument)
    if add_bass:
        midi.addProgramChange(bass_track, 2, 0, bass_instrument)
    if add_drums:
        midi.addProgramChange(drum_track, 9, 0, 0)  # Standard drum kit
    
    # IMPROVED MELODY GENERATION
    volume = 100
    harmony_volume = 70
    bass_volume = 80
    drum_volume = 90
    
    # Parse morse code into phrases
    symbols = [s for s in morse_code if s in '.-']
    phrase_boundaries = []
    current_phrase = []
    
    i = 0
    for char in morse_code:
        if char in '.-':
            current_phrase.append((char, i))
            i += 1
        elif char == ' ' and current_phrase:
            # End of letter
            phrase_boundaries.append(current_phrase)
            current_phrase = []
        elif char == '/' and current_phrase:
            # End of word
            phrase_boundaries.append(current_phrase)
            current_phrase = []
    
    if current_phrase:
        phrase_boundaries.append(current_phrase)
    
    # Generate beautiful melodies for each phrase
    time = 0
    for phrase in phrase_boundaries:
        phrase_length = len(phrase)
        
        for pos, (symbol, _) in enumerate(phrase):
            # Generate melodically intelligent note
            pitch = melody_ai.generate_melodic_note(symbol, pos, phrase_length)
            
            if symbol == '.':
                note_duration = duration_unit
                rest_duration = duration_unit * 0.5
            else:  # dash
                note_duration = duration_unit * 3
                rest_duration = duration_unit * 0.5
            
            # Add musical expression
            velocity = volume + random.randint(-15, 15)  # Natural dynamics
            actual_time = time + random.uniform(-0.02, 0.02)  # Humanize timing
            
            midi.addNote(melody_track, 0, pitch, actual_time, note_duration, velocity)
            time += note_duration + rest_duration
        
        # Add phrase ending
        if phrase_length >= 2:
            ending_note = melody_ai.create_phrase_ending()
            midi.addNote(melody_track, 0, ending_note, time, duration_unit, volume - 20)
            time += duration_unit
        
        # Rest between phrases
        time += duration_unit * 3
    
    # Add harmony track (enhanced with melody awareness)
    if add_harmony:
        harmony_time = 0
        chord_duration = duration_unit * 8
        chord_index = 0
        progression = CHORD_PROGRESSIONS[chord_progression]
        
        while harmony_time < time:
            # Choose chord root from progression
            chord_root = key_root + progression[chord_index % len(progression)]
            
            # Enhanced chord selection based on scale
            if scale_type in ['minor', 'harmonic_minor', 'melodic_minor']:
                chord_notes = get_chord_notes(chord_root, 'minor')
            elif scale_type == 'blues':
                chord_notes = get_chord_notes(chord_root, 'dom7')
            else:
                chord_notes = get_chord_notes(chord_root, 'major')
            
            # Add chord with slight timing variations
            for i, note in enumerate(chord_notes):
                note_time = harmony_time + i * 0.01  # Slight roll
                midi.addNote(harmony_track, 1, note, note_time, chord_duration, harmony_volume)
            
            harmony_time += chord_duration
            chord_index += 1
    
    # Enhanced bass line
    if add_bass:
        bass_time = 0
        chord_duration = duration_unit * 8
        chord_index = 0
        progression = CHORD_PROGRESSIONS[chord_progression]
        
        while bass_time < time:
            chord_root = key_root + progression[chord_index % len(progression)] - 12
            
            # More interesting bass patterns
            if scale_type == 'jazz':
                # Walking bass
                pattern = [chord_root, chord_root + 7, chord_root + 3, chord_root + 5]
            elif scale_type == 'blues':
                # Blues bass
                pattern = [chord_root, chord_root, chord_root + 7, chord_root]
            else:
                # Standard root-fifth pattern
                pattern = [chord_root, chord_root + 7, chord_root, chord_root + 7]
            
            step_duration = chord_duration / len(pattern)
            for bass_note in pattern:
                if bass_time < time:
                    midi.addNote(bass_track, 2, bass_note, bass_time, step_duration, bass_volume)
                    bass_time += step_duration
            
            chord_index += 1
    
    # Enhanced drum patterns
    if add_drums:
        drum_time = 0
        beat_duration = duration_unit
        kick_drum = 36
        snare_drum = 38
        hi_hat = 42
        
        while drum_time < time:
            beat_in_measure = int(drum_time / beat_duration) % 4
            
            # Scale-appropriate drum patterns
            if scale_type in ['blues', 'jazz']:
                # Swing feel
                if beat_in_measure == 0:
                    midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
                elif beat_in_measure == 2:
                    midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
                
                # Swing hi-hat
                midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.6, drum_volume // 3)
                if beat_in_measure % 2 == 1:
                    midi.addNote(drum_track, 9, hi_hat, drum_time + beat_duration * 0.67, 
                               beat_duration * 0.33, drum_volume // 4)
            else:
                # Standard rock pattern
                if beat_in_measure == 0:
                    midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
                elif beat_in_measure == 2:
                    midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
                
                midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.5, drum_volume // 3)
            
            drum_time += beat_duration
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi.writeFile(f)

# Keep your existing functions for compatibility
def morse_to_ai_enhanced_midi(morse_code, output_file, **kwargs):
    """Alias for the improved function"""
    return morse_to_enhanced_midi(morse_code, output_file, **kwargs)

def midi_to_wav(midi_path, wav_path, soundfont_path=None):
    """Convert MIDI to WAV using FluidSynth"""
    if soundfont_path is None:
        print("WAV generation skipped - no soundfont provided")
        return
        
    try:
        # Check if soundfont exists
        if not os.path.exists(soundfont_path):
            print(f"Soundfont not found at {soundfont_path}")
            return
            
        # Run FluidSynth to convert MIDI to WAV
        result = subprocess.run([
            "fluidsynth",
            "-ni",
            soundfont_path,
            midi_path,
            "-F",
            wav_path,
            "-r", "44100"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FluidSynth error: {result.stderr}")
        else:
            print(f"Successfully generated WAV file: {wav_path}")
            
    except FileNotFoundError:
        print("WAV generation skipped - fluidsynth not found. Install with: brew install fluidsynth")
    except Exception as e:
        print(f"Error generating WAV: {e}")

def enhanced_midi_to_wav(midi_path, wav_path):
    """Enhanced MIDI to WAV conversion with better quality"""
    
    # Try multiple soundfont locations
    soundfont_paths = [
        os.path.expanduser("~/soundfonts/FluidR3_GM.sf2"),
        "/usr/share/soundfonts/FluidR3_GM.sf2",
        "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls",
        "FluidR3_GM.sf2"  # Local directory
    ]
    
    soundfont_path = None
    for path in soundfont_paths:
        if os.path.exists(path):
            soundfont_path = path
            break
    
    if not soundfont_path:
        print("No soundfont found - WAV generation skipped")
        return
        
    try:
        # Enhanced FluidSynth command with better quality settings
        cmd = [
            "fluidsynth",
            "-ni",  # No interactive mode
            "-g", "0.8",  # Gain
            "-r", "44100",  # Sample rate
            "-c", "2",  # Stereo channels
            "-z", "1024",  # Buffer size for better quality
            "-T", "oss",  # Audio driver
            soundfont_path,
            midi_path,
            "-F", wav_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Successfully generated enhanced WAV: {wav_path}")
        else:
            print(f"FluidSynth error: {result.stderr}")
            # Fallback: try simpler command
            simple_cmd = ["fluidsynth", "-ni", soundfont_path, midi_path, "-F", wav_path]
            result = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"Generated WAV with fallback method: {wav_path}")
            
    except subprocess.TimeoutExpired:
        print("FluidSynth timed out - try a shorter message")
    except FileNotFoundError:
        print("FluidSynth not found - install with: brew install fluidsynth (Mac) or apt install fluidsynth (Linux)")
    except Exception as e:
        print(f"Error generating WAV: {e}")

def generate_enhanced_files_from_text(text, **musical_options):
    """
    Generate enhanced musical files from text with improved melody generation
    """
    morse = text_to_morse(text)
    tmpdir = tempfile.gettempdir()
    
    # Create unique filenames based on message
    safe_text = "".join(c for c in text if c.isalnum())[:10]
    midi_path = os.path.join(tmpdir, f"enhanced_morse_{safe_text}.mid")
    wav_path = os.path.join(tmpdir, f"enhanced_morse_{safe_text}.wav")
    
    # Use the improved function
    morse_to_enhanced_midi(morse, midi_path, **musical_options)
    
    # Convert to WAV
    soundfont_path = os.path.expanduser("~/soundfonts/FluidR3_GM.sf2")
    midi_to_wav(midi_path, wav_path, soundfont_path)
    
    return midi_path, wav_path, morse

# Enhanced instrument presets with better categorization
INSTRUMENT_PRESETS = {
    # Keyboards
    'Piano': 0, 'Electric Piano': 4, 'Harpsichord': 6, 'Clavinet': 7,
    
    # Guitars
    'Acoustic Guitar': 24, 'Electric Guitar': 27, 'Electric Guitar (Jazz)': 26,
    'Electric Guitar (Clean)': 27, 'Electric Guitar (Muted)': 28,
    
    # Bass
    'Bass': 32, 'Electric Bass': 33, 'Fretless Bass': 35, 'Slap Bass': 36,
    
    # Strings
    'Violin': 40, 'Viola': 41, 'Cello': 42, 'Strings': 48, 'String Ensemble': 49,
    
    # Brass
    'Trumpet': 56, 'Trombone': 57, 'French Horn': 60, 'Brass Section': 61,
    
    # Woodwinds
    'Flute': 73, 'Clarinet': 71, 'Saxophone': 64, 'Oboe': 68,
    
    # Synths
    'Pad': 88, 'Lead': 80, 'Bass Synth': 38, 'Choir': 52,
    
    # Ethnic
    'Sitar': 104, 'Banjo': 105, 'Shamisen': 106, 'Koto': 107
}

# Enhanced key presets with enharmonic equivalents
KEY_PRESETS = {
    'C': 60, 'C#/Db': 61, 'D': 62, 'D#/Eb': 63, 'E': 64, 'F': 65,
    'F#/Gb': 66, 'G': 67, 'G#/Ab': 68, 'A': 69, 'A#/Bb': 70, 'B': 71
}
