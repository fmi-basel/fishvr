"""
Use this script to overwrite a subset of parameters values in the config file
"""

import json
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.update()

file = filedialog.askopenfilename(title='Select config file', filetypes=[('JSON files', '*.json')])

params_to_update = {'use_keyboard':False, 'scale':0.98}

with open(file) as f:
    config = json.load(f)
    f.close()

ntrials = len(config['trials'])

for i in range(ntrials):
    for key, value in params_to_update.items():
            if key in config['trials'][i]:
                config['trials'][i][key] = value
            else:
                print("'{}' not found in trial {}".format(key, i))

with open(file, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)
    f.close()