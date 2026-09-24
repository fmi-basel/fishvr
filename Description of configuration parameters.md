# Manual

This document contains a detailed description of all the user configurable values in the hardware configurations .ini file and the Trial Configuration.  

### VR setup file (.ini)  

Example values are showing the format
| Parameter | Example value/format | Description |
|-----------|-------|-------------|
| framerate | 90 | Framerate settings of the projection/VR update in frames per second |
| syncvideo | False | Sync video setting |
| use_timer | False | Timer usage |
| savepath | log/ | Save path for the log file |
| configpath | exp_configs/ | Path to where the user is directed when running the main VR code to select the Experiment Configuration file |
| projection_width | 5760 | Width of projection pixels |
| projection_height | 1080 | Height of projection pixels |
| window_origin_x | 1921 | Window x position |
| window_origin_y | 0 | Window y position |
| mainlight_rgba | .4, .4, .4, 1. | Main light color and alpha |
| mainlight_hpr | 0, 30, 0 | Main light heading, pitch, roll |
| ambient_rgba | .4, .4, .4, 1. | Ambient light color and alpha |
| ncameras | 3 | Number of projectors used |
| projector_fov | 60 | Diagonal field of view of the projection in mm |
| projector0_hpr | 0, 0, 0 | Projector 0 orientation |
| projector1_hpr | 60, 0, 0 | Projector 1 orientation |
| projector2_hpr | -60, 0, 0 | Projector 2 orientation |
| display_region0 | 0.333, 0.666, 0, 1 | Display region 0 |
| display_region1 | 0, 0.333, 0, 1 | Display region 1 |
| display_region2 | 0.666, 0.999, 0, 1 | Display region 2 |
| serial_port | COM4 | Serial port where the Teensy microcontroller is connected to |
| serial_timeout | 0.004 | Timeout of the serial connection with the Teensy |
| udp_ip | 127.0.0.1 | UDP address where the VR code is listening to the broadcast from the Tail Tracking code |
| udp_port | 5005 | UDP port where the VR code is listening to the broadcast from the Tail Tracking code |
| udp_buffer_size | 64 | Buffer from the UDP |
| udp_timeout | 0.001 | Timeout from the UDP |

## Configure VR trial (configure_vr_trial_gui.py)

# Note on VR dimensions vs real world distance

| Parameter | Example value/format | Description |
|-----------|-------|-------------|
| trial_id | "default" | Unique identifier for the trial |
| repeats | 2 | Number of times to repeat the trial |
| use_keyboard | True | Enable keyboard control |
| keyboard_gain | 5.0 | Sensitivity multiplier for keyboard input |
| keyboard_heading_increment | 20 | Degrees per keyboard press |
| vr_gain | 1.0 | Gain multiplier for ?? |
| enable2d | False | constrains movement of fish in 2D when True, becomes 3D when False  |
| invert_turn_direction | True | Invert left/right turning direction |
| trial_start_coord | [0, 2] | Starting position  of fish [x, y] |
| trial_end_coords | [[0, 40], [15, 45]] | position of end of trial in VR [[x1, y1], [x2, y2]] |
| distance_threshold | 1.0 | Distance ??? |
| trial_end_delay | 2.0 | Delay in seconds after reaching VR end |
| model | "models/1D-Tunnel_naturalistic.bam" | Path to 3D environment model |
| init_position | [0.0, 0.0, 0.2] | Initial camera position [x, y, z] |
| init_hpr | [0.0, 0.0, 0.0] | Initial heading, pitch, roll angles |
| scale | 0.25 | Scale factor for the environment |
| intertrial_duration | 5 | Duration in seconds between trials in seconds |
| max_trial_duration | 20.0 | Maximum trial duration in seconds |
| repeat_incomplete_trials | False | Repeat trials that don't reach end |
| inactivity_threshold | 0.0 | Movement threshold in ??? to detect inactivity |
| max_inactive_duration | 5.0 | Max time in seconds without movement before action |
| inactivity_leads_to | "flow" | Action triggered by inactivity ??? |
| inactivity_triggered_flow_duration | 2.0 | Duration in seconds of inactivity-triggered flow |
| do2p | True | If True enables 2P start/stop triggers|
| continuous2p | False | Continuous 2P imaging mode |
| fade_duration | 1.0 | Fade in/out duration in seconds |
| stimulation | True | Enable stimulation configurations. Everything below will not be taken into account when False |
| nstimchannels | 8 | Number of stimulation channels |
| use_channel | [False, False, False, False, False, False, False, False] | Enable/disable each channel |
| stimulation_mode | "crossing" | Stimulation pattern mode |


| stim_intensity | 50 | Intensity of analog stimulation. 0-3.3V of Teensy pin distributed over 0-100 |
| stim_coord | [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]] | Coordinates within the VR where stimulus might be triggered |
| crossing_direction | ["y","y","y","y","y","y","y","y"] | Direction of fish crossing the stimulation location  |
| stim_radius | [1.,1.,1.,1.,1.,1.,1.,1.] | Stimulus radius in the VR per channel |
| stim_onset_time | [1.,1.,1.,1.,1.,1.,1.,1.] | Stimulus onset time in ??? per channel |
| stim_duration | [1.,1.,1.,1.,1.,1.,1.,1.] | Stimulus duration in ??? per channel |
| stim_pulse_duration | 0.05 | Duration in ??? of stimulus pulses |
| optic_flow | False | Enable optic flow stimulus |
| optic_flow_reference_frame | "allocentric" | Reference frame for optic flow |
| optic_flow_direction | 0 | Direction of optic flow movement in ??? |
| optic_flow_velocity | -1.0 | Velocity in ??? of optic flow |
| optic_flow_mode | "zone" | Optic flow rendering mode |


| optic_flow_coord | [0, 15] | Optic flow zone coordinates in VR|
| optic_flow_radius | 10.0 | Radius of optic flow zone |
| show_landmarks | True | Display landmark objects |
| landmark_scale | 0.08 | Scale of landmark models |
| mirror_landmarks | [True, True] | Mirror landmarks left/right |
| mirror_distance | [2.15, 2.5] | Distance for mirroring per landmark |
| landmark_number | 2 | Number of landmarks |
| landmark_position | [[-1.45, 10, 0.25], [-0.6, 20, 0.25]] | Position of each landmark [x, y, z] |
| landmark_hpr | [[90, 0, 0], [90, 0, 0]] | Orientation of each landmark, heading, pitch, roll |
| landmarks | ["models/VRE_autoPA_realFish.png", "models/VRE_autoPA_realFish.avi"] | Landmark files, expected to be in ??? folder |
| landmark_flag | [True, True] | ??? Enable/disable each landmark |
| hide_movie | False | Hide movie |
| background_texture | [False, False] | Enable background textures |
| movie_onset_distance | 0.075 | Distance in m ??? to trigger movie display |
| movie_onset_delay | 0.0 | Delay in seconds ??? before movie starts |
| handle_collisions | True | Enable collision detection |
| collision_radius | 0.3 | Collision detection radius in mm ??? |
| collider_flag | ["Floor", "Collider"] | Collision objects to enable |
| hide_collider | [False, True] | Hide collision objects visually |

