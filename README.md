# Virtual reality software for headfixed (zebra) fish 

This software package is linked to the publication 'supercoolfish VR behavior' [LINK].  
If you use use this code for your publication, please cite us.

### Overview
This software package was designed to allow the user to configure and run a virtual reality (VR) experiment intended for headfixed zebrafish (*Danio rerio*). Landmarks, stimulation triggers, repetitions and other conditions can be configured and saved. Inputs are the position updates from the tail-tracking script from the UDP broadcast, the Blendr VR model, the setup configuration and the experiment configuration of the Trials. Outputs are the updated VR, stimuli triggers and a log file.

## System requirements
PC
python

## Installation instructions
Use the environment.yml file to download the necessary packages.

## User manual  

A detailed description of all the configuration options can be found [here](/Description_of_configuration_parameters.md).  
Documentation on some user-editable functions can be found [here]( )

### To run the software with an example:  
Run fish_vr_world_panda3d.py and select an example [Setup Configuration file](setup/vrsetup_3projectors.ini) and then [EXAMPLE EXPERIMENT CONFIG] when prompted, the option to determine the log save path can be canceled without consequences. An example VR environment will be loaded and the VR started. Arrows can be used to navigate in the VR.  

### The package is structured as follows:

- Create a virtual reality environment (.bam) in for example Blendr  
- Make VR Setup configuration file (.ini)  
- Make Trial Configuration with configure_vr_trials_gui.py  
- Combine Trial Configurations into an Experiment Configuration with configure_vr_experiment_gui.py  
- Run VR with fish_vr_world_panda3d.py  

To set up your own experiment, one would first have to design a .bam VR environment.  
The VR Setup file (.ini) are user settings that are specific to your experimental hardware setup.  
To make it easy to repeat Trials or make Blocks of a specific sequence of Trials, first Trials are configured, which can then be grouped and/or repeated in an Experiment Configuration.  
The Setup Config file (.ini) and Experiment Config file (.json) are selected, and the log file save path is chosen when the main software is launched.  

To configure a Trial, use configure_vr_trials_gui.py.  
This will launch a user interface in which the settings of a Trial can be configured. While the first column is compulsory, the second and third column, below 'stimulation', are optional when 'stimulation' is set to False. If 'stimulation' is True, i.a. the stimulation mode, triggers, location, duration and/or landmarks (images or videos) can be configured. The stimulation channels refer to the pins on a Teensy microcontroller. When activated, these will give a digital 3.3V signal and could for example be used to toggle odour stimulation in a certain location for a certain duration within the VR. An additional single analog pin on the Teensy board is available for example for brightness control of optogenetic stimulation. The resulting Trial Configuration is saved as .json.  

Once one or more Trials are configured, they can be combined using configure_vr_experiment_gui.py  
This will launch a small GUI that will let one add Trials and set the repeats of the Trial. This can be repeated with different Trial Configuration files to create a Trial Block. Also Trial Blocks can be added in this GUI to make it easy to combine multiple Trial Blocks into an Experiment Configuration. The resulting Experiment Configuration is selected when the main code is launched.  

Running fish_vr_world_panda3d.py will start the VR experiment. The VR will be projected and updated with the data stream from the Tail Tracking UDP broadcast, stimuli and or landmarks will be triggered at the specified locations for the specified duration, 2P acquisition can be started/stopped and the logfile will be update with the VR information and 2P frame count.  


## Hardware
Teensy 4.0 microcontroller was used to trigger for example odour stimulation, and to log VR state and 2-photon frame.
Documentation on the interface circuit can be found [here](Interface_circuit_for_teensy_4_0).  
Inputs are the 2-photon Frame Clock (to be able to link VR state and 2-photon frame), a digital indicator for whether a 2-photon acquisition is running (in our case linked to the laser shutter) and the commands to the 8 digital and 1 analog stimulation pins via serial communication.  

For the odour delivery, the 3.3V Teensy output was bumped to 5V with a 74ACT541 to control the valve controller. Pull-down resistors were used before the VR Timing Teensy and after the 74ACT541to prevent channels from floating causing rapid switching between ON/OFF states. Circuit drawings can be found [here](Interface_circuit_for_teensy_4_0).   
An Automate Scientific ValveLink8.2/ 8.3 controller and valve system and odour manifold were used to deliver the odour compounds. [LINK](https://www.autom8.com/shop/perfusion-equipment/perfusion-accessories/micro-manifold-8-into-1-with-flow-control-ptfe-inert/)  

The adult zebrafish were mounted with a headbar in a 4 sided tank. The VR was projected on the front and sides of the tank with three VOPLLS N3 projectors.  



## References
Inspiration for parts of this code has been drawn from among others:  
-Štih V, Petrucco L, Kist AM, Portugues R (2019) Stytra: An open-source, integrated system for stimulation, tracking and closed-loop behavioral experiments. PLOS Computational Biology. DOI: 10.1371/journal.pcbi.1006699  
-Huang KH, Rupprecht P, Frank T, Kawakami K, Bouwmeester T, Friedrich RW (2020) A virtual reality system to analyze neural activity and behavior in adult zebrafish. Nature Methods. DOI: 10.1038/s41592-020-0759-2  
-Desai NS, Gray R and Johnston D (2017) A Dynamic Clamp on Every Rig DOI: http://dx.doi.org/10.1523/ENEURO.0250-17.2017   

## Authors
Alex Javier, Sriram Narayanan, Lukas Anneser, Jaap van Krugten, Rainer Friedrich
