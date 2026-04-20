from psychopy import visual, core, sound
import os

# --- Setup ---
win = visual.Window(size=(1024, 768), color=[-0.5, -0.5, -0.5], units='height', fullscr=False)

header_stim = visual.TextStim(win, text='', pos=(0, 0.2), height=0.05, color='cyan')
class_stim = visual.TextStim(win, text='', pos=(0, 0), height=0.15, color='white', bold=True)

fig_path = "figures"
mic_file = os.path.join(fig_path, "microphone.png")
mic_icon = visual.ImageStim(win, image=mic_file, pos=(.1, 0.2), size=(0.05, 0.05))

beep = sound.Sound('A', octave=5, secs=0.2)
words = ['pinch', 'stop']
n_trials = 2
trial_clock = core.Clock()

def run_flicker_phase(target_time, header, h_color, class_txt, class_h, mode):
    while trial_clock.getTime() < target_time:
        # Flicker logic (1.2 multiplier as per your previous edit)
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

# --- Main Experiment Loop ---
for trial in range(n_trials):
    current_word = words[trial % len(words)]
    trial_clock.reset()

    # --- 1. Instruction Innerly (0.0s - 5.0s) ---
    run_flicker_phase(5.0, 'innerly', 'cyan', current_word, 0.15, 'innerly')

    # --- 2. Imagery Prompt (5.0s - 11.0s) ---
    # Beeps at 1.5s intervals: 5.0, 6.5, 8.0, 9.5, 11.0
    beep_times = [5.0, 6.5, 8.0, 9.5, 11.0]
    for t_val in beep_times:
        core.wait(t_val - trial_clock.getTime())
        win.flip() # Ensure screen is blank
        beep.stop(); beep.play()

    # --- 3. Post-Beep Silence (11.0s - 12.5s) ---
    # Keeps screen blank for 1.5s before overtly instruction appears
    win.flip()
    core.wait(12.5 - trial_clock.getTime())

    # --- 4. Instruction Overtly (12.5s - 17.5s) ---
    run_flicker_phase(17.5, 'overtly', 'orange', 'please say last imagined unit', 0.06, 'overtly')

    # --- 5. Overt Period (17.5s - 20.5s) ---
    beep.stop(); beep.play() # "Go" signal for speaking
    win.flip() # Blank screen
    core.wait(20.5 - trial_clock.getTime())

    # --- 6. Rest Instruction (20.5s - 23.5s) ---
    class_stim.text = 'rest'
    class_stim.height = 0.15
    class_stim.draw()
    win.flip()
    core.wait(23.5 - trial_clock.getTime())

    # --- 7. Rest Blank Period (23.5s - 33.5s) ---
    beep.stop(); beep.play() # Signal start of long rest
    win.flip()
    core.wait(33.5 - trial_clock.getTime())

    # Final beep to end the trial
    beep.stop(); beep.play()
    core.wait(1.0)

win.close()
core.quit()