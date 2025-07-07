import json

"""
Program a VR trial
---- Set trial parameters in the dictionary
---- Save the trial as a json file
---- Load the trial and save a configuration file to test with the panda3D VR code
---- The first trial is set to loop infinitely until user input is received, ignoring the number of repeats parameter in the trial configuration 
"""

savepath = "exp_configs/" # path to save trial and corresponding config files (if savetestconfig is True)

trialname = "trial_sample1"

configname = "defaultconfig"

# multiple saved trials can be loaded and combined into a single configuration file to program a multi-trial experiment
# refer to configure_vr_experiment.py for how to program a multi-trial experiment
savetrial = False

# use this configuration file to test whether the trial is executed correctly and the environment is set up as intended
savetestconfig = False # a test configuration is saved

paramdict = {"trial_id"                             : trialname,
             "repeats"                              : 2,
             "use_keyboard"                         : True,
             "keyboard_gain"                        : 5.,
             "keyboard_heading_increment"           : 20,
             "vr_gain"                              : 1., # global gain multiplier to apply to fish velocity and heading (use independent gains in tail tracking code for scaling)  
             "enable2d"                             : False,
             "invert_turn_direction"                : True,
             "trial_start_coord"                    : [0,2],
             "trial_end_coords"                     : [[0,40], [15,45]],
             "distance_threshold"                   : 1.,
             "trial_end_delay"                      : 2.,
             "model"                                : "models/1D-Tunnel_naturalistic.bam",
             "init_position"                        : [0.,0.,.2],
             "init_hpr"                             : [0.,0.,0.],
             "scale"                                : 0.25,
             "intertrial_duration"                  : 5,
             "max_trial_duration"                   : 20.,
             "repeat_incomplete_trials"             : False, # first trial loops until user input is received, irrespective of this parameter 
             "inactivity_threshold"                 : 0.,
             "max_inactive_duration"                : 5.,
             "inactivity_leads_to"                  : "flow", # "reset", "flow" or "nothing"
             "inactivity_triggered_flow_duration"   : 2.,  
             "do2p"                                 : True,
             "continuous2p"                         : False,
             "fade_duration"                        : 1.,
             "stimulation"                          : True,
             "nstimchannels"                        : 8, # number of channels used out of 8 available. channels are assigned in sequential order
             "stimulation_mode"                     : "crossing", # location, crossing (x or y direction), zone or time
             "stim_intensity"                       : 50, # only one intensity per trial for all stimulus channels
             "stim_coord"                           : [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]], # Placeholder values must be set for all stiumulus channels, even if not used
             "crossing_direction"                   : ["y","y","y","y","y","y","y","y"], # direction of crossing for each stimulus channel, only used when stimulation_mode is "crossing"
             "stim_radius"                          : [1.,1.,1.,1.,1.,1.,1.,1.], # radius of the stimulus zone for each channel, only used when stimulation_mode is "zone"
             "stim_onset_time"                      : [1.,1.,1.,1.,1.,1.,1.,1.], # onset time of the stimulus for each channel, only used when stimulation_mode is "time"
             "stim_duration"                        : [1.,1.,1.,1.,1.,1.,1.,1.], # duration of the stimulus for each channel, applies to modes that are software timed ('continuous') and not 'pulsed'
             "stim_pulse_duration"                  : 0.05, # duration of a stimulus trigger pulse in seconds when pulsed modes are used
             "optic_flow"                           : False,
             "optic_flow_reference_frame"           : "allocentric", # allocentric or egocentric
             "optic_flow_direction"                 : 0, # angle in degrees when allocentric. ignored when egocentric
             "optic_flow_velocity"                  : -1.,
             "optic_flow_mode"                      : "zone", # zone or trial
             "optic_flow_coord"                     : [0,15],
             "optic_flow_radius"                    : 10.,
             "show_landmarks"                       : True,
             "landmark_scale"                       : 0.08,
             "mirror_landmarks"                     : [True, True],
             "mirror_distance"                      : [2.15, 2.5],
             "landmark_number"                      : 2,
             "landmark_position"                    : [[-1.45,10,0.25], [-.6,20,0.25]], # landmark coordinates
             "landmark_hpr"                         : [[90,0,0], [90,0,0]], # landmark orientation
             "landmarks"                            : ["models/VRE_autoPA_realFish.png", "models/VRE_autoPA_realFish.avi"], # landmark files (image or video)
             "landmark_flag"                        : [True, True], # Show or hide landmarks. Can be updated in spinCameraTask to make landmarks interactive
             "handle_collisions"                    : True,
             "collision_radius"                     : 0.3,
             "collider_flag"                        : ["Floor", "Collider"], #complex collider geometries impact performance significantly
             "hide_collider"                        : [False, True]}


# save trial configuration
if savetrial:
    trialpath = savepath + trialname + '.json'
    with open(trialpath, 'w', encoding='utf-8') as f:
        json.dump(paramdict, f, ensure_ascii=False, indent=4)


if savetestconfig:

    # load saved trial configuration
    with open(trialpath, 'r') as f:
        trial = json.load(f)

    configdict = {"trials":[trial]} # include multiple dictionaries separated by commas to program a multi-trial experiment

    # Save config
    configpath = savepath + configname + '.json'
    with open(configpath, 'w', encoding='utf-8') as f:
        json.dump(configdict, f, ensure_ascii=False, indent=4)

    # Load config
    with open(configpath, 'r') as f:
        print(json.load(f))
