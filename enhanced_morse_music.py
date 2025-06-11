from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess
import math
import hashlib

# Morse code dictionary
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

# Enhanced musical scales with more variety
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'minor_pentatonic': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11]
}

# More sophisticated chord progressions
CHORD_PROGRESSIONS = {
    'classic': [0, 5, 3, 4],  # I-vi-IV-V
    'pop': [0, 3, 5, 4],      # I-IV-vi-V
    'folk': [0, 4, 0, 4],     # I-V-I-V
    'minor': [0, 6, 3, 4],    # i-VI-III-IV
    'jazz': [0, 3, 5, 1],     # I-IV-vi-ii
    'modern': [5, 3, 0, 4],   # vi-IV-I-V
    'modal': [0, 6, 4, 0],    # I-VII-V-I
    'indie': [0, 2, 5, 3]     # I-iii-vi-IV
}

# Advanced music theory for realistic composition
class MusicalPhraseMaker:
    def __init__(self, scale_notes, message_seed):
        self.scale_notes = scale_notes
        self.extended_scale = scale_notes + [n + 12 for n in scale_notes] + [n - 12 for n in scale_notes]
        self.phrase_direction = 1  # 1 for ascending tendency, -1 for descending
        self.phrase_position = 0   # Track position in musical phrase
        self.last_interval = 0     # Track melodic intervals
        
        # Set seed for consistent but varied results per message
        random.seed(message_seed)
        
        # Define note weights based on music theory
        self.note_weights = self._calculate_note_weights()
        
    def _calculate_note_weights(self):
        """Calculate weights for notes based on scale degree importance"""
        weights = {}
        for i, note in enumerate(self.scale_notes):
            # Tonic, dominant, mediant get higher weights
            if i % 7 == 0:      # Tonic
                weights[note] = 10
            elif i % 7 == 4:    # Dominant  
                weights[note] = 8
            elif i % 7 == 2:    # Mediant
                weights[note] = 6
            elif i % 7 == 5:    # Submediant
                weights[note] = 5
            else:               # Other degrees
                weights[note] = 3
        return weights
    
    def get_melodic_note(self, is_dash=False, previous_note=None):
        """Generate melodically intelligent note choices"""
        candidates = []
        
        if previous_note is None:
            # Start with a strong scale degree
            candidates = [n for n in self.scale_notes if self.note_weights.get(n, 1) >= 6]
        else:
            # Generate candidates based on good voice leading
            for note in self.extended_scale:
                interval = abs(note - previous_note)
                
                # Prefer stepwise motion and small leaps
                if interval <= 2:      # Steps
                    weight = 10
                elif interval <= 4:    # Small leaps
                    weight = 7
                elif interval <= 7:    # Larger leaps
                    weight = 4 if is_dash else 2  # Dashes can take bigger leaps
                else:                  # Large jumps
                    weight = 1 if is_dash else 0
                
                # Add scale degree importance
                scale_weight = self.note_weights.get(note % 12, 1)
                total_weight = weight * scale_weight
                
                # Add to candidates with repetition based on weight
                candidates.extend([note] * max(1, total_weight // 2))
        
        if not candidates:
            candidates = self.scale_notes
            
        chosen_note = random.choice(candidates)
        
        # Update phrase tracking
        if previous_note:
            self.last_interval = chosen_note - previous_note
            # Adjust phrase direction based on melodic flow
            if abs(self.last_interval) > 4:
                self.phrase_direction *= -1  # Change direction after big leap
        
        self.phrase_position += 1
        return chosen_note

def create_advanced_message_seed(text):
    """Create sophisticated seed that varies with message content"""
    # Use message content to create unique but deterministic patterns
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Extract different aspects for different musical elements
    seed_base = int(text_hash[:8], 16) % 10000
    rhythm_seed = int(text_hash[8:16], 16) % 1000
    harmony_seed = int(text_hash[16:24], 16) % 1000
    
    return {
        'base': seed_base,
        'rhythm': rhythm_seed, 
        'harmony': harmony_seed
    }

def generate_humanized_timing(base_duration, message_seeds):
    """Add subtle timing variations that feel human"""
    random.seed(message_seeds['rhythm'])
    
    # Very subtle timing variations (±2-5%)
    variation = random.uniform(0.96, 1.04)
    humanized_duration = base_duration * variation
    
    return humanized_duration

def create_sophisticated_harmony(chord_root, measure_num, scale_type, harmony_seeds):
    """Generate more sophisticated harmony with voice leading"""
    random.seed(harmony_seeds['harmony'] + measure_num)
    
    # Basic triad
    if scale_type in ['minor', 'dorian']:
        if measure_num % 4 in [0, 2]:  # i and iii chords often minor
            chord_notes = [chord_root, chord_root + 3, chord_root + 7]
        else:
            chord_notes = [chord_root, chord_root + 4, chord_root + 7]
    else:
        if measure_num % 4 == 1:  # ii chord often minor
            chord_notes = [chord_root, chord_root + 3, chord_root + 7] 
        else:
            chord_notes = [chord_root, chord_root + 4, chord_root + 7]
    
    # Add extensions for richer harmony
    if measure_num % 8 == 7:  # Add seventh on resolution
        if scale_type in ['minor', 'dorian']:
            chord_notes.append(chord_root + 10)  # Minor 7th
        else:
            chord_notes.append(chord_root + 11)  # Major 7th
    elif measure_num % 6 == 0:  # Occasional add9
        chord_notes.append(chord_root + 14)  # Add 9 (octave + 2nd)
    
    return chord_notes

def create_musical_bass_line(chord_root, scale_notes, measure_num, bass_seeds):
    """Generate sophisticated bass lines with musical patterns"""
    random.seed(bass_seeds['harmony'] + measure_num * 7)
    
    bass_root = chord_root - 12
    
    # Different bass patterns based on musical context
    pattern_type = measure_num % 6
    
    if pattern_type == 0:
        # Root movement with passing tones
        return [bass_root, bass_root + 2, bass_root + 4, bass_root + 5]
    elif pattern_type == 1:
        # Arpeggio pattern
        return [bass_root, bass_root + 7, bass_root + 4, bass_root + 7]
    elif pattern_type == 2:
        # Walking bass
        return [bass_root, bass_root + 2, bass_root + 4, bass_root + 7]
    elif pattern_type == 3:
        # Pedal tone with upper movement
        return [bass_root, bass_root, bass_root + 7, bass_root]
    elif pattern_type == 4:
        # Syncopated pattern
        return [bass_root, bass_root + 7, bass_root + 2, bass_root + 4]
    else:
        # Octave movement
        return [bass_root, bass_root + 12, bass_root + 7, bass_root]

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root_pitch, scale_type):
    """Generate notes for a given scale"""
    scale_intervals = SCALES[scale_type]
    return [root_pitch + interval for interval in scale_intervals]

def morse_to_ultra_realistic_midi(morse_code, output_file, **kwargs):
    """Generate ultra-realistic MIDI with advanced musical intelligence"""
    
    # Extract parameters
    tempo = kwargs.get('tempo', 120)
    key_root = kwargs.get('key_root', 60)
    scale_type = kwargs.get('scale_type', 'major')
    add_harmony = kwargs.get('add_harmony', True)
    add_bass = kwargs.get('add_bass', True)
    add_drums = kwargs.get('add_drums', False)
    chord_progression = kwargs.get('chord_progression', 'classic')
    melody_instrument = kwargs.get('melody_instrument', 0)
    harmony_instrument = kwargs.get('harmony_instrument', 48)
    bass_instrument = kwargs.get('bass_instrument', 32)
    original_message = kwargs.get('original_message', 'DEFAULT')
    style = kwargs.get('style', 'folk')
    
    # Create sophisticated seeds
    message_seeds = create_advanced_message_seed(original_message)
    
    # Initialize musical phrase maker
    scale_notes = get_scale_notes(key_root, scale_type)
    phrase_maker = MusicalPhraseMaker(scale_notes, message_seeds['base'])
    
    # Musical timing
    base_duration = 60.0 / tempo  # Convert to seconds per beat
    dot_duration = base_duration * 0.5
    dash_duration = base_duration * 1.5
    
    time = 0
    
    # Create MIDI file
    num_tracks = 1
    if add_harmony: num_tracks += 1
    if add_bass: num_tracks += 1
    if add_drums: num_tracks += 1
    
    midi = MIDIFile(num_tracks)
    
    # Track setup
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
    
    # Generate melody with musical intelligence
    progression = CHORD_PROGRESSIONS[chord_progression]
    previous_note = None
    note_in_phrase = 0
    
    # Dynamic volume based on message content and position
    base_volume = 85
    
    for i, symbol in enumerate(morse_code):
        if symbol == '.':
            # Dots: shorter, more delicate
            pitch = phrase_maker.get_melodic_note(is_dash=False, previous_note=previous_note)
            
            # Humanized timing and volume
            duration = generate_humanized_timing(dot_duration, message_seeds)
            volume = base_volume + random.randint(-15, 10)
            
            # Add slight velocity curve within phrases
            phrase_position = note_in_phrase % 8
            if phrase_position < 4:
                volume += (phrase_position * 2)  # Crescendo
            else:
                volume -= ((phrase_position - 4) * 1)  # Diminuendo
            
            midi.addNote(melody_track, 0, pitch, time, duration, max(40, min(127, volume)))
            previous_note = pitch
            time += duration + generate_humanized_timing(dot_duration * 0.5, message_seeds)
            note_in_phrase += 1
            
        elif symbol == '-':
            # Dashes: longer, more prominent
            pitch = phrase_maker.get_melodic_note(is_dash=True, previous_note=previous_note)
            
            # Humanized timing and volume
            duration = generate_humanized_timing(dash_duration, message_seeds)
            volume = base_volume + random.randint(-10, 20)
            
            # Dashes get slight emphasis
            phrase_position = note_in_phrase % 8
            volume += 5  # Slight emphasis for dashes
            if phrase_position < 4:
                volume += (phrase_position * 2)
            else:
                volume -= ((phrase_position - 4) * 1)
            
            midi.addNote(melody_track, 0, pitch, time, duration, max(50, min(127, volume)))
            previous_note = pitch
            time += duration + generate_humanized_timing(dot_duration * 0.5, message_seeds)
            note_in_phrase += 1
            
        elif symbol == ' ':
            # Letter space
            time += generate_humanized_timing(dot_duration * 2, message_seeds)
            note_in_phrase = 0  # Reset phrase counter
            
        elif symbol == '/':
            # Word space  
            time += generate_humanized_timing(dot_duration * 4, message_seeds)
            note_in_phrase = 0
            # Reset phrase maker for new phrase
            phrase_maker.phrase_position = 0
    
    # Add sophisticated harmony
    if add_harmony:
        harmony_time = 0
        chord_index = 0
        chord_duration = base_duration * 4  # Whole note chords
        measure_num = 0
        
        while harmony_time < time:
            chord_root = key_root + progression[chord_index % len(progression)]
            chord_notes = create_sophisticated_harmony(
                chord_root, measure_num, scale_type, message_seeds
            )
            
            # Humanized chord timing (slight arpeggiation)
            for j, note in enumerate(chord_notes):
                timing_offset = j * 0.03  # Very slight roll
                note_duration = generate_humanized_timing(chord_duration, message_seeds)
                volume = 65 + random.randint(-10, 15)
                
                midi.addNote(harmony_track, 1, note, 
                           harmony_time + timing_offset, note_duration, volume)
            
            harmony_time += chord_duration
            chord_index += 1
            measure_num += 1
    
    # Add musical bass line
    if add_bass:
        bass_time = 0
        chord_index = 0
        bass_beat_duration = base_duration
        measure_num = 0
        
        while bass_time < time:
            chord_root = key_root + progression[chord_index % len(progression)]
            bass_pattern = create_musical_bass_line(
                chord_root, scale_notes, measure_num, message_seeds
            )
            
            for bass_note in bass_pattern:
                if bass_time < time:
                    duration = generate_humanized_timing(bass_beat_duration, message_seeds)
                    volume = 75 + random.randint(-15, 15)
                    
                    midi.addNote(bass_track, 2, bass_note, bass_time, duration, volume)
                    bass_time += bass_beat_duration
            
            chord_index += 1
            measure_num += 1
    
    # Add musical drums (if requested)
    if add_drums:
        drum_time = 0
        beat_duration = base_duration
        kick_drum = 36
        snare_drum = 38
        hi_hat_closed = 42
        hi_hat_open = 46
        crash = 49
        
        measure_count = 0
        
        while drum_time < time:
            beat_in_measure = int((drum_time / beat_duration) % 4)
            
            # Kick drum pattern
            if beat_in_measure == 0:
                volume = 90 + random.randint(-10, 10)
                midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration * 0.3, volume)
            elif beat_in_measure == 2 and measure_count % 2 == 1:  # Syncopated kick
                volume = 80 + random.randint(-5, 10)
                midi.addNote(drum_track, 9, kick_drum, drum_time + beat_duration * 0.5, 
                           beat_duration * 0.3, volume)
            
            # Snare on beats 2 and 4
            if beat_in_measure in [1, 3]:
                volume = 85 + random.randint(-10, 15)
                midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration * 0.2, volume)
            
            # Hi-hat pattern
            for subdivision in [0, 0.25, 0.5, 0.75]:
                hat_time = drum_time + (beat_duration * subdivision)
                if hat_time < time:
                    # Mix closed and open hi-hats
                    hat_type = hi_hat_open if subdivision == 0.5 and beat_in_measure % 2 == 1 else hi_hat_closed
                    volume = 45 + random.randint(-10, 15)
                    midi.addNote(drum_track, 9, hat_type, hat_time, beat_duration * 0.1, volume)
            
            # Occasional crash at phrase beginnings
            if beat_in_measure == 0 and measure_count % 8 == 0 and measure_count > 0:
                volume = 70 + random.randint(-10, 10)
                midi.addNote(drum_track, 9, crash, drum_time, beat_duration * 2, volume)
            
            drum_time += beat_duration
            if beat_in_measure == 3:
                measure_count += 1
    
    # Reset random seed
    random.seed()
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi.writeFile(f)

def midi_to_wav(midi_path, wav_path, soundfont_path=None):
    """Convert MIDI to WAV with better error handling"""
    if soundfont_path is None:
        return False
        
    try:
        if not os.path.exists(soundfont_path):
            return False
            
        result = subprocess.run([
            "fluidsynth", "-ni", soundfont_path, midi_path, "-F", wav_path, 
            "-r", "44100", "-g", "0.8"  # Slightly reduce gain for better mix
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0
    except:
        return False

def generate_enhanced_files_from_text(text, **musical_options):
    """Generate files with ultra-realistic musical output"""
    morse = text_to_morse(text)
    tmpdir = tempfile.gettempdir()
    
    safe_text = "".join(c for c in text if c.isalnum())[:10]
    midi_path = os.path.join(tmpdir, f"morse_realistic_{safe_text}.mid")
    wav_path = os.path.join(tmpdir, f"morse_realistic_{safe_text}.wav")
    
    # Pass the original message for musical intelligence
    musical_options['original_message'] = text
    
    # Generate ultra-realistic MIDI
    morse_to_ultra_realistic_midi(morse, midi_path, **musical_options)
    
    # Try to generate WAV with better soundfont search
    wav_success = False
    try:
        soundfont_paths = [
            os.path.expanduser("~/soundfonts/FluidR3_GM.sf2"),
            "/usr/share/soundfonts/FluidR3_GM.sf2",
            "/usr/share/soundfonts/default.sf2",
            os.path.expanduser("~/Music/soundfonts/FluidR3_GM.sf2")
        ]
        
        if 'soundfont_override' in kwargs and kwargs['soundfont_override']:
        soundfont_paths.insert(0, kwargs['soundfont_override'])

    for soundfont_path in soundfont_paths:
            if os.path.exists(soundfont_path):
                print(f'✅ Using SoundFont: {soundfont_path}')
        wav_success = midi_to_wav(midi_path, wav_path, soundfont_path)
                if wav_success:
                    break
    except:
        pass
    
    if not wav_success:
        wav_path = None
    
    return midi_path, wav_path, morse

# Keep existing presets for compatibility
INSTRUMENT_PRESETS = {
    'Piano': 0, 'Electric Piano': 4, 'Harpsichord': 6,
    'Acoustic Guitar': 24, 'Electric Guitar': 27, 'Bass': 32,
    'Violin': 40, 'Strings': 48, 'Choir': 52, 'Trumpet': 56,
    'Flute': 73, 'Pad': 88, 'Lead': 80
}

KEY_PRESETS = {
    'C': 60, 'C#/Db': 61, 'D': 62, 'D#/Eb': 63, 'E': 64, 'F': 65,
    'F#/Gb': 66, 'G': 67, 'G#/Ab': 68, 'A': 69, 'A#/Bb': 70, 'B': 71
}
