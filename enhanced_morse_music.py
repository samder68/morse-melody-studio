from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess

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

# Musical scales
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues': [0, 3, 5, 6, 7, 10]
}

# Chord progressions
CHORD_PROGRESSIONS = {
    'classic': [0, 5, 3, 4],
    'pop': [0, 3, 5, 4],
    'folk': [0, 4, 0, 4],
    'minor': [0, 6, 3, 4]
}

# Musical styles
MUSICAL_STYLES = {
    'ballad': {'tempo_range': (70, 90)},
    'folk': {'tempo_range': (90, 120)},
    'jazz': {'tempo_range': (110, 140)},
    'ambient': {'tempo_range': (60, 80)}
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root_pitch, scale_type):
    """Generate notes for a given scale"""
    scale_intervals = SCALES[scale_type]
    return [root_pitch + interval for interval in scale_intervals]

def get_chord_notes(root_pitch, chord_type='major'):
    """Generate chord notes"""
    if chord_type == 'major':
        return [root_pitch, root_pitch + 4, root_pitch + 7]
    elif chord_type == 'minor':
        return [root_pitch, root_pitch + 3, root_pitch + 7]
    elif chord_type == 'dim':
        return [root_pitch, root_pitch + 3, root_pitch + 6]
    else:
        return [root_pitch, root_pitch + 4, root_pitch + 7]

def create_message_seed(text):
    """Create a unique seed based on the message for consistent variety"""
    seed = 0
    for char in text.upper():
        if char.isalpha():
            seed += ord(char) - ord('A')
    return seed % 1000

def morse_to_enhanced_midi(morse_code, output_file, **kwargs):
    """Enhanced MIDI generator with simple but effective variety"""
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
    
    # Set random seed based on message for consistent but different results
    message_seed = create_message_seed(original_message)
    random.seed(message_seed)
    
    duration_unit = 0.25
    time = 0
    
    # Create MIDI file
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
    
    # Add tempo
    for track in range(num_tracks):
        midi.addTempo(track, 0, tempo)
    
    # Set instruments
    midi.addProgramChange(melody_track, 0, 0, melody_instrument)
    if add_harmony:
        midi.addProgramChange(harmony_track, 1, 0, harmony_instrument)
    if add_bass:
        midi.addProgramChange(bass_track, 2, 0, bass_instrument)
    if add_drums:
        midi.addProgramChange(drum_track, 9, 0, 0)
    
    # Get scale notes
    scale_notes = get_scale_notes(key_root, scale_type)
    progression = CHORD_PROGRESSIONS[chord_progression]
    chord_duration = duration_unit * 8
    
    # Generate melody with more musical variety
    volume = 100
    harmony_volume = 70
    bass_volume = 80
    drum_volume = 90
    
    # Create different note ranges based on scale type for variety
    if scale_type == 'major':
        dot_notes = scale_notes[:4] + [n + 12 for n in scale_notes[:3]]  # Lower and mid range
        dash_notes = scale_notes[2:] + [n + 12 for n in scale_notes[2:5]]  # Mid and higher range
    elif scale_type == 'minor':
        dot_notes = scale_notes[:3] + [n + 12 for n in scale_notes[:2]]  # Even lower for minor
        dash_notes = scale_notes[3:] + [n + 12 for n in scale_notes[3:]]  # Higher contrast
    elif scale_type == 'pentatonic':
        dot_notes = scale_notes[:3] + [n + 12 for n in scale_notes[:2]]
        dash_notes = scale_notes[2:] + [n + 12 for n in scale_notes[2:]]
    else:  # blues
        dot_notes = scale_notes[:3] + [n + 12 for n in scale_notes[:2]]
        dash_notes = scale_notes[3:] + [n + 12 for n in scale_notes[2:]]
    
    # Track previous notes for better melodic flow
    previous_notes = []
    
    for i, symbol in enumerate(morse_code):
        if symbol == '.':
            # Choose from dot range, but prefer stepwise motion
            if previous_notes:
                last_note = previous_notes[-1]
                # Find notes within 3 semitones of last note
                nearby_notes = [n for n in dot_notes if abs(n - last_note) <= 4]
                if nearby_notes:
                    pitch = random.choice(nearby_notes)
                else:
                    pitch = random.choice(dot_notes)
            else:
                pitch = random.choice(dot_notes)
            
            # Add some velocity variation
            note_velocity = volume + random.randint(-15, 15)
            midi.addNote(melody_track, 0, pitch, time, duration_unit, note_velocity)
            previous_notes.append(pitch)
            time += duration_unit + duration_unit
            
        elif symbol == '-':
            # Choose from dash range, allow bigger leaps
            if previous_notes:
                last_note = previous_notes[-1]
                # For dashes, allow larger intervals but still musical
                candidates = [n for n in dash_notes if abs(n - last_note) <= 7]
                if candidates:
                    pitch = random.choice(candidates)
                else:
                    pitch = random.choice(dash_notes)
            else:
                pitch = random.choice(dash_notes)
            
            # Dashes get slightly more emphasis
            note_velocity = volume + random.randint(-10, 20)
            midi.addNote(melody_track, 0, pitch, time, duration_unit * 3, note_velocity)
            previous_notes.append(pitch)
            time += duration_unit * 3 + duration_unit
            
        elif symbol == ' ':
            time += duration_unit * 3
            # Reset note choice occasionally for phrase variety
            if len(previous_notes) > 6:
                previous_notes = previous_notes[-2:]
                
        elif symbol == '/':
            time += duration_unit * 7
            # Clear previous notes for new phrase
            previous_notes = []
    
    # Add harmony with some variation
    if add_harmony:
        harmony_time = 0
        chord_index = 0
        while harmony_time < time:
            chord_root = key_root + progression[chord_index % len(progression)]
            
            # Vary chord types based on position and scale
            if scale_type == 'minor':
                if chord_index % 4 in [0, 2]:
                    chord_notes = get_chord_notes(chord_root, 'minor')
                else:
                    chord_notes = get_chord_notes(chord_root, 'major')
            else:
                if chord_index % 4 == 1:
                    chord_notes = get_chord_notes(chord_root, 'minor')
                else:
                    chord_notes = get_chord_notes(chord_root, 'major')
            
            # Add slight timing variation to harmony
            for j, note in enumerate(chord_notes):
                timing_offset = j * 0.02  # Slight arpeggio effect
                midi.addNote(harmony_track, 1, note, harmony_time + timing_offset, 
                           chord_duration, harmony_volume + random.randint(-10, 10))
            
            harmony_time += chord_duration
            chord_index += 1
    
    # Add bass with different patterns
    if add_bass:
        bass_time = 0
        chord_index = 0
        bass_pattern_duration = chord_duration / 4
        
        while bass_time < time:
            chord_root = key_root + progression[chord_index % len(progression)] - 12
            
            # Vary bass patterns
            pattern_choice = chord_index % 3
            if pattern_choice == 0:
                # Root-fifth pattern
                bass_notes = [chord_root, chord_root + 7, chord_root, chord_root + 7]
            elif pattern_choice == 1:
                # Root-third-fifth pattern
                bass_notes = [chord_root, chord_root + 4, chord_root + 7, chord_root + 4]
            else:
                # Walking pattern
                bass_notes = [chord_root, chord_root + 2, chord_root + 4, chord_root + 5]
            
            for bass_note in bass_notes:
                if bass_time < time:
                    bass_velocity = bass_volume + random.randint(-15, 15)
                    midi.addNote(bass_track, 2, bass_note, bass_time, bass_pattern_duration, bass_velocity)
                    bass_time += bass_pattern_duration
            
            chord_index += 1
    
    # Add drums with variation
    if add_drums:
        drum_time = 0
        beat_duration = duration_unit
        kick_drum = 36
        snare_drum = 38
        hi_hat = 42
        
        while drum_time < time:
            beat_in_measure = int(drum_time / beat_duration) % 4
            measure_num = int(drum_time / (beat_duration * 4))
            
            # Basic pattern with some variation every few measures
            if beat_in_measure == 0:
                midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
            elif beat_in_measure == 2:
                midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
            
            # Hi-hat with some variation
            hat_velocity = drum_volume // 2 + random.randint(-10, 10)
            midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.5, hat_velocity)
            
            # Add occasional extra kick or snare for variety
            if measure_num % 4 == 3 and beat_in_measure == 3:  # Every 4th measure
                if random.choice([True, False]):
                    midi.addNote(drum_track, 9, kick_drum, drum_time + beat_duration * 0.5, 
                               beat_duration * 0.5, drum_volume // 2)
            
            drum_time += beat_duration
    
    # Reset random seed to avoid affecting other parts
    random.seed()
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi.writeFile(f)

def midi_to_wav(midi_path, wav_path, soundfont_path=None):
    """Convert MIDI to WAV - with error handling for cloud deployment"""
    if soundfont_path is None:
        return False
        
    try:
        if not os.path.exists(soundfont_path):
            return False
            
        result = subprocess.run([
            "fluidsynth", "-ni", soundfont_path, midi_path, "-F", wav_path, "-r", "44100"
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0
    except:
        return False

def generate_enhanced_files_from_text(text, **musical_options):
    """Generate files from text with enhanced musical variety"""
    morse = text_to_morse(text)
    tmpdir = tempfile.gettempdir()
    
    safe_text = "".join(c for c in text if c.isalnum())[:10]
    midi_path = os.path.join(tmpdir, f"morse_{safe_text}.mid")
    wav_path = os.path.join(tmpdir, f"morse_{safe_text}.wav")
    
    # Pass the original message for variety
    musical_options['original_message'] = text
    
    # Generate MIDI
    morse_to_enhanced_midi(morse, midi_path, **musical_options)
    
    # Try to generate WAV
    wav_success = False
    try:
        soundfont_paths = [
            os.path.expanduser("~/soundfonts/FluidR3_GM.sf2"),
            "/usr/share/soundfonts/FluidR3_GM.sf2"
        ]
        
        for soundfont_path in soundfont_paths:
            if os.path.exists(soundfont_path):
                wav_success = midi_to_wav(midi_path, wav_path, soundfont_path)
                if wav_success:
                    break
    except:
        pass
    
    if not wav_success:
        wav_path = None
    
    return midi_path, wav_path, morse

# Instrument presets
INSTRUMENT_PRESETS = {
    'Piano': 0, 'Electric Piano': 4, 'Harpsichord': 6,
    'Acoustic Guitar': 24, 'Electric Guitar': 27, 'Bass': 32,
    'Violin': 40, 'Strings': 48, 'Choir': 52, 'Trumpet': 56,
    'Flute': 73, 'Pad': 88, 'Lead': 80
}

# Key presets
KEY_PRESETS = {
    'C': 60, 'C#/Db': 61, 'D': 62, 'D#/Eb': 63, 'E': 64, 'F': 65,
    'F#/Gb': 66, 'G': 67, 'G#/Ab': 68, 'A': 69, 'A#/Bb': 70, 'B': 71
}
