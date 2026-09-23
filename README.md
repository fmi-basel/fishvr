# Virtual reality software for headfixed (zebra) fish 

This software package is linked to the publication 'supercoolfish VR behavior' [LINK].  
If you use use this code for your publication, please cite us.

### Overview
This software package was designed to allow the user to configure and run a virtual reality (VR) experiment intended for headfixed zebrafish (*Danio rerio*). Repetitions, conditions and triggers can be configured and saved. Inputs are the position updates from the tail-tracking script via [XXX], the Blendr VR model and the experiment configuration of the XXX. Outputs are the updated VR over the projectors stimuli triggers and log file.

## System requirements
PC
python

## Installation instructions
Use the environment.yml file to download the necessary packages.

## User manual  

For a detailed description of all the setting options, click here.  
For documentation on some user-editable functions, see LINK.  

To get the software running with an example:  
Run fish_vr_world_panda3d.py and select [EXAMPLE SETUP CONFIG] and [EXAMPLE EXPERIMENT CONFIG], the option to determine the log save path can be canceled without consequences. An example VR environment will be loaded and the VR started. Arrows can be used to navigate in the VR.

The package is structured as follows:
The setup configurations (.ini) are user settings that are specific to your experimental hardware. To make it easy to repeat trials or make blocks of trials, first trials are configured, which can then be configured to be grouped and/or repeated in an experiment configuration. The setup config file (.ini) and experiment config file (.json) are selected when the main software is launched along with where the log file will be saved.

To set up your own experiment, one would have to design a .bam VR environment.

Then, to configure a trial, use configure_vr_trials_gui.py  
    This will launch a user interface in which the settings of a trial can be configured. While the first column is compulsory, the second and third column, below 'stimulation' are optional when 'stimulation' is set to False. If 'stimulation' is True, i.a. the stimulation mode, location, duration and /or landmarks (images or videos) can be configured. The stimulation channels refer to the pins on a Teensy microcontroller. When activated these will give a 3V signal and could for example be used to toggle odour stimulation in a certain location for a certain duration within the VR. 

-configure_vr_experiment_gui.py  
-To run the VR software: fish_vr_world_panda3d.py 


To get started and get the 
-keyboard shortcuts

## Hardware
A Teensy 4.0 microcontroller was used for the timing and trigger control.  
The adult zebrafish were mounted with a headbar in a 4 sided tank. The VR was projected on the front and sides of the tank with three VOPLLS N3 projectors.  
For the odour delivery, the 3.3V Teensy output was bumped to 5V with a 74ACT541 to control the valve controller. Pull-down resistors were used before the VR Timing Teensy and after the 74ACT541to prevent channels from floating causing rapid switching between ON/OFF states. Circuit drawings can be found [here](Interface_circuit_for_teensy_4_0).   
An Automate Scientific ValveLink8.2/ 8.3 controller and valve system and odour manifold were used to deliver the odour compounds. [LINK](https://www.autom8.com/shop/perfusion-equipment/perfusion-accessories/micro-manifold-8-into-1-with-flow-control-ptfe-inert/)


## License
check with FMI

## References
Inspiration for parts of this code has been drawn from among others:  
Štih V, Petrucco L, Kist AM, Portugues R (2019) Stytra: An open-source, integrated system for stimulation, tracking and closed-loop behavioral experiments. PLOS Computational Biology. DOI: 10.1371/journal.pcbi.1006699  
Huang KH, Rupprecht P, Frank T, Kawakami K, Bouwmeester T, Friedrich RW (2020) A virtual reality system to analyze neural activity and behavior in adult zebrafish. Nature Methods. DOI: 10.1038/s41592-020-0759-2  
Desai NS, Gray R and Johnston D (2017) A Dynamic Clamp on Every Rig DOI: http://dx.doi.org/10.1523/ENEURO.0250-17.2017  

## Authors
Alex Javier, Sriram Narayanan, Jan Eckhardt, Jaap van Krugten, Rainer Friedrich
