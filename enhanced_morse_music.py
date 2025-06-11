# Fixed and Enhanced Version: `enhanced_morse_music_randomized.py`
# ✔ Uses MotifGenerator to introduce phrase variation
# ✔ Integrates properly into Morse structure
# ✔ Avoids shared motif between message runs

from midiutil import MIDIFile
import os
import random
import tempfile
import subprocess

# Motif Generator with variation and proper state control
class MotifGenerator:
    def __init__(self, scale_notes, seed=None):
        self.scale_notes = scale_notes
        self.memory = []
        self.motif_size = 4
        self.current_motif = []
        self.seed = seed or random.randint(1000, 9999)
        self.symbol_counter = 0
        random.seed(self.seed)

    def _clamp(self, note):
        options = self.scale_notes + [n + 12 for n in self.scale_notes] + [n - 12 for n in self.scale_notes]
        return min(options, key=lambda x: abs(x - note))

    def generate_motif(self):
        base = random.choice(self.scale_notes)
        return [self._clamp(base + random.choice([-2, -1, 0, 1, 2])) for _ in range(self.motif_size)]

    def next_motif(self):
        if not self.memory or random.random() < 0.4:
            motif = self.generate_motif()
            self.memory.append(motif)
        else:
            motif = random.choice(self.memory)
        self.current_motif = motif
        return motif

    def get_note(self):
        if not self.current_motif or self.symbol_counter % self.motif_size == 0:
            self.next_motif()
        note = self.current_motif[self.symbol_counter % self.motif_size]
        self.symbol_counter += 1
        return note

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}

SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10]
}

INSTRUMENTS = {
    'Piano': 0, 'Strings': 48, 'Bass': 32
}

KEY_PRESETS = {
    'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(root, scale):
    return [root + i for i in SCALES[scale]]

def generate_randomized_morse_music(message, output_file, tempo=100, key='C', scale='major'):
    morse = text_to_morse(message)
    root_pitch = KEY_PRESETS[key]
    scale_notes = get_scale_notes(root_pitch, scale)

    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, INSTRUMENTS['Piano'])

    motif_gen = MotifGenerator(scale_notes)
    time = 0
    dot = 0.5 * 60 / tempo
    dash = 1.5 * 60 / tempo

    for symbol in morse:
        if symbol in ['.', '-']:
            pitch = motif_gen.get_note()
            dur = dot if symbol == '.' else dash
            midi.addNote(0, 0, pitch, time, dur, 90)
            time += dur + 0.1
        elif symbol == ' ':
            time += dot * 2
        elif symbol == '/':
            time += dot * 4

    with open(output_file, 'wb') as f:
        midi.writeFile(f)

if __name__ == "__main__":
    generate_randomized_morse_music("Hope is the frequency", "morse_final.mid", tempo=90, key='C')
    print("✅ Your updated Morse melody with random motifs is ready!")
