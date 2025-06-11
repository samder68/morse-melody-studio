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

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(c.upper(), '') for c in text)

def morse_to_midi(morse_code, output_file, tempo=120, base_pitch=60):
    track = 0
    channel = 0
    volume = 100
    duration_unit = 0.25  # base duration for a dot
    time = 0

    midi = MIDIFile(1)
    midi.addTempo(track, time, tempo)
    midi.addProgramChange(track, channel, time, 0)  # Acoustic Grand Piano

    for symbol in morse_code:
        if symbol == '.':
            pitch = base_pitch + random.choice([-2, 0, 2])
            midi.addNote(track, channel, pitch, time, duration_unit, volume)
            time += duration_unit + duration_unit  # dot + intra-symbol gap
        elif symbol == '-':
            pitch = base_pitch + random.choice([-5, 0, 5])
            midi.addNote(track, channel, pitch, time, duration_unit * 3, volume)
            time += duration_unit * 3 + duration_unit  # dash + intra-symbol gap
        elif symbol == ' ':
            time += duration_unit * 3  # gap between letters
        elif symbol == '/':
            time += duration_unit * 7  # gap between words

    with open(output_file, 'wb') as f:
        midi.writeFile(f)

def midi_to_wav(midi_path, wav_path, soundfont_path=None):
    # Note: This function requires fluidsynth and a soundfont file
    # For portable use, we'll skip WAV generation if fluidsynth isn't available
    if soundfont_path is None:
        print("WAV generation skipped - requires fluidsynth installation")
        return
        
    try:
        subprocess.run([
            "fluidsynth",
            "-ni",
            soundfont_path,
            midi_path,
            "-F",
            wav_path,
            "-r", "44100"
        ])
    except FileNotFoundError:
        print("WAV generation skipped - fluidsynth not found")

def generate_files_from_text(text):
    morse = text_to_morse(text)
    tmpdir = tempfile.gettempdir()
    midi_path = os.path.join(tmpdir, "cody_musical_message.mid")
    wav_path = os.path.join(tmpdir, "cody_musical_message.wav")

    morse_to_midi(morse, midi_path)
    midi_to_wav(midi_path, wav_path)

    return midi_path, wav_path, morse
