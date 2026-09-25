# Description of configuration parameters

This document contains a detailed description of all the user configurable values in the hardware configurations .ini file and the parameters available to configure a trial in a VR experiment.  

### Preconfigured function keys
The following shortkeys can be used to control the VR and start/stop 2-photon acquisition via external triggering.  
'w' Force progress to next trial regardless of outcome of the current trial  
's' Progress to next trial only if the current trial is completed  
'e' End current trial and progress to next immediately  
'p' Print current position (X, Y) and heading  
't' Toggle 2-photon imaging on/off (start if off, stop if on) 
'r' Toggles in and out of the replay mode in which the sensory experience from past trials are replayed. Available when using the fish_vr_world_panda3d_record_replay.py script

### VR setup file (.ini)  

Example values are included to show the expected input format
| Parameter | Example value/format | Description |
|-----------|-------|-------------|
| framerate | 90 | Framerate settings of the VR update in frames per second |
| syncvideo | False | When True, the VR update rate is synchronized to the refresh rate of the graphics processor. VR update rate and projector refresh occur independently when False |
| use_timer | True | Whether a Teensy or equivalent microcontroller running the vrtiming.ino script is connected or not |
| savepath | log/ | Save path for the log files |
| configpath | exp_configs/ | Path to where the user is directed when running the main VR code to select the experiment configuration file |
| projection_width | 5760 | Width of projection window in pixels |
| projection_height | 1080 | Height of projection window in pixels |
| window_origin_x | 1921 | Window x position |
| window_origin_y | 0 | Window y position |
| mainlight_rgba | .4, .4, .4, 1. | Main light color and alpha |
| mainlight_hpr | 0, 30, 0 | Main light heading, pitch, roll |
| ambient_rgba | .4, .4, .4, 1. | Ambient light color and alpha |
| ncameras | 3 | Number of projectors used. This number must match the number of projector{x}_hpr and display_region{x} specified below |
| projector_fov | 60 | Horizontal field of view of a single projector in degrees. Vertical fov is calculated by Panda3D from the aspect ratio of the window |
| projector0_hpr | 0, 0, 0 | Projector 0 orientation |
| projector1_hpr | 60, 0, 0 | Projector 1 orientation |
| projector2_hpr | -60, 0, 0 | Projector 2 orientation |
| display_region0 | 0.333, 0.666, 0, 1 | Portion of the window occupied by projector 0 along the horizontal axis |
| display_region1 | 0, 0.333, 0, 1 | Portion of the window occupied by projector 0 along the horizontal axis |
| display_region2 | 0.666, 0.999, 0, 1 | Portion of the window occupied by projector 0 along the horizontal axis |
| serial_port | COM4 | Serial port where the Teensy or equivalent microcontroller is connected |
| serial_timeout | 0.004 | Timeout of the serial connection with the Teensy in seconds |
| udp_ip | 127.0.0.1 | UDP address where a broadcast from the tail tracking code is expected |
| udp_port | 5005 | UDP port to for receiving values from the tail tracking code |
| udp_buffer_size | 64 | Buffer size for UDP communication |
| udp_timeout | 0.001 | Timeout for UDP communication |

### Configure VR trial (configure_vr_trials_gui.py)

Trials are saved as a json file and are converted to an experiment configuration file, which consists of a json object of one or more trials, using configure_vr_experiment_gui.py.
All distances are assumed to be metres in the VR model and time is specified in seconds. 
| Parameter | Example value/format | Description |
|-----------|-------|-------------|
| trial_id | "default" | Unique identifier for the trial |
| repeats | 2 | Number of times to repeat the trial |
| use_keyboard | True | Toggle between keyboard or tail tracking input to move through the VR |
| keyboard_gain | 5.0 | Sensitivity multiplier for keyboard input |
| keyboard_heading_increment | 20 | Degrees per second to update heading directin upon keyboard input |
| vr_gain | 1.0 | Global gain multiplier for vr update with input from tail tracking. Independent multipliers for velocity and heading update can be set in the tracking code |
| enable2d | False | constrains movement of the fish to 1D when False |
| invert_turn_direction | True | Invert left/right turning direction |
| trial_start_coord | [0, 2] | Starting position  of fish [x, y] |
| trial_end_coords | [[0, 40], [15, 45]] | position of end of trial in VR [[x1, y1], [x2, y2],.... [xn, yn]] |
| distance_threshold | 1.0 | Radius within which the fish is considered to have reached a coordinate, such as the end points of a trial |
| trial_end_delay | 2.0 | Delay to end a trial once an end coordinate is reached |
| model | "models/1D-Tunnel_naturalistic.bam" | Path to 3D environment model |
| init_position | [0.0, 0.0, 0.2] | Initial camera position [x, y, z] |
| init_hpr | [0.0, 0.0, 0.0] | Initial heading, pitch, roll angles |
| scale | 0.25 | Scale factor to apply to the 3D model of the environment |
| intertrial_duration | 5 | Duration between trials |
| max_trial_duration | 20.0 | Maximum trial duration |
| repeat_incomplete_trials | False | Repeat trials that are not completed within the allowed maximum duration |
| inactivity_threshold | 0.0 | Threshold velocity below which the fish is considered 'inactive' |
| max_inactive_duration | 5.0 | Continuous period of inactivity which when crossed can be used to trigger an action |
| inactivity_leads_to | "flow" | Action triggered by inactivity |
| inactivity_triggered_flow_duration | 2.0 | Duration in seconds of inactivity-triggered optic flow |
| do2p | True | If True enables 2P start/stop triggers|
| continuous2p | False | Toggles continuous or trial chunked 2P imaging mode |
| fade_duration | 1.0 | Fade in/out duration at end of a trial to mask abrupt teleportation |
| stimulation | True | Enable digital stimulation triggers. Corresponding parameter fields can be left blank when False |
| nstimchannels | 8 | Number of stimulation channels |
| use_channel | [False, False, False, False, False, False, False, False] | Enable/disable each channel |
| stimulation_mode | "crossing" | Logic that triggers stimulation. Refer to the comments in configure_vr_trials.py. Can be a list specifying different modes for each channel |
| stim_intensity | 50 | Intensity of analog stimulation in percentage. Corresponds to an unbuffered analog voltage of 0-3.3V output from the Teensy |
| stim_coord | [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]] | VR coordinates linked to the digital stimulation trigger outputs, in their respective trigger modes |
| crossing_direction | ["y","y","y","y","y","y","y","y"] | Direction of fish crossing the stimulation location to be used when the mode is set to "crossing" |
| stim_radius | [1.,1.,1.,1.,1.,1.,1.,1.] | Radius in the VR per channel around a coordinate. Only applicable when the mode is set to "location" or "zone" |
| stim_onset_time | [1.,1.,1.,1.,1.,1.,1.,1.] | Stimulus onset time when in "time" mode |
| stim_duration | [1.,1.,1.,1.,1.,1.,1.,1.] | Duration of stimulation pulse when in "time" mode |
| stim_pulse_duration | 0.05 | Duration of a digital output pulse. Applicable to "crossing" and "location" modes |
| optic_flow | False | Enable optic flow. Corresponding parameter fields can be left blank if False |
| optic_flow_reference_frame | "allocentric" | Reference frame for optic flow. Can be "allocentric" or "egocentric" |
| optic_flow_direction | 0 | Direction of optic flow along the horizontal plane in degrees in the allocentric or egocentric frame of reference |
| optic_flow_velocity | -1.0 | Optic flow velocity |
| optic_flow_mode | "zone" | Mode that determines how optic flow is triggered. Can be "trial" or "zone" |
| optic_flow_coord | [0, 15] | Optic flow coordinate at or around which optic flow is triggered |
| optic_flow_radius | 10.0 | Radius around the specified coordinate within which optic flow is triggered when the mode is set to "zone" |
| show_landmarks | True | Display landmarks in the VR world. These can be image or video files |
| landmark_scale | 0.08 | Scale of images or movies |
| mirror_landmarks | [True, True] | Display a mirrored copy of a landmark |
| mirror_distance | [2.15, 2.5] | Distance for mirroring |
| landmark_number | 2 | Number of landmarks |
| landmark_position | [[-1.45, 10, 0.25], [-0.6, 20, 0.25]] | Position of each landmark [x, y, z] |
| landmark_hpr | [[90, 0, 0], [90, 0, 0]] | Orientation of each landmark, heading, pitch, roll |
| landmarks | ["models/landmark.png", "models/movie.avi"] | Landmark files, expected to be in the specified path |
| landmark_flag | [True, True] | Enable/disable each landmark |
| hide_movie | False | If set to True, movies shown as landmarks are hidden by a background texture placed on top and revealed by proximity |
| background_texture | [False, False] | Which landmark to use as the background texture to hide the movie |
| movie_onset_distance | 0.075 | Distance to reveal the hidden movie by removing the background texture |
| movie_onset_delay | 0.0 | Delay after the fish is within the onset distance after which the movie is revealed |
| handle_collisions | True | Enable Panda3D collision handling |
| collision_radius | 0.3 | Collision radius |
| collider_flag | ["Floor", "Collider"] | Name of nodes in the VR model file for which collisions are detected |
| hide_collider | [False, True] | Hide a node flagged as a collider from being displayed in the VR |