import threading

from psychopy import visual, core, sound
import speech_recognition as sr
import os

# --- Setup ---
recognizer = sr.Recognizer()
recognizer = sr.Recognizer()
# Adjust for short phonemes
recognizer.pause_threshold = 0.5      # Seconds of silence before a phrase is considered done
recognizer.non_speaking_duration = 0.3 # How much 'silence' to keep on either side of the vowel
recognizer.phrase_threshold = 0.2      # Minimum sound duration to be considered speech

# In your detection logic:
PHONEME_MAP = {
    'a': ['a', 'ah', 'uh', 'ay', 'hey', 'eight', 'apple'],
    'e': ['e', 'ee', 'he', 'she', 'eat', 'it'],
    'i': ['i', 'eye', 'hi', 'high', 'my', 'ai'],
    'o': ['o', 'oh', 'who', 'owe', 'low'],
    'u': ['u', 'you', 'oo', 'new', 'view']
}
# Update the match check:

mic = sr.Microphone()
score = 0
mistakes = 0

win = visual.Window(size=(1024, 768), color=[-0.5, -0.5, -0.5], units='height', fullscr=False)

# Stimuli
welcome_stim = visual.TextStim(win, text="Welcome to the Experiment", pos=(0, 0), height=0.07, color='white')
count_stim   = visual.TextStim(win, text='', pos=(0, 0), height=0.2, color='white', bold=True)
header_stim  = visual.TextStim(win, text='', pos=(0, 0.2), height=0.05, color='cyan')
class_stim   = visual.TextStim(win, text='', pos=(0, 0), height=0.15, color='white', bold=True)

fig_path = "figures"
mic_file   = os.path.join(fig_path, "microphone.png")
brain_file = os.path.join(fig_path, "brain.png")

mic_icon   = visual.ImageStim(win, image=mic_file, pos=(.1, 0.2), size=(0.05, 0.05))
brain_icon = visual.ImageStim(win, image=brain_file, pos=(0, -0.2), size=(0.1, 0.1))

beep = sound.Sound('A', octave=6, secs=0.2)
words = ['a', 'incorporate']
n_trials = 2
trial_clock = core.Clock()

def background_recognition(audio_data, target, trial_num, current_word):
    global score, mistakes

    try:
        # This part happens "behind the scenes" while the participant rests
        detected_text = recognizer.recognize_google(audio_data).lower()

        variants = PHONEME_MAP.get(target, [target])
        if any(v in detected_text for v in variants):
            score += 1
            print(f"✅ Trial {trial_num} Result: Match! Heard '{detected_text}'")
        else:
            mistakes += 1
            print(f"❌ Trial {trial_num} Result: Mistake. Heard '{detected_text}'")

    except Exception:
        mistakes += 1
        print(f"☁️ Trial {trial_num} Result: No recognizable speech.")

    filename = f"trial_{trial+1}_{current_word}.wav"
    with open(filename, "wb") as f:
        f.write(audio.get_wav_data())

def run_flicker_phase(target_time, header, h_color, class_txt, class_h, mode):
    while trial_clock.getTime() < target_time:
        show_icon = (int(trial_clock.getTime() * 1.2) % 2) == 0
        header_stim.text = header
        header_stim.color = h_color
        class_stim.text = class_txt
        class_stim.height = class_h
        class_stim.draw()
        if show_icon:
            header_stim.draw()
            if mode == 'overtly':
                mic_icon.draw()
        win.flip()

# --- 1. Welcome & Calibration ---
welcome_stim.draw()
brain_icon.draw()
win.flip()

with mic as source:
    recognizer.adjust_for_ambient_noise(source, duration=2)

while trial_clock.getTime() < 3.0:
    win.flip()

# --- 2. Countdown Window (3, 2, 1) ---
for i in ['3', '2', '1']:
    count_stim.text = i
    count_stim.draw()
    win.flip()
    core.wait(1.0)

# --- 3. Main Experiment Loop ---
for trial in range(n_trials):
    current_word = words[trial % len(words)]
    trial_clock.reset()

    # --- Step 1: Innerly (5.0s) ---
    run_flicker_phase(5.0, 'innerly', 'cyan', current_word, 0.15, 'innerly')

    # --- Step 2: Imagery Beeps (Interval 1.7s) ---
    # Beep times: 5.0, 6.7, 8.4, 10.1, 11.8
    beep_times = [5.0, 6.7, 8.4, 10.1, 11.8]
    for t_val in beep_times:
        core.wait(max(0, t_val - trial_clock.getTime()))
        win.flip()
        beep.stop(); beep.play()

    # --- Step 3: Buffer (1.7s Blank after last beep) ---
    # 11.8 + 1.7 = 13.5s
    win.flip()
    core.wait(max(0, 13.5 - trial_clock.getTime()))

    # --- Step 4: Overt Instruction (5.0s duration) ---
    # 13.5 + 5.0 = 18.5s
    run_flicker_phase(17, 'overtly', 'orange', 'please say last imagined unit', 0.06, 'overtly')

    # --- Step 5: Overt Listening (6s Window - BLANK SCREEN) ---
    beep.stop(); beep.play()
    win.flip() # Ensure screen is blank during recording
    core.wait(0.2)

    with mic as source:
        # Trigger: START_EPOCH
        audio = recognizer.record(source, duration=5.0)
        # Trigger: END_EPOCH

    # 2. START BACKGROUND RECOGNITION (Non-blocking)
    # This fires off the request and immediately continues to the next line of code
    recog_thread = threading.Thread(
        target=background_recognition,
        args=(audio, current_word, trial+1, current_word)
    )
    recog_thread.start()

    # Cumulative update
    print(f"Current Stats -> Matches: {score} | Mistakes: {mistakes}\n")

    # Reset clock for Rest phases
    trial_clock.reset()

    # --- Step 6: Rest Instruction (3.0s) ---
    class_stim.text = 'rest'
    class_stim.height = 0.15
    class_stim.draw()
    win.flip()
    core.wait(2.5)

    # --- Step 7: Rest Blank (10.0s) ---
    beep.stop(); beep.play()
    win.flip()
    core.wait(10.0)

    beep.stop(); beep.play()

win.close()
core.quit()