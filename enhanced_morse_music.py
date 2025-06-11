# enhanced_morse_music_randomized.py — FINAL & FUNCTIONAL
# ✅ Fully randomized yet melodic Morse-to-MIDI generator
# ✅ Motifs stay in scale, with each phrase a musical variation
# ✅ Output: melodic .mid file that feels alive, not robotic

from midiutil import MIDIFile
import random

# Motif Generator
class MotifGenerator:
    def __init__(self, scale_notes, motif_size=4):
        self.scale_notes = scale_notes
        self.motif_size = motif_size
        self.motif = []
        self.symbol_count = 0

    def generate_new_motif(self):
        base = random.choice(self.scale_notes)
        self.motif = [self._snap_to_scale(base + random.choice([-4, -2, 0, 2, 4])) for _ in range(self.motif_size)]
        self.symbol_count = 0

    def _snap_to_scale(self, note):
        candidates = self.scale_notes + [n + 12 for n in self.scale_notes] + [n - 12 for n in self.scale_notes]
        return min(candidates, key=lambda x: abs(x - note))

    def get_note(self):
        if self.symbol_count % self.motif_size == 0:
            self.generate_new_motif()
        note = self.motif[self.symbol_count % self.motif_size]
        self.symbol_count += 1
        return note

# Morse Code and Music Parameters
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}
SCALES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10]}
KEYS = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}

# Main Functions
def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def get_scale_notes(key_root, scale_type):
    return [key_root + interval for interval in SCALES[scale_type]]

def generate_random_music(text, output_file, tempo=90, key='C', scale_type='major'):
    morse = text_to_morse(text)
    root = KEYS[key]
    scale = get_scale_notes(root, scale_type)
    motif_gen = MotifGenerator(scale)

    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, 0)  # Piano

    dot = 0.5 * 60 / tempo
    dash = 1.5 * 60 / tempo
    time = 0

    for char in morse:
        if char == '.':
            pitch = motif_gen.get_note()
            midi.addNote(0, 0, pitch, time, dot, 100)
            time += dot + 0.1
        elif char == '-':
            pitch = motif_gen.get_note()
            midi.addNote(0, 0, pitch, time, dash, 100)
            time += dash + 0.1
        elif char == ' ':
            time += dot * 2
        elif char == '/':
            time += dot * 4

    with open(output_file, 'wb') as f:
        midi.writeFile(f)

if __name__ == '__main__':
    generate_random_music("Hope is the frequency", "morse_final_output.mid")
    print("✅ MIDI file generated: morse_final_output.mid")
