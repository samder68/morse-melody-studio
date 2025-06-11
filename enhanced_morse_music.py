'blues': [0, 3, 5, 6, 7, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10]
}

# Enhanced chord progressions
CHORD_PROGRESSIONS = {
    'classic': [0, 5, 3, 4],     # I-vi-IV-V
    'pop': [0, 3, 5, 4],         # I-IV-vi-V
    'folk': [0, 4, 0, 4],        # I-V-I-V
    'minor': [0, 6, 3, 4],       # i-VII-IV-V
    'jazz': [0, 5, 1, 4],        # I-vi-ii-V
    'blues': [0, 0, 4, 0, 5, 4, 0, 5]  # 12-bar blues pattern
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
    """Generate notes for a given scale"""
    scale_intervals = SCALES[scale_type]
    return [root_pitch + interval for interval in scale_intervals]

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

class MelodicAI:
    """Enhanced AI that creates real melodies following musical conventions"""
    
    def __init__(self, key_root, scale_type, style='ballad'):
        self.key_root = key_root
        self.scale_type = scale_type
        self.style = style
        self.scale_notes = get_scale_notes(key_root, scale_type)
        self.extended_scale = self.create_extended_scale()
        
        # Musical memory for context
        self.melody_history = deque(maxlen=8)
        self.phrase_direction = 0  # -1 descending, 0 neutral, 1 ascending
        self.phrase_climax_reached = False
        self.current_phrase_length = 0
        
        # Melodic patterns and tendencies
        self.melodic_patterns = self.create_melodic_patterns()
        self.interval_weights = self.create_interval_weights()
        
    def create_extended_scale(self):
        """Create an extended scale covering multiple octaves for better melodic range"""
        extended = []
        # Add notes from one octave below to one octave above
        for octave_offset in [-12, 0, 12]:
            for note in self.scale_notes:
                extended.append(note + octave_offset)
        return sorted(extended)
    
    def create_melodic_patterns(self):
        """Define melodic patterns based on musical style"""
        patterns = {
            'ballad': {
                'phrase_arch': 'rise_fall',  # Start low, rise to climax, fall
                'step_preference': 0.7,     # 70% stepwise motion
                'leap_max': 5,              # Max interval of 5 semitones
                'climax_position': 0.7,     # Climax 70% through phrase
                'tendency_tones': True      # Use leading tones and resolution
            },
            'folk': {
                'phrase_arch': 'wave',      # Gentle up and down motion
                'step_preference': 0.8,     # 80% stepwise motion
                'leap_max': 4,              # Smaller intervals
                'climax_position': 0.6,
                'tendency_tones': True
            },
            'jazz': {
                'phrase_arch': 'complex',   # More varied contour
                'step_preference': 0.5,     # More leaps allowed
                'leap_max': 7,              # Larger intervals allowed
                'climax_position': 0.6,
                'tendency_tones': True
            },
            'ambient': {
                'phrase_arch': 'floating', # Minimal direction
                'step_preference': 0.9,    # Very smooth
                'leap_max': 3,             # Very small intervals
                'climax_position': 0.5,
                'tendency_tones': False    # Less resolution needed
            }
        }
        return patterns.get(self.style, patterns['ballad'])
    
    def create_interval_weights(self):
        """Create weighted probabilities for different intervals"""
        if self.style == 'ballad':
            # Prefer steps, some small leaps
            return {
                0: 0.05,   # Unison (rare)
                1: 0.25,   # Half step
                2: 0.25,   # Whole step  
                3: 0.15,   # Minor third
                4: 0.10,   # Major third
                5: 0.08,   # Fourth
                7: 0.07,   # Fifth
                8: 0.03,   # Minor sixth
                9: 0.02    # Major sixth
            }
        elif self.style == 'folk':
            # Very stepwise, traditional
            return {
                0: 0.03,
                1: 0.15,
                2: 0.35,   # Lots of whole steps
                3: 0.20,
                4: 0.15,
                5: 0.07,
                7: 0.05
            }
        elif self.style == 'jazz':
            # More adventurous intervals
            return {
                0: 0.02,
                1: 0.15,
                2: 0.20,
                3: 0.15,
                4: 0.15,
                5: 0.10,
                7: 0.10,
                8: 0.05,
                9: 0.05,
                11: 0.03   # Major seventh
            }
        else:  # ambient
            # Very smooth, minimal movement
            return {
                0: 0.10,   # Some repeated notes
                1: 0.40,   # Lots of half steps
                2: 0.30,
                3: 0.15,
                4: 0.05
            }
    
    def get_phrase_target(self, phrase_length):
        """Determine where the phrase should go based on musical structure"""
        pattern = self.melodic_patterns
        climax_pos = pattern['climax_position']
        arch_type = pattern['phrase_arch']
        
        if arch_type == 'rise_fall':
            if phrase_length < climax_pos:
                return 'rise'
            else:
                return 'fall'
        elif arch_type == 'wave':
            # Gentle wave motion
            wave_pos = (phrase_length * 2 * math.pi) % (2 * math.pi)
            if math.sin(wave_pos) > 0:
                return 'rise'
            else:
                return 'fall'
        elif arch_type == 'floating':
            return 'neutral'
        else:  # complex
            # More unpredictable motion
            if random.random() < 0.4:
                return 'rise'
            elif random.random() < 0.8:
                return 'fall'
            else:
                return 'neutral'
    
    def choose_melodic_interval(self, current_note, target_direction):
        """Choose the next interval based on musical logic"""
        intervals = list(self.interval_weights.keys())
        weights = list(self.interval_weights.values())
        
        # Adjust weights based on target direction
        if target_direction == 'rise':
            # Boost upward intervals
            for i, interval in enumerate(intervals):
                if interval > 0:
                    weights[i] *= 1.5
        elif target_direction == 'fall':
            # Boost downward intervals by making them negative
            for i, interval in enumerate(intervals):
                if interval > 0:
                    intervals[i] = -interval
        
        # Choose interval
        chosen_interval = random.choices(intervals, weights=weights)[0]
        
        # Apply direction
        if target_direction == 'fall' and chosen_interval > 0:
            chosen_interval = -chosen_interval
        elif target_direction == 'rise' and chosen_interval < 0:
            chosen_interval = -chosen_interval
        
        return chosen_interval
    
    def apply_tendency_tones(self, note, next_note):
        """Apply music theory tendency tones for better resolution"""
        if not self.melodic_patterns['tendency_tones']:
            return next_note
        
        # Leading tone resolution (7th degree resolves up to tonic)
        note_degree = (note - self.key_root) % 12
        next_degree = (next_note - self.key_root) % 12
        
        # If we're on the leading tone (7th degree), prefer resolution to tonic
        if note_degree == 11 and random.random() < 0.6:  # 60% chance
            return self.key_root + (next_note // 12) * 12  # Resolve to tonic in same octave
        
        # If we're on the 4th degree, prefer resolution down to 3rd
        if note_degree == 5 and random.random() < 0.4:  # 40% chance
            target_degree = 4  # 3rd degree
            return self.key_root + target_degree + (next_note // 12) * 12
        
        return next_note
    
    def ensure_scale_membership(self, note):
        """Ensure the note belongs to our scale, with occasional chromatic passing tones"""
        # Find closest scale note
        closest_scale_note = min(self.extended_scale, key=lambda x: abs(x - note))
        
        # 90% of the time, use scale notes
        if random.random() < 0.9:
            return closest_scale_note
        else:
            # 10% of the time, allow chromatic passing tones
            return note
    
    def choose_melodic_note(self, symbol, position_in_phrase, **kwargs):
        """Enhanced melodic note selection following musical conventions"""
        self.current_phrase_length = position_in_phrase
        
        # Determine phrase target direction
        phrase_progress = position_in_phrase / 8.0  # Assume 8-note phrases
        target_direction = self.get_phrase_target(phrase_progress)
        
        if not self.melody_history:
            # Start with a good opening note (usually tonic or nearby)
            opening_notes = [self.key_root, self.key_root + 2, self.key_root + 4]
            if symbol == '.':
                note = random.choice(opening_notes[:2])  # Lower for dots
            else:
                note = random.choice(opening_notes[1:])  # Higher for dashes
        else:
            current_note = self.melody_history[-1]
            
            # Choose interval based on musical logic
            interval = self.choose_melodic_interval(current_note, target_direction)
            
            # Apply interval
            candidate_note = current_note + interval
            
            # Apply tendency tone resolution
            candidate_note = self.apply_tendency_tones(current_note, candidate_note)
            
            # Ensure it's in our scale (mostly)
            note = self.ensure_scale_membership(candidate_note)
            
            # Keep in reasonable range
            note = max(self.key_root - 12, min(note, self.key_root + 19))
        
        # Adjust for dot vs dash character
        if symbol == '.' and len(self.melody_history) > 0:
            # Dots tend to be lower/shorter
            if random.random() < 0.3:  # 30% chance to go lower
                note = max(note - 2, self.key_root - 12)
        elif symbol == '-' and len(self.melody_history) > 0:
            # Dashes tend to be higher/longer
            if random.random() < 0.3:  # 30% chance to go higher
                note = min(note + 2, self.key_root + 19)
        
        self.melody_history.append(note)
        return note
    
    def create_phrase_ending(self, phrase_length):
        """Create a satisfying phrase ending"""
        if len(self.melody_history) < 2:
            return self.key_root
        
        current_note = self.melody_history[-1]
        
        # Strong tendency to end phrases on stable tones (1, 3, 5 of scale)
        stable_endings = [
            self.key_root,      # Tonic
            self.key_root + 4,  # Third  
            self.key_root + 7   # Fifth
        ]
        
        # Choose closest stable ending
        target_ending = min(stable_endings, key=lambda x: abs(x - current_note))
        
        # Move toward it step-wise if possible
        if abs(current_note - target_ending) <= 2:
            return target_ending
        else:
            # Move one step toward the target
            direction = 1 if target_ending > current_note else -1
            return current_note + direction
    
    def generate_smart_harmony(self, melody_note, time, phrase_position, **kwargs):
        """Generate harmony that intelligently follows the melody"""
        ai_harmony = kwargs.get('ai_harmony', True)
        
        if not ai_harmony:
            return get_chord_notes(self.key_root, 'major' if self.scale_type == 'major' else 'minor')
        
        # Analyze melody note in context of scale
        melody_scale_degree = (melody_note - self.key_root) % 12
        
        # Smart chord selection based on scale degree
        if self.scale_type == 'major':
            chord_map = {
                0: ('major', 0),    # Tonic
                2: ('minor', 2),    # Supertonic
                4: ('minor', 4),    # Mediant
                5: ('major', 5),    # Subdominant
                7: ('major', 7),    # Dominant
                9: ('minor', 9),    # Submediant
                11: ('dim', 11)     # Leading tone
            }
        else:  # minor scale
            chord_map = {
                0: ('minor', 0),    # Tonic
                2: ('dim', 2),      # Supertonic
                3: ('major', 3),    # Mediant
                5: ('minor', 5),    # Subdominant
                7: ('minor', 7),    # Dominant
                8: ('major', 8),    # Submediant
                10: ('major', 10)   # Subtonic
            }
        
        # Find best fitting chord
        best_chord = None
        for scale_degree, (chord_type, root_offset) in chord_map.items():
            if melody_scale_degree in [scale_degree, (scale_degree + 2) % 12, (scale_degree + 4) % 12]:
                chord_root = self.key_root + root_offset
                best_chord = get_chord_notes(chord_root, chord_type)
                break
        
        if not best_chord:
            best_chord = get_chord_notes(self.key_root, 'major' if self.scale_type == 'major' else 'minor')
        
        # Add jazz extensions for jazz style
        if self.style == 'jazz' and random.random() < 0.4:
            extension = random.choice([9, 11, 13])
            if len(best_chord) < 4:
                best_chord.append(best_chord[0] + extension)
        
        return best_chord
    
    def generate_walking_bass(self, current_chord, next_chord, duration, **kwargs):
        """Generate intelligent walking bass lines"""
        walking_bass = kwargs.get('walking_bass', True)
        
        if not walking_bass:
            bass_root = min(current_chord) - 12
            return [(bass_root, duration)]
        
        bass_notes = []
        current_root = min(current_chord) - 12
        
        if next_chord:
            next_root = min(next_chord) - 12
            steps = 4
            step_duration = duration / steps
            
            for i in range(steps):
                if i == 0:
                    bass_notes.append((current_root, step_duration))
                elif i == steps - 1:
                    approach_note = next_root - 1 if next_root > current_root else next_root + 1
                    bass_notes.append((approach_note, step_duration))
                else:
                    if i == 1:
                        bass_notes.append((current_root + 7, step_duration))
                    else:
                        if abs(next_root - current_root) > 2:
                            direction = 1 if next_root > current_root else -1
                            approach = current_root + direction * (i - 1)
                        else:
                            chord_tone = random.choice([current_root + 3, current_root + 5])
                        bass_notes.append((approach if abs(next_root - current_root) > 2 else chord_tone, step_duration))
        else:
            pattern = [current_root, current_root + 7, current_root + 5, current_root + 7]
            step_duration = duration / len(pattern)
            for note in pattern:
                bass_notes.append((note, step_duration))
        
        return bass_notes
    
    def apply_humanization(self, time, duration, velocity, **kwargs):
        """Apply human-like timing and dynamics variations"""
        humanize = kwargs.get('humanize', True)
        
        if not humanize:
            return time, duration, velocity
        
        timing_variance = random.uniform(-0.02, 0.02)
        humanized_time = max(0, time + timing_variance)
        
        duration_variance = random.uniform(0.95, 1.05)
        humanized_duration = duration * duration_variance
        
        velocity_variance = random.randint(-10, 10)
        humanized_velocity = max(1, min(127, velocity + velocity_variance))
        
        return humanized_time, humanized_duration, humanized_velocity

def morse_to_enhanced_midi(morse_code, output_file, **kwargs):
    """
    Enhanced MIDI generator with multiple musical features (original version)
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
    
    # Get scale notes for melody
    scale_notes = get_scale_notes(key_root, scale_type)
    
    # Get chord progression
    progression = CHORD_PROGRESSIONS[chord_progression]
    chord_duration = duration_unit * 8  # Each chord lasts 8 beats
    current_chord_index = 0
    chord_change_time = chord_duration
    
    # Generate melody (encoded message)
    volume = 100
    harmony_volume = 70
    bass_volume = 80
    drum_volume = 90
    
    for symbol in morse_code:
        if symbol == '.':
            # Dot: use scale notes with some variation
            pitch = random.choice(scale_notes[:5])  # Use lower part of scale for dots
            midi.addNote(melody_track, 0, pitch, time, duration_unit, volume)
            time += duration_unit + duration_unit  # dot + intra-symbol gap
            
        elif symbol == '-':
            # Dash: use higher scale notes
            pitch = random.choice(scale_notes[3:])  # Use higher part of scale for dashes
            midi.addNote(melody_track, 0, pitch, time, duration_unit * 3, volume)
            time += duration_unit * 3 + duration_unit  # dash + intra-symbol gap
            
        elif symbol == ' ':
            time += duration_unit * 3  # gap between letters
            
        elif symbol == '/':
            time += duration_unit * 7  # gap between words
    
    # Add harmony track
    if add_harmony:
        harmony_time = 0
        chord_index = 0
        
        while harmony_time < time:
            # Get current chord root
            chord_root = key_root + progression[chord_index % len(progression)]
            chord_notes = get_chord_notes(chord_root, 'major')
            
            # Add chord notes
            for note in chord_notes:
                midi.addNote(harmony_track, 1, note, harmony_time, chord_duration, harmony_volume)
            
            harmony_time += chord_duration
            chord_index += 1
    
    # Add bass line
    if add_bass:
        bass_time = 0
        chord_index = 0
        bass_pattern_duration = chord_duration / 4  # Quarter notes
        
        while bass_time < time:
            chord_root = key_root + progression[chord_index % len(progression)] - 12  # One octave lower
            
            # Simple bass pattern: root, fifth, root, fifth
            bass_notes = [chord_root, chord_root + 7, chord_root, chord_root + 7]
            
            for bass_note in bass_notes:
                if bass_time < time:
                    midi.addNote(bass_track, 2, bass_note, bass_time, bass_pattern_duration, bass_volume)
                    bass_time += bass_pattern_duration
            
            chord_index += 1
    
    # Add simple drum pattern
    if add_drums:
        drum_time = 0
        beat_duration = duration_unit
        kick_drum = 36  # C2
        snare_drum = 38  # D2
        hi_hat = 42     # F#2
        
        while drum_time < time:
            # Simple 4/4 pattern
            beat_in_measure = int(drum_time / beat_duration) % 4
            
            if beat_in_measure == 0:  # Beat 1 - kick
                midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
            elif beat_in_measure == 2:  # Beat 3 - snare
                midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
            
            # Hi-hat on every beat
            midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.5, drum_volume // 2)
            
            drum_time += beat_duration
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi.writeFile(f)

def morse_to_ai_enhanced_midi(morse_code, output_file, **kwargs):
    """
    AI-Enhanced MIDI generator with melodically intelligent features
    """
    # Extract parameters with defaults
    tempo = kwargs.get('tempo', 120)
    key_root = kwargs.get('key_root', 60)
    scale_type = kwargs.get('scale_type', 'major')
    style = kwargs.get('style', 'ballad')
    add_harmony = kwargs.get('add_harmony', True)
    add_bass = kwargs.get('add_bass', True)
    add_drums = kwargs.get('add_drums', False)
    chord_progression = kwargs.get('chord_progression', 'classic')
    melody_instrument = kwargs.get('melody_instrument', 0)
    harmony_instrument = kwargs.get('harmony_instrument', 48)
    bass_instrument = kwargs.get('bass_instrument', 32)
    
    duration_unit = 0.25
    time = 0
    
    # Initialize enhanced melodic AI
    ai = MelodicAI(key_root, scale_type, style)
    
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
        midi.addProgramChange(drum_track, 9, 0, 0)
    
    # Generate melodically enhanced melody
    volume = 100
    harmony_volume = 70
    bass_volume = 80
    drum_volume = 90
    
    melody_notes = []
    phrase_position = 0
    
    # Process morse code with musical phrasing
    symbols = list(morse_code)
    for i, symbol in enumerate(symbols):
        if symbol == '.':
            pitch = ai.choose_melodic_note('.', phrase_position, **kwargs)
            note_duration = duration_unit
            rest_duration = duration_unit * 0.5
            
            final_time, final_duration, final_velocity = ai.apply_humanization(
                time, note_duration, volume, **kwargs)
            
            midi.addNote(melody_track, 0, pitch, final_time, final_duration, final_velocity)
            melody_notes.append((pitch, time, note_duration))
            time += note_duration + rest_duration
            phrase_position += 1
            
        elif symbol == '-':
            pitch = ai.choose_melodic_note('-', phrase_position, **kwargs)
            note_duration = duration_unit * 3
            rest_duration = duration_unit * 0.5
            
            final_time, final_duration, final_velocity = ai.apply_humanization(
                time, note_duration, volume, **kwargs)
            
            midi.addNote(melody_track, 0, pitch, final_time, final_duration, final_velocity)
            melody_notes.append((pitch, time, note_duration))
            time += note_duration + rest_duration
            phrase_position += 1
            
        elif symbol == ' ':
            # End of letter - create phrase ending if we have enough notes
            if phrase_position >= 3:
                ending_note = ai.create_phrase_ending(phrase_position)
                ending_time, ending_duration, ending_velocity = ai.apply_humanization(
                    time, duration_unit * 0.5, volume - 20, **kwargs)
                midi.addNote(melody_track, 0, ending_note, ending_time, ending_duration, ending_velocity)
                melody_notes.append((ending_note, time, duration_unit * 0.5))
                time += duration_unit * 0.5
            
            time += duration_unit * 2.5
            phrase_position = 0
            
        elif symbol == '/':
            # End of word - stronger phrase ending
            if phrase_position >= 2:
                ending_note = ai.create_phrase_ending(phrase_position)
                ending_time, ending_duration, ending_velocity = ai.apply_humanization(
                    time, duration_unit, volume - 10, **kwargs)
                midi.addNote(melody_track, 0, ending_note, ending_time, ending_duration, ending_velocity)
                melody_notes.append((ending_note, time, duration_unit))
                time += duration_unit
            
            time += duration_unit * 6
            phrase_position = 0
    
    # Add AI-enhanced harmony track
    if add_harmony:
        harmony_time = 0
        chord_duration = duration_unit * 8
        chord_index = 0
        
        while harmony_time < time:
            melody_in_period = [
                note for note, note_time, dur in melody_notes 
                if harmony_time <= note_time < harmony_time + chord_duration
            ]
            
            if melody_in_period:
                main_melody_note = melody_in_period[len(melody_in_period)//2]
                chord_notes = ai.generate_smart_harmony(
                    main_melody_note, harmony_time, chord_index, **kwargs)
            else:
                progression = CHORD_PROGRESSIONS[chord_progression]
                chord_root = key_root + progression[chord_index % len(progression)]
                chord_notes = get_chord_notes(chord_root, 'major')
            
            for i, note in enumerate(chord_notes):
                final_time, final_duration, final_velocity = ai.apply_humanization(
                    harmony_time + i * 0.01, chord_duration, harmony_volume, **kwargs)
                midi.addNote(harmony_track, 1, note, final_time, final_duration, final_velocity)
            
            harmony_time += chord_duration
            chord_index += 1
    
    # Add bass and drums
    if add_bass:
        bass_time = 0
        chord_duration = duration_unit * 8
        chord_index = 0
        progression = CHORD_PROGRESSIONS[chord_progression]
        
        while bass_time < time:
            current_chord_root = key_root + progression[chord_index % len(progression)]
            next_chord_root = key_root + progression[(chord_index + 1) % len(progression)]
            
            current_chord = get_chord_notes(current_chord_root, 'major')
            next_chord = get_chord_notes(next_chord_root, 'major')
            
            bass_notes = ai.generate_walking_bass(
                current_chord, next_chord, chord_duration, **kwargs)
            
            for bass_note, note_duration in bass_notes:
                if bass_time < time:
                    final_time, final_duration, final_velocity = ai.apply_humanization(
                        bass_time, note_duration, bass_volume, **kwargs)
                    midi.addNote(bass_track, 2, bass_note, final_time, final_duration, final_velocity)
                    bass_time += note_duration
            
            chord_index += 1
    
    if add_drums:
        drum_time = 0
        beat_duration = duration_unit
        kick_drum = 36
        snare_drum = 38
        hi_hat = 42
        open_hat = 46
        
        while drum_time < time:
            beat_in_measure = int(drum_time / beat_duration) % 4
            
            # Enhanced drum patterns based on style
            if style == 'jazz':
                # Jazz swing pattern
                if beat_in_measure == 0:  # Beat 1
                    midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
                    midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.3, drum_volume // 3)
                elif beat_in_measure == 2:  # Beat 3
                    midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
                
                # Swing hi-hat
                if beat_in_measure % 2 == 0:
                    midi.addNote(drum_track, 9, hi_hat, drum_time + beat_duration * 0.67, 
                               beat_duration * 0.33, drum_volume // 4)
            else:
                # Standard rock/pop pattern
                if beat_in_measure == 0:  # Beat 1 - kick
                    midi.addNote(drum_track, 9, kick_drum, drum_time, beat_duration, drum_volume)
                elif beat_in_measure == 2:  # Beat 3 - snare
                    midi.addNote(drum_track, 9, snare_drum, drum_time, beat_duration, drum_volume)
                
                # Hi-hat on every beat
                hat_volume = drum_volume // 3
                if beat_in_measure == 1 or beat_in_measure == 3:
                    # Occasionally open hi-hat on off-beats
                    hat_drum = open_hat if random.random() < 0.1 else hi_hat
                    midi.addNote(drum_track, 9, hat_drum, drum_time, beat_duration * 0.5, hat_volume)
                else:
                    midi.addNote(drum_track, 9, hi_hat, drum_time, beat_duration * 0.5, hat_volume)
            
            drum_time += beat_duration
    
    # Write MIDI file
    with open(output_file, 'wb') as f:
        midi.writeFile(f)

def midi_to_wav(midi_path, wav_path, soundfont_path=None):
    """Convert MIDI to WAV using FluidSynth with cloud deployment error handling"""
    if soundfont_path is None:
        print("WAV generation skipped - no soundfont provided")
        return False
        
    try:
        # Check if soundfont exists
        if not os.path.exists(soundfont_path):
            print(f"Soundfont not found at {soundfont_path}")
            return False
            
        # Run FluidSynth to convert MIDI to WAV
        result = subprocess.run([
            "fluidsynth",
            "-ni",
            soundfont_path,
            midi_path,
            "-F",
            wav_path,
            "-r", "44100"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Successfully generated WAV file: {wav_path}")
            return True
        else:
            print(f"FluidSynth error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FluidSynth timed out - try a shorter message")
        return False
    except FileNotFoundError:
        print("WAV generation skipped - fluidsynth not found")
        return False
    except Exception as e:
        print(f"Error generating WAV: {e}")
        return False

def generate_enhanced_files_from_text(text, **musical_options):
    """
    Generate AI-enhanced musical files from text with cloud deployment support
    
    All original musical options plus new AI features:
    - ai_harmony: Intelligent chord progressions that follow melody
    - walking_bass: Smart bass lines with musical movement
    - humanize: Natural timing and dynamic variations
    - smart_dynamics: Expressive musical phrasing
    - style: Musical style affecting all AI decisions
    """
    morse = text_to_morse(text)
    tmpdir = tempfile.gettempdir()
    
    # Create unique filenames based on message
    safe_text = "".join(c for c in text if c.isalnum())[:10]
    midi_path = os.path.join(tmpdir, f"ai_morse_{safe_text}.mid")
    wav_path = os.path.join(tmpdir, f"ai_morse_{safe_text}.wav")
    
    # Check if AI features are requested
    use_ai = any([
        musical_options.get('ai_harmony', False),
        musical_options.get('walking_bass', False),
        musical_options.get('humanize', False),
        musical_options.get('smart_dynamics', False)
    ])
    
    try:
        if use_ai:
            # Use the new AI-enhanced function
            morse_to_ai_enhanced_midi(morse, midi_path, **musical_options)
        else:
            # Use the original function for compatibility
            morse_to_enhanced_midi(morse, midi_path, **musical_options)
        
        # Verify MIDI file was created
        if not os.path.exists(midi_path):
            raise Exception("MIDI file generation failed")
        
        # Try to convert to WAV (may fail on cloud platforms)
        wav_success = False
        try:
            # Try multiple soundfont locations
            soundfont_paths = [
                os.path.expanduser("~/soundfonts/FluidR3_GM.sf2"),
                "/usr/share/soundfonts/FluidR3_GM.sf2",
                "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls"
            ]
            
            for soundfont_path in soundfont_paths:
                if os.path.exists(soundfont_path):
                    wav_success = midi_to_wav(midi_path, wav_path, soundfont_path)
                    if wav_success:
                        break
            
            if not wav_success:
                print("WAV generation not available on this platform - MIDI file ready for download")
                wav_path = None
        
        except Exception as wav_error:
            print(f"WAV generation failed: {wav_error}")
            wav_path = None
    
        return midi_path, wav_path, morse
        
    except Exception as e:
        print(f"Error in file generation: {e}")
        raise e

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
}# This is the same complete file as before, but with fixed WAV generation
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

# Enhanced musical scales
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues':
