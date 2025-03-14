import tkinter as tk
from tkinter import filedialog
import json
import random

"""
Experiment configuration app made using ChatGPT with minor modifications. USE WITH CAUTION
User interface wrapper around the makeconfig function in configure_vr_experiment.py
Functionality should be identical to configure_vr_experiment.py 
"""

class ExperimentConfigurationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Configuration App")
        self.width = 500
        self.height = 100
        self.maxwidth = 350
        self.root.geometry(f"{self.width}x{self.height}")  # Initial size
        
        self.file_list = []
        self.int_values = []  # List to store integer values
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)
        
        self.add_button = tk.Button(self.button_frame, text="Add Trial", command=self.add_file)
        self.add_button.pack(side="left", padx=5)
        
        self.randomize_var = tk.BooleanVar()
        self.randomize_checkbox = tk.Checkbutton(self.button_frame, text="Randomize", variable=self.randomize_var)
        self.randomize_checkbox.pack(side="left", padx=5)
        
        self.save_button = tk.Button(self.button_frame, text="Save Configuration", command=self.save_configuration)
        self.save_button.pack(side="left", padx=5)

        self.update_display()
        self.adjust_window_size()
    

    def add_file(self):
        file_path = filedialog.askopenfilename(title="Select File", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.file_list.append(file_path)
            self.int_values.append(tk.IntVar(value=1))  # Add corresponding integer variable
            self.update_display()
            self.adjust_window_size()
    

    def remove_file(self, index):
        if 0 <= index < len(self.file_list):
            self.file_list.pop(index)
            self.int_values.pop(index)
            self.update_display()
            self.adjust_window_size()
    

    def save_configuration(self):

        saveas = filedialog.asksaveasfilename(initialdir='.', title='Save configuration', defaultextension='.csv', filetypes=[('JSON files', '*.json')])

        if saveas is not None and len(saveas) > 0:
            self.makeconfig(saveas=saveas)


    def update_display(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.frame)
        header_frame.pack(fill="x", padx=5, pady=2)
        
        file_label = tk.Label(header_frame, text="File Name", anchor="w", font=("Arial", 10, "bold"), width=42)
        file_label.pack(side="left", fill="x", expand=True)
        
        repeats_label = tk.Label(header_frame, text="Repeats", font=("Arial", 10, "bold"), width=10)
        repeats_label.pack(side="left", padx=0)
        
        spacer = tk.Label(header_frame, text=" ", width=10)  # Empty label for alignment
        spacer.pack(side="right")

        widths = []
        
        for i, file_path in enumerate(self.file_list):
            file_frame = tk.Frame(self.frame)
            file_frame.pack(fill="x", padx=5, pady=2)
            
            label = tk.Label(file_frame, text=file_path, anchor="w")
            label.pack(side="left", fill="x", expand=True)
            
            entry = tk.Entry(file_frame, textvariable=self.int_values[i], width=5)
            entry.pack(side="left", padx=5)
            
            remove_button = tk.Button(file_frame, text="Remove", command=lambda idx=i: self.remove_file(idx))
            remove_button.pack(side="right")

            widths.append(label.winfo_reqwidth())

        if len(widths) > 0:
            self.maxwidth = max(widths)
        else:
            self.maxwidth = 350
    

    def adjust_window_size(self):
        new_height = max(100, 100 + len(self.file_list) * 25)
        new_width = self.maxwidth + 150
        self.root.geometry(f"{new_width}x{new_height}")


    def makeconfig(self, saveas):

        trialfiles = self.file_list
        trialrepeats = [int(var.get()) for var in self.int_values]
        randomize_trial_order = self.randomize_var.get()

        trials = []
        for trialfile, repeats in zip(trialfiles, trialrepeats):
            for i in range(repeats):
                with open(trialfile, 'r') as f:
                    trials.append(json.load(f))

        if randomize_trial_order and len(trials) > 2: # keep the first trial in place and randomize the rest
            first_trial = [trials[0]]
            trials = trials[1:]
            random.shuffle(trials)
            trials = first_trial + trials

        configdict = {"trials":trials} # combine trials

        # Save config
        with open(saveas, 'w', encoding='utf-8') as f:
            json.dump(configdict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentConfigurationApp(root)
    root.mainloop()