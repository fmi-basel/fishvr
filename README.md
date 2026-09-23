# Virtual reality software for headfixed (zebra) fish 

This software package is linked to the publication 'supercoolfish VR behavior' [LINK].  
If you use use this code for your publication, please cite us.

### Overview
This software package was designed to allow the user to configure and run a virtual reality (VR) experiment intended for headfixed zebrafish (*Danio rerio*). A virtual environment is designed in blender. With this software, an experiment is then configured. Repetitions, conditions and triggers can be implemented here. Inputs are the position updates from the tail-tracking script via [XXX], the Blendr VR model and the experiment configuration of the XXX. Outputs are the updated VR over the projectors stimuli triggers and log file.


[image with all connections of the setup?]

## System requirements
PC
python

## Installation instructions
Use the environment.yml file to set up your pc for proper installation and download the necessary packages

## User manual
For a detailed description of all the setting options, click here. For documention on some user editable functions, see LINK


## Hardware
A Teensy 4.0 microcontroller was used for the timing and trigger control.  
The adult zebrafish were mounted with a headbar in a 4 sided tank. The VR was projected on the front and sides of the tank with three VOPLLS N3 projectors.  
For the odour delivery, the 3.3V Teensy output was bumped to 5V with a 74ACT541. Pull-down resistors were used before the VR Timing Teensy and after the 74ACT541to prevent channels from floating causing rapid switching between ON/OFF states. Cirquit drawings can be found [here](Interface_circuit_for_teensy_4_0).   
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
