# enhanced_morse_music_randomized.py
# Fully updated version using MotifGenerator instead of fixed melodic mapping

from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess
import math

# New MotifGenerator
class MotifGenerator:
    def __init__(self, scale_notes, variation_seed=None):
        self.scale_notes = scale_notes
        self.memory = []
        self.motif_size = 4
        self.current_motif = []
        self.variation_seed = variation_seed or random.randint(0, 99999)
        random.seed(self.variation_seed)

    def generate_base_motif(self):
        base_note = random.choice(self.scale_notes)
        motif = [base_note]
        for _ in range(self.motif_size - 1):
            interval = random.choice([-2, -1, 1, 2, 3, 4])
            next_note = motif[-1] + interval
            next_note = self._clamp_to_scale(next_note)
            motif.append(next_note)
        return motif

    def vary_motif(self, motif):
        return [self._clamp_to_scale(n + random.choice([-2, 0, 2])) for n in motif]

    def _clamp_to_scale(self, note):
        closest = min(self.scale_notes + [n + 12 for n in self.scale_notes] + [n - 12 for n in self.scale_notes],
                      key=lambda x: abs(x - note))
        return closest

    def get_next_phrase(self):
        if not self.memory or random.random() < 0.4:
            new_motif = self.generate_base_motif()
            self.memory.append(new_motif)
            self.current_motif = new_motif
        else:
            self.current_motif = self.vary_motif(random.choice(self.memory))
        return self.current_motif

    def get_note_from_morse(self, index):
        if not self.current_motif:
            self.get_next_phrase()
        return self.current_motif[index % len(self.current_motif)]


# Morse dictionary
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

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10]
}

INSTRUMENTS = {
    'Piano': 0,
    'Strings': 48,
    'Bass': 32
}

KEY_PRESETS = {
    'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root_pitch, scale_type):
    intervals = SCALES[scale_type]
    return [root_pitch + i for i in intervals]

def generate_random_music(text, output_file, tempo=100, key='C', scale_type='major'):
    morse = text_to_morse(text)
    root_pitch = KEY_PRESETS[key]
    scale_notes = get_scale_notes(root_pitch, scale_type)

    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, INSTRUMENTS['Piano'])

    time = 0
    dot = 0.5 * 60.0 / tempo
    dash = 1.5 * 60.0 / tempo

    motif_engine = MotifGenerator(scale_notes)
    motif = motif_engine.get_next_phrase()

    symbol_index = 0
    for symbol in morse:
        if symbol in ['.', '-']:
            pitch = motif_engine.get_note_from_morse(symbol_index)
            duration = dot if symbol == '.' else dash
            midi.addNote(0, 0, pitch, time, duration, 80)
            time += duration + 0.1
            symbol_index += 1
        elif symbol == ' ':
            time += 0.2
        elif symbol == '/':
            time += 0.5

    with open(output_file, 'wb') as f:
        midi.writeFile(f)

# Example usage:
if __name__ == '__main__':
    message = "Hope is the frequency"
    generate_random_music(message, "morse_fresh.mid", tempo=90, key='C', scale_type='major')
    print("✅ New randomized composition generated.")
