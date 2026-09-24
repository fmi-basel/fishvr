# Manual

This document contains a detailed description of all the user configurable values in the hardware configurations .ini file and the Trial Configuration.  

### VR setup file (.ini)  

framerate = 90 (framerate settings of the projection/VR update in frames per second). 
syncvideo = False ()  
use_timer = False()  
savepath = log/ (save path for the log file)  
configpath = exp_configs/ (path to where the user is directed when running the main VR code to select the Experiment Configuration file)  
projection_width = 5760 (width of projection pixels)  
projection_height = 1080 (height of projection pixels)  
window_origin_x = 1921 ()  
window_origin_y = 0 ()  
mainlight_rgba = .4, .4, .4, 1. ()  
mainlight_hpr = 0, 30, 0 ()  
ambient_rgba = .4, .4, .4, 1. ()  
ncameras = 3 (number of projectors used)  
projector_fov = 60  (Diagonal field of view of the projection in mm)  
projector0_hpr = 0, 0, 0 ()  
projector1_hpr = 60, 0, 0 ()  
projector2_hpr = -60, 0, 0 ()  
display_region0 = 0.333, 0.666, 0, 1  ()  
display_region1 = 0, 0.333, 0, 1 ()  
display_region2 = 0.666, 0.999, 0, 1 ()  
serial_port = COM4 (Serial port where the Teensy microcontroller is connected to)  
serial_timeout = 0.004 (Timeout of the serial connection with the Teensy)  
udp_ip = 127.0.0.1 (UDP address where the VR code is listening to the broadcast from the Tail Tracking code)  
udp_port = 5005 (UDP address where the VR code is listening to the broadcast from the Tail Tracking code)  
udp_buffer_size = 64 (buffer from the UDP)  
udp_timeout = 0.001 (Timeout from the UDP)  

