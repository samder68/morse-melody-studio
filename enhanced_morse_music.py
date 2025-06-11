from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess
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

# Enhanced musical scales with more character
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues': [0, 3, 5, 6, 7, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10]
}

# More sophisticated chord progressions
CHORD_PROGRESSIONS = {
    'classic': [0, 5, 3, 4],      # I-vi-IV-V
    'pop': [0, 3, 5, 4],          # I-IV-vi-V  
    'folk': [0, 4, 0, 4],         # I-V-I-V
    'minor': [0, 6, 3, 4],        # i-VII-IV-V
    'jazz': [0, 5, 1, 4],         # I-vi-ii-V
    'blues': [0, 0, 4, 0, 5, 4, 0, 5],  # 12-bar blues
    'emotional': [0, 3, 5, 1],    # I-IV-vi-ii
    'mysterious': [0, 1, 5, 4],   # i-ii-vi-V
    'uplifting': [0, 4, 5, 0],    # I-V-vi-I
    'melancholy': [5, 3, 0, 4]    # vi-IV-I-V
}

# Style-specific parameters that create distinct sounds
MUSICAL_STYLES = {
    'ballad': {
        'tempo_range': (70, 90),
        'note_range': (-5, 10),      # Narrow range, mid register
        'rhythm_pattern': 'legato',   # Smooth, connected
        'harmony_density': 'rich',    # Full chords
        'bass_style': 'simple',
        'preferred_progression': 'emotional'
    },
    'folk': {
        'tempo_range': (90, 120),
        'note_range': (-3, 8),       # Natural singing range
        'rhythm_pattern': 'natural',  # Slightly uneven, human-like
        'harmony_density': 'medium',  # Some open chords
        'bass_style': 'alternating',
        'preferred_progression': 'folk'
    },
    'jazz': {
        'tempo_range': (110, 140),
        'note_range': (-8, 15),      # Wide range, more adventurous
        'rhythm_pattern': 'syncopated', # Off-beat accents
        'harmony_density': 'complex', # 7ths, 9ths, extensions
        'bass_style': 'walking',
        'preferred_progression': 'jazz'
    },
    'ambient': {
        'tempo_range': (60, 80),
        'note_range': (-10, 12),     # Very wide, ethereal
        'rhythm_pattern': 'floating', # Minimal, sustained
        'harmony_density': 'sparse',  # Lots of space
        'bass_style': 'minimal',
        'preferred_progression': 'mysterious'
    }
}

class MessageBasedComposer:
    """Creates music that varies based on the actual message content"""
    
    def __init__(self, message, style='ballad'):
        self.message = message.upper()
        self.style = style
        self.style_params = MUSICAL_STYLES[style]
        self.message_seed = self.create_message_seed()
        random.seed(self.message_seed)  # Deterministic but message-dependent
        
        # Analyze message characteristics
        self.message_mood = self.analyze_message_mood()
        self.message_complexity = self.analyze_message_complexity()
        self.letter_weights = self.create_letter_based_weights()
        
    def create_message_seed(self):
        """Create a unique seed based on message content"""
        return int(hashlib.md5(self.message.encode()).hexdigest()[:8], 16)
    
    def analyze_message_mood(self):
        """Determine mood based on message content"""
        positive_words = ['LOVE', 'HOPE', 'JOY', 'HAPPY', 'BRIGHT', 'WARM', 'GOOD', 'YES', 'WIN']
        negative_words = ['SAD', 'DARK', 'COLD', 'NO', 'STOP', 'END', 'FEAR', 'LOST', 'HELP']
        urgent_words = ['URGENT', 'NOW', 'FAST', 'QUICK', 'RUN', 'GO', 'MOVE', 'HURRY']
        
        mood_score = 0
        urgency_score = 0
        
        for word in positive_words:
            if word in self.message:
                mood_score += 2
        
        for word in negative_words:
            if word in self.message:
                mood_score -= 2
                
        for word in urgent_words:
            if word in self.message:
                urgency_score += 1
        
        # Determine overall mood
        if mood_score > 1:
            mood = 'positive'
        elif mood_score < -1:
            mood = 'negative'
        else:
            mood = 'neutral'
            
        return {'mood': mood, 'urgency': urgency_score, 'score': mood_score}
    
    def analyze_message_complexity(self):
        """Analyze message for musical complexity hints"""
        length = len(self.message.replace(' ', ''))
        unique_letters = len(set(self.message.replace(' ', '')))
        
        return {
            'length': length,
            'unique_letters': unique_letters,
            'complexity_ratio': unique_letters / max(length, 1),
            'has_numbers': any(c.isdigit() for c in self.message),
            'word_count': len(self.message.split())
        }
    
    def create_letter_based_weights(self):
        """Create note selection weights based on letter frequency in message"""
        letter_counts = {}
        for char in self.message.replace(' ', ''):
            if char.isalpha():
                letter_counts[char] = letter_counts.get(char, 0) + 1
        
        # Map letters to musical intervals (A=0, B=1, etc.)
        note_weights = {}
        for letter, count in letter_counts.items():
            note_index = ord(letter) - ord('A')
            scale_degree = note_index % 7  # Map to scale degrees
            note_weights[scale_degree] = count
            
        return note_weights
    
    def get_base_note_for_message(self, key_root, scale_notes):
        """Choose a starting note based on message characteristics"""
        mood = self.message_mood['mood']
        
        if mood == 'positive':
            # Start higher, more optimistic
            return random.choice(scale_notes[2:5])
        elif mood == 'negative':
            # Start lower, more somber
            return random.choice(scale_notes[:3])
        else:
            # Start in middle
            return random.choice(scale_notes[1:4])
    
    def choose_note_for_symbol(self, symbol, position, prev_notes, scale_notes, key_root):
        """Choose notes based on message content and musical logic"""
        note_range = self.style_params['note_range']
        min_note = key_root + note_range[0]
        max_note = key_root + note_range[1]
        
        # Get base probabilities from message analysis
        available_notes = [n for n in scale_notes if min_note <= n <= max_note]
        
        if not prev_notes:
            return self.get_base_note_for_message(key_root, available_notes)
        
        last_note = prev_notes[-1]
        
        # Create melodic movement based on message characteristics
        if symbol == '.':
            # Dots: generally stepwise, influenced by message mood
            if self.message_mood['mood'] == 'positive':
                # Slight upward tendency
                candidates = [n for n in available_notes if n >= last_note - 2 and n <= last_note + 4]
            elif self.message_mood['mood'] == 'negative':
                # Slight downward tendency
                candidates = [n for n in available_notes if n >= last_note - 4 and n <= last_note + 2]
            else:
                # Balanced movement
                candidates = [n for n in available_notes if n >= last_note - 3 and n <= last_note + 3]
        
        else:  # Dash
            # Dashes: allow larger intervals, more dramatic
            if self.message_mood['urgency'] > 0:
                # More dramatic leaps for urgent messages
                candidates = [n for n in available_notes if abs(n - last_note) >= 3]
            else:
                # Moderate movement
                candidates = [n for n in available_notes if n >= last_note - 5 and n <= last_note + 7]
        
        # Fall back to available notes if no candidates
        if not candidates:
            candidates = available_notes
        
        # Weight selection based on letter frequency in message
        if self.letter_weights:
            weighted_candidates = []
            for note in candidates:
                scale_degree = (note - key_root) % 7
                weight = self.letter_weights.get(scale_degree, 1)
                weighted_candidates.extend([note] * weight)
            candidates = weighted_candidates if weighted_candidates else candidates
        
        return random.choice(candidates)

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root_pitch, scale_type):
    """Generate notes for a given scale"""
    scale_intervals = SCALES[scale_type]
    return [root_pitch + interval for interval in scale_intervals]

def get_chord_notes(root_pitch, chord_type='major', style='ballad'):
    """Generate chord notes with style-specific voicings"""
    base_chord = None
    
    if chord_type == 'major':
        base_chord = [root_pitch, root_pitch + 4, root_pitch + 7]
    elif chord_type == 'minor':
        base_chord = [root_pitch, root_pitch + 3, root_pitch + 7]
    elif chord_type == 'dim':
        base_chord = [root_pitch, root_pitch + 3, root_pitch + 6]
    else:
        base_chord = [root_pitch, root_pitch + 4, root_pitch + 7]
    
    # Add style-specific extensions
    if style == 'jazz':
        # Add 7ths and sometimes 9ths
        if chord_type == 'major':
            base_chord.append(root_pitch + 11)  # Major 7th
            if random.random() < 0.4:
                base_chord.append(root_pitch + 14)  # 9th
        elif chord_type == 'minor':
            base_chord.append(root_pitch + 10)  # Minor 7th
    
    elif style == 'ballad':
        # Sometimes add 2nds for color
        if random.random() < 0.3:
            base_chord.append(root_pitch + 2)
    
    return base_chord

def create_dynamic_rhythm(style, morse_symbol, position):
    """Create rhythm variations based on style and context"""
    base_duration = 0.25
    
    if style == 'jazz':
        # Swing feel - slightly uneven timing
        if position % 2 == 0:
            return base_duration * 1.15  # Slightly longer
        else:
            return base_duration * 0.85  # Slightly shorter
    
    elif style == 'folk':
        # Natural human timing variations
        variation = random.uniform(0.9, 1.1)
        return base_duration * variation
    
    elif style == 'ambient':
        # More sustained notes
        return base_duration * random.uniform(1.2, 2.0)
    
    else:  # ballad
        # Expressive timing
        if morse_symbol == '-':
            return base_duration * 3.2  # Slightly longer dashes
        else:
            return base_duration * 1.1   # Slightly longer dots
    
    return base_duration

def morse_to_enhanced_midi(morse_code, output_file, **kwargs):
    """Enhanced MIDI generator with message-based composition"""
    # Extract parameters
    tempo = kwargs.get('tempo', 120)
    key_root = kwargs.get('key_root', 60)
    scale_type = kwargs.get('scale_type', 'major')
    add_harmony = kwargs.get('add_harmony', True)
    add_bass = kwargs.get('add_bass', True)
    add_drums = kwargs.get('add_drums', False)
    chord_progression_name = kwargs.get('chord_progression', 'classic')
    melody_instrument = kwargs.get('melody_instrument', 0)
    harmony_instrument = kwargs.get('harmony_instrument', 48)
    bass_instrument = kwargs.get('bass_instrument', 32)
    style = kwargs.get('style', 'ballad')
    original_message = kwargs.get('original_message', 'DEFAULT')
    
    # Create message-based composer
    composer = MessageBasedComposer(original_message, style)
    
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
    
    # Get scale notes and chord progression
    scale_notes = get_scale_notes(key_root, scale_type)
    
    # Use style-preferred progression or specified one
    style_params = MUSICAL_STYLES[style]
    if chord_progression_name == 'classic':
        chord_progression_name = style_params.get('preferred_progression', 'classic')
    
    progression = CHORD_PROGRESSIONS[chord_progression_name]
    chord_duration = duration_unit * 8
    
    # Generate message-influenced melody
    volume = 100
    harmony_volume = 70
    bass_volume = 80
    drum_volume = 90
    
    melody_notes = []
    position = 0
    
    for symbol in morse_code:
        if symbol == '.':
            # Choose note based on message analysis
            pitch = composer.choose_note_for_symbol('.', position, melody_notes, scale_notes, key_root)
            note_duration = create_dynamic_rhythm(style, '.', position)
            
            # Add expression based on message mood
            if composer.message_mood['mood'] == 'positive':
                velocity = random.randint(85, 110)
            elif composer.message_mood['mood'] == 'negative':
                velocity = random.randint(60, 85)
            else:
                velocity = random.randint(70, 95)
                
            midi.addNote(melody_track, 0, pitch, time, note_duration, velocity)
            melody_notes.append(pitch)
            time += note_duration + duration_unit * 0.5
            position += 1
            
        elif symbol == '-':
            pitch = composer.choose_note_for_symbol('-', position, melody_notes, scale_notes, key_root)
            note_duration = create_dynamic_rhythm(style, '-', position)
            
            # Dashes get slightly more emphasis
            if composer.message_mood['mood'] == 'positive':
                velocity = random.randint(90, 115)
            elif composer.message_mood['mood'] == 'negative':
                velocity = random.randint(65, 90)
            else:
                velocity = random.randint(75, 100)
                
            midi.addNote(melody_track, 0, pitch, time, note_duration, velocity)
            melody_notes.append(pitch)
            time += note_duration + duration_unit * 0.5
            position += 1
            
        elif symbol == ' ':
            time += duration_unit * (2.5 + composer.message_complexity['length'] * 0.1)
            
        elif symbol == '/':
            time += duration_unit * (6 + composer.message_complexity['word_count'] * 0.2)
    
    # Add harmony with style-specific voicings
    if add_harmony:
        harmony_time = 0
        chord_index = 0
        while harmony_time < time:
            chord_root = key_root + progression[chord_index % len(progression)]
            
            # Determine chord type based on context
            if scale_type == 'minor':
                chord_type = 'minor' if chord_index % 4 in [0, 2] else 'major'
            else:
                chord_type = 'major' if chord_index % 4 in [0, 3] else 'minor'
                
            chord_notes = get_chord_notes(chord_root, chord_type, style)
            
            # Add some rhythmic variation to harmony
            chord_duration_varied = chord_duration
            if style == 'jazz':
                chord_duration_varied *= random.uniform(0.8, 1.2)
            
            for note in chord_notes:
                midi.addNote(harmony_track, 1, note, harmony_time, chord_duration_varied, harmony_volume)
            
            harmony_time += chord_duration
            chord_index += 1
    
    # Add bass with style-specific patterns
    if add_bass:
        bass_time = 0
        chord_index = 0
        bass_pattern_duration = chord_duration / 4
        
        while bass_time < time:
            chord_root = key_root + progression[chord_index % len(progression)] - 12
            
            if style == 'jazz':
                # Walking bass
                bass_notes = [chord_root, chord_root + 3, chord_root + 5, chord_root + 7]
            elif style == 'folk':
                # Alternating root-fifth
                bass_notes = [chord_root, chord_root + 7, chord_root, chord_root + 7]
            elif style == 'ambient':
                # Sustained root
                bass_notes = [chord_root]
                bass_pattern_duration = chord_duration
            else:  # ballad
                # Root, third, fifth pattern
                bass_notes = [chord_root, chord_root + 4, chord_root + 7, chord_root + 4]
            
            for bass_note in bass_notes:
                if bass_time < time:
                    # Add slight timing humanization
                    timing_offset = random.uniform(-0.02, 0.02) if style != 'ambient' else 0
                    midi.addNote(bass_track, 2, bass_note, bass_time + timing_offset, bass_pattern_duration, bass_volume)
                    bass_time += bass_pattern_duration
            
            chord_index += 1
    
    # Add drums with style-specific patterns
    if add_drums:
        drum_time = 0
        beat_duration = duration_unit
        
        while drum_time < time:
            beat_in_measure = int(drum_time / beat_duration) % 4
            
            if style == 'jazz':
                # Jazz brush pattern
                if beat_in_measure in [0, 2]:
                    midi.addNote(drum_track, 9, 42, drum_time, beat_duration * 0.3, drum_volume // 3)  # Hi-hat
                if beat_in_measure == 0:
                    midi.addNote(drum_track, 9, 36, drum_time, beat_duration, drum_volume // 2)  # Kick
                elif beat_in_measure == 2:
                    midi.addNote(drum_track, 9, 38, drum_time, beat_duration, drum_volume // 2)  # Snare
                    
            elif style == 'folk':
                # Simple, natural drum pattern
                if beat_in_measure == 0:
                    midi.addNote(drum_track, 9, 36, drum_time, beat_duration, drum_volume // 2)
                elif beat_in_measure == 2:
                    midi.addNote(drum_track, 9, 38, drum_time, beat_duration, drum_volume // 3)
                    
            # Skip drums for ballad and ambient to keep them cleaner
            
            drum_time += beat_duration
    
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
    
    # Pass the original message to the composition engine
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

# Enhanced instrument presets
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
