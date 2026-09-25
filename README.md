# Virtual reality software for headfixed (zebra) fish 

This software package is linked to the publication 'supercoolfish VR behavior' [LINK].  
If you use this code for your publication, please cite us.

### Overview
This software package was designed to allow the user to configure and run virtual reality (VR) experiments intended for headfixed zebrafish (*Danio rerio*). Landmarks, stimulation triggers, repetitions, block structures and other conditions can be configured and saved. Inputs are the position updates from the tail-tracking script from a UDP broadcast, a Blender VR model, a setup configuration and an experiment configuration file. Tail tracking is used to update the VR in real time. The executed trial configurations and a frame-by-frame log of the VR experiment are saved as outputs.

## System requirements
- PC with a graphics card supporting multiple displays as needed  
- The software has been extensively tested on Windows 10 and 11 and is expected to also run across OS platforms that support the specific requirements of the python environment

## Installation instructions
Create a python environment with the dependencies listed in the environment.yml file. This file includes dependencies needed for both the VR and the tail tracking workflows.

## User manual  
A detailed description of all the configuration options can be found [here](/Description_of_configuration_parameters.md).  

### Instructions to run a VR experiment:
- Create a python environment with the necessary dependencies
- Export a 3D model of the VR world made in Blender as a .gltf or .glb file    
- Convert the .gltf or .glb file to a .bam file using the gltf2bam command line utility  which will be installed as part of the panda3d-gltf package (see dependencies)    
- Make a VR setup configuration file (.ini)  
- Make a trial configuration with configure_vr_trials_gui.py, saved as a .json file ([see here](/Description_of_configuration_parameters.md))  
- Combine trial configuration(s) into an experiment configuration with configure_vr_experiment_gui.py, also in .json format  
- An experiment configuration can be made using a single trial or by combining multiple trials in random or fixed orders  
- Block structures can be created by combining experiment configurations together to generate a new experiment  
- By default, the first trial is set to repeat indefinitely until user input forces a progress to the next trial ([see here](/Description_of_configuration_parameters.md))  
- If running tail tracking, make a .ini parameters file for the tail tracking software package  
- Initiate tail tracking to start broadcasting a UDP message of the real time tracking output (see instructions in the tail tracking package)  
- Run VR with either fish_vr_world_panda3d.py  or fish_vr_world_panda3d_record_replay.py

### To run the software with an example:  
Run fish_vr_world_panda3d.py and select an example [Setup Configuration file](setup/vrsetup_3projectors.ini) and then [EXAMPLE EXPERIMENT CONFIG] when prompted, log files can optionally be saved. An example VR environment will be loaded and the VR started. Arrow keys can be used to navigate in the VR.  

## Hardware
A Teensy 4.0 microcontroller running the vrtiming.ino firmware was used to trigger 2-photon acquisition, log 2-photon frame count as well as generate TTL triggers to control stimulus delivery (such as odours or light sources for optogenetics).
Documentation on the interface circuit can be found [here](Interface_circuit_for_teensy_4_0).  

For the odour delivery, we level-shifted the output from the Teensy to 5V with a 74ACT541 to control the valve controller. Pull-down resistors were used before the VR Timing Teensy and after the 74ACT541 to prevent channels from floating, thereby causing rapid switching between ON/OFF states. Circuit drawings can be found [here](Interface_circuit_for_teensy_4_0). An Automate Scientific ValveLink8.2/ 8.3 controller and valve system and odour manifold were used to deliver the odour compounds. [LINK](https://www.autom8.com/shop/perfusion-equipment/perfusion-accessories/micro-manifold-8-into-1-with-flow-control-ptfe-inert/)  

The adult zebrafish were mounted with a headbar in a semi-hexagonal tank (see Huang et al., 2020, [LINK](https://doi.org/10.1038/s41592-020-0759-2)). The VR was projected on the front and sides of the tank with three VOPLLS N3 projectors.  

## References
Inspiration for parts of this code has been drawn from among others:  
- Štih V, Petrucco L, Kist AM, Portugues R (2019) Stytra: An open-source, integrated system for stimulation, tracking and closed-loop behavioral experiments. PLoS Comput Biol 15(4): e1006699. https://doi.org/10.1371/journal.pcbi.1006699  
- Huang, KH., Rupprecht, P., Frank, T. et al. A virtual reality system to analyze neural activity and behavior in adult zebrafish. Nat Methods 17, 343–351 (2020). https://doi.org/10.1038/s41592-020-0759-2  
- Desai NS, Gray R and Johnston D (2017) A Dynamic Clamp on Every Rig DOI: http://dx.doi.org/10.1523/ENEURO.0250-17.2017   

## Authors
Alexandre Javier, Sriram Narayanan, Lukas Anneser, Jaap van Krugten, Rainer W. Friedrich
