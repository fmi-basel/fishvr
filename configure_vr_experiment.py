import json
import random

"""
Make config file
---- The first trial is set to loop infinitely until user input is received, ignoring the number of repeats parameter in the trial configuration  
---- Place the fish in VR and set up imaging while the infinite VR loop keeps the fish engaged.
---- Subsequent trials are carried out with the specified number of repeats.
"""

def makeconfig(trialfiles, trialrepeats, configfile, randomize_trial_order=False, saveconfig=True):

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
    if saveconfig:
        with open(configfile, 'w', encoding='utf-8') as f:
            json.dump(configdict, f, ensure_ascii=False, indent=4)


configfile = "exp_configs/defaultconfig.json"
saveconfig = True

trialfiles = ["exp_configs/trials/trial_sample1.json", "exp_configs/trials/trial_sample2.json"]
repeats = [1, 1]
randomize_trial_order = False # The first trial, which loops infinitely until the experiment is begun is kept in place. Subsequent trials are randomized. 

makeconfig(trialfiles, repeats, configfile, randomize_trial_order=randomize_trial_order, saveconfig=saveconfig)