import tkinter as tk
import ast
from tkinter import messagebox, filedialog
from tkinter import *
import json

"""
Trial editor GUI made using ChatGPT. USE WITH CAUTION
"""

# Initial dictionary
paramdict = {
    "trial_id": "default",
    "repeats": 2,
    "use_keyboard": True,
    "keyboard_gain": 5.0,
    "keyboard_heading_increment": 20,
    "vr_gain": 1.0,
    "enable2d": False,
    "invert_turn_direction": True,
    "trial_end_coords": [[0, 40], [15, 45]],
    "trial_start_coord": [0, 2],
    "distance_threshold": 1.0,
    "trial_end_delay": 2.0,
    "model": "models/1D-Tunnel_naturalistic.bam",
    "init_position": [0.0, 0.0, 0.2],
    "init_hpr": [0.0, 0.0, 0.0],
    "scale": 0.25,
    "intertrial_duration": 5,
    "max_trial_duration": 20.0,
    "repeat_incomplete_trials": False,
    "inactivity_threshold": 0.0,
    "max_inactive_duration": 5.0,
    "inactivity_leads_to": "flow",
    "inactivity_triggered_flow_duration": 2.0,
    "do2p": True,
    "continuous2p": False,
    "fade_duration": 1.0,
    "stimulation": True,
    "stimulation_mode": "crossing",
    "stim_intensity": 50,
    "stim_coord": [0, 15],
    "crossing_direction": "y",
    "stim_radius": 10.0,
    "stim_onset_time": 2.0,
    "stim_duration": 1.0,
    "optic_flow": False,
    "optic_flow_reference_frame": "allocentric",
    "optic_flow_direction": 0,
    "optic_flow_velocity": -1.0,
    "optic_flow_mode": "zone",
    "optic_flow_coord": [0, 15],
    "optic_flow_radius": 10.0,
    "show_landmarks": True,
    "mirror_landmarks": [True, True],
    "mirror_distance": [2.15, 2.5],
    "landmark_number": 2,
    "landmark_position": [[-1.45, 10, 0.25], [-0.6, 20, 0.25]],
    "landmark_hpr": [[90, 0, 0], [90, 0, 0]],
    "landmarks": ["models/VRE_autoPA_realFish.png", "models/VRE_autoPA_realFish.avi"],
    "landmark_flag": [True, True],
    "handle_collisions": True,
    "collision_radius": 0.3,
    "collider_flag": ["Floor", "Collider"],
    "hide_collider": [False, True]
}


class TrialEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Trial Editor")
        self.geometry("950x640")
        self.entries = {}
        nrows = 27

        # Create input fields for the dictionary
        row = 0
        col = 0
        for key, value in paramdict.items():
            label = tk.Label(self, text=key)
            label.grid(row=row, column=col, sticky="w", padx=20,pady=1)

            entry = tk.Entry(self, width=42)
            entry.insert(0, str(value))
            entry.grid(row=row, column=col+1, sticky="w")
            
            self.entries[key] = entry
            row += 1
            if row == nrows:
                row = 0
                col += 2

        # Save edited paramdict button
        save_button = tk.Button(self, text="Save Trial", command=self.save_trial, width=35)
        save_button.grid(row=row, column=col+1, columnspan=3, sticky="w", padx=0, pady=2)
        row += 1


    def parse_entry(self):
        """
        Parses the text from a Tkinter Entry widget into a corresponding data type.
        
        Tries to parse as:
        - Boolean ('true' or 'false' case insensitive)
        - Integer
        - Float
        - List (if enclosed in brackets)
        - List of Lists (nested lists)
        - String (default if parsing fails)
        
        :param entry_widget: Tkinter Entry widget containing the input text
        :Parse value as str, bool, int, float, list, or list of lists
        """
        
        keys, values = [], []

        for key, entry in self.entries.items():

            keys.append(key)

            raw_text = entry.get().strip()
            if not raw_text:
                values.append(None)
                continue

            # Try parsing as boolean
            if raw_text.lower() in ('true', 'false'):
                if raw_text.lower() == 'true':
                    values.append(True)
                if raw_text.lower() == 'false':
                    values.append(False)
                continue
            
            # Try parsing as integer
            try:
                values.append(int(raw_text))
                continue
            except ValueError:
                pass
            
            # Try parsing as float
            try:
                values.append(float(raw_text))
                continue
            except ValueError:
                pass
            
            # Try parsing as list or nested list
            try:
                parsed_value = ast.literal_eval(raw_text)
                if isinstance(parsed_value, (list, tuple)):
                    values.append(parsed_value)  # Can be a list or list of lists
                    continue
            except (ValueError, SyntaxError):
                pass
            
            # Default return as string
            values.append(raw_text)

        return dict(zip(keys, values))


    def save_trial(self):

        paramdict = self.parse_entry()

        # Save the updated dictionary to a JSON file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(paramdict, f, indent=4)

            print(f"Trial saved to {file_path}")


if __name__ == "__main__":
    app = TrialEditor()
    app.mainloop()
