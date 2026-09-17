# Virtual reality software for headfixed (zebra) fish 

This software package is linked to the publication 'supercoolfish VR behavior' [LINK]

### Overview
This software package was designed to allow the user to configure and run a virtual reality (VR) experiment intended for headfixed zebrafish (*Danio rerio*). A virtual environment is designed in blender. With this software, an experiment is then configured. Repetitions, conditions and triggers can be implemented here. Inputs are the position updates from the tail-tracking script via [XXX], the Blendr VR model and the experiment configuration of the XXX. Outputs are the updated VR over the projectors stimuli triggers and log file.


[image with all connections of the setup?]

## System requirements
PC
python

## Installation instructions
Use the environment.yml file to set up your pc for proper installation and download the necessary packages

## User manual
link to short user manual

docstring thing

## Hardware
A Teensy 4.0 microcontroller was used for the timing and triggers control.  
The adult zebrafish were mounted with a headbar in a 4 sided tank. The VR was projected on the front and sides of the tank with three VOPLLS N3 projectors.  
For the odour delivery, the 3.3V Teensy output was bumped to 5V with a 74ACT541. Pull-down resistors were used before the VR Timing Teensy and after the 74ACT541to prevent channels from floating causing rapid switching between ON/OFF states. Cirquit drawings can be found [here](Interface_circuit_for_teensy_4_0).   
An Automate Scientific ValveLink8.2/ 8.3 controller and valve system and odour manifold were used to deliver the odour compounds. [LINK](https://www.autom8.com/shop/perfusion-equipment/perfusion-accessories/micro-manifold-8-into-1-with-flow-control-ptfe-inert/)


## License
check with FMI

## Authors
Alex Javier, Sriram Narayanan, Jan Eckhardt, Jaap van Krugten, Rainer Friedrich
