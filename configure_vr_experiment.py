import json

"""
Make config file
---- The first trial loops infinitely until user input is received. 
---- Place the fish in VR and set up imaging while the infinite VR loop keeps the fish engaged.
---- Subsequent trials are carried out with the specified number of repeats.
"""

configname = "exp_configs/defaultconfig.json"

paramdict = {"trial_id"                     : "default",
             "repeats"                      : 2,
             "use_keyboard"                 : True,
             "keyboard_gain"                : 5.,
             "keyboard_heading_increment"   : 20,
             "fish_gain"                    : 1., # global gain multiplier to apply to fish velocity and heading (use independent gains in tail tracking code for scaling)  
             "enable2d"                     : False,
             "displacement_restart"         : 40,
             "displacement_trial_start"     : 1.,
             "model"                        : "models/1D-Tunnel_naturalistic.bam",
             "init_position"                : [0.,0.,.2],
             "init_hpr"                     : [0.,0.,0.],
             "scale"                        : [.25,.25,.25],
             "intertrial_duration"          : 5,
             "max_trial_duration"           : 20.,
             "do2p"                         : True,
             "continuous2p"                 : False,
             "fade_duration"                : 1.,
             "stimulation"                  : True,
             "stimulation_mode"             : "crossing", # location, crossing (x or y direction), zone or time
             "stim_intensity"               : 50,
             "stim_coord"                   : [0,15],
             "crossing_direction"           : "y",
             "stim_radius"                  : 10.,
             "stim_onset_time"              : 2.,
             "stim_duration"                : 1.,
             "optic_flow"                   : True,
             "optic_flow_reference_frame"   : "allocentric", # allocentric or egocentric
             "optic_flow_direction"         : 90, # angle in degrees when allocentric. ignored when egocentric
             "optic_flow_velocity"          : -1.,
             "optic_flow_mode"              : "zone", # zone or trial
             "optic_flow_coord"             : [0,15],
             "optic_flow_radius"            : 10.,
             "show_landmarks"               : True,
             "mirror_landmarks"             : [True, True],
             "mirror_distance"              : [2.15, 2.5],
             "landmark_number"              : 2,
             "landmark_position"            : [[-1.45,10,0.25], [-.6,20,0.25]], #expand each element to include x,y,z values
             "landmark_hpr"                 : [[90,0,0], [90,0,0]],
             "landmarks"                    : ["models/VRE_autoPA_realFish.png", "models/VRE_autoPA_realFish.avi"],
             "landmark_flag"                : [True, True],
             "handle_collisions"            : True,
             "collision_radius"             : 0.3,
             "collider_flag"                : ["Floor", "Collider"], #complex collider geometries impact performance significantly
             "hide_collider"                : [False, True]}

configdict = {"trials":[paramdict, paramdict, paramdict]} # include multiple dictionaries separated by commas to program a multi-trial experiment

# Save config
with open(configname, 'w', encoding='utf-8') as f:
    json.dump(configdict, f, ensure_ascii=False, indent=4)

# Load config
# with open(configname, 'r') as f:
#     print(json.load(f))

