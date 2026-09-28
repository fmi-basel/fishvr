"""
**** Run this script to test the latency of the VR system ***

Running this script generates periodic digital output triggers and sharp luminance transitions (black to white screen).

These outputs can be read by feedback inputs to the teensy running the vrtiming.ino script to estimate the time difference
between the action and its consequence. Measurements performed this way are limited by the time resolution of the VR frame rate.

Latencies for the updating 1) the state of the digital trigger outputs and 2) the VR display, are estimated on independent runs
by configuring the hardware as described below:


For digital triggers:
1) Connect One of the digital output pins from the teensy back to the 2-photon frame clock input. 
2) A constant +5V source must be connected to the 2p acquisition state input pin of the teensy interface circuit to log digital input events. 
3) Run this script and save the log file. 
4) The log file will include a frame-by-frame timestamp, the state of the digital output and the measured feedback of
the digital trigger being executed in hardware.
5) The time difference between the onset of the trigger and the rising edge (time of first non-zero value in the log) of the feedback input is the latency.

For VR display update:
1) Position a light sensor, such as an amplified photodiode sensor, to detect the output from the VR display (eg. the projector).
2) Ensure that the light sensor has a sufficiently fast response time (<VR frame rate) and limit its maximum output voltage to +5V.
3) Visualize the output of the sensor on an oscilloscope to ensure that the signal reads close to zero when the screen is dark 
and close to the 5V maximum when the screen displays white.
4) Connect the output of the sensor to the 2-photon frame clock input. 
5) As before, a constant +5V source must be connected to the 2p acquisition state input pin of the teensy interface circuit to log digital input events. 
3) Run this script and save the log file. 
4) The log file will include a frame-by-frame timestamp, the output state (same as above) when the screen turns white, and the measured feedback from the light sensor.
5) The time difference between the onset of the trigger and the rising edge (time of first non-zero value in the log) of the feedback input is the latency.
"""

import sys
import builtins
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight, Vec4, ClockObject, loadPrcFileData
from panda3d.core import CardMaker
import teensytimer
import csv
import configparser
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.update()


######################
# Initialize panda3D #
######################

setupfile = None
if setupfile is None:
    setupfile = filedialog.askopenfilename(initialdir='setup/', title='Select VR setup file', filetypes=[('INI files', '*.ini')])

setup = configparser.ConfigParser()
setup.read(setupfile)

framerate = setup.getint('params', 'framerate')                 # Will apply only when syncvideo is False
syncvideo = setup.getboolean('params', 'syncvideo')             # Decouple spinCameraTask from monitor refresh (False sets user specified fps, True clamps to monitor refresh)
use_timer = setup.getboolean('params', 'use_timer')             # Use teensy timer for synchronization
savepath = setup.get('params', 'savepath')                      # Save data to this directory. Can be changed in file dialog
configpath = setup.get('params', 'configpath')                  # Path to experiment configuration files. Can be changed in file dialog

serial_port = setup.get('params', 'serial_port')                # Serial port for teensy timer
serial_timeout = setup.getfloat('params', 'serial_timeout')     # Time to wait for response from teensy
udp_ip = setup.get('params', 'udp_ip')                          # Address to receive UDP message from tail tracking code
udp_port = setup.getint('params', 'udp_port')                   # UDP port
udp_buffer_size = setup.getint('params', 'udp_buffer_size')     # Buffer size for UDP communication. Set large enough to hold multiple values
udp_timeout = setup.getfloat('params', 'udp_timeout')           # Timeout to listen for a UDP message before proceeding

projection_width = setup.getint('params', 'projection_width')   # combined width of screen across 3 projectors
projection_height = setup.getint('params', 'projection_height') # height of screen
window_origin_x = setup.getint('params', 'window_origin_x')     # panda3D window position
window_origin_y = setup.getint('params', 'window_origin_y')

mainlight_rgba = [float(x) for x in setup.get('params', 'mainlight_rgba').split(',')]
mainlight_hpr = [float(x) for x in setup.get('params', 'mainlight_hpr').split(',')]
ambient_rgba = [float(x) for x in setup.get('params', 'ambient_rgba').split(',')]

ncameras = setup.getint('params', 'ncameras') # number of projectors                   
projector_aspect_ratio = (projection_width/ncameras)/projection_height
projector_fov = setup.getfloat('params', 'projector_fov') # field of view of each projector
projector_hpr = []  # angle, pitch, roll of each projector (measure with angle finder, adjust as needed to fix misalignments)
display_region = [] # display region for each projector in relative coordinates
hpr_keys = ['projector{}_hpr'.format(x) for x in range(ncameras)]
dr_keys = ['display_region{}'.format(x) for x in range(ncameras)]

for i in range(ncameras):

    hpr = setup.get('params', hpr_keys[i]).split(',')
    hpr = [float(x) for x in hpr]
    projector_hpr.append(hpr)

    dr = setup.get('params', dr_keys[i]).split(',')
    dr = [float(x) for x in dr]
    display_region.append(dr)

globalClock = ClockObject.getGlobalClock()
globalClock.setMode(ClockObject.MLimited)
globalClock.setFrameRate(framerate) 

loadPrcFileData('', 'win-size {} {}'.format(projection_width, projection_height))
loadPrcFileData('', 'win-origin {} {}'.format(window_origin_x, window_origin_y))
loadPrcFileData('', 'sync-video {}'.format(syncvideo))
loadPrcFileData('', 'threading-model Cull/Draw')
loadPrcFileData('', "background-color 0 0 0")

######################
#        END         #
######################


class ZebrafishVirtualReality(ShowBase):

    def __init__(self, use_timer=use_timer, serial_port=serial_port, serial_timeout=serial_timeout,
                 ncameras=ncameras, projector_hpr=projector_hpr, projector_fov=projector_fov, 
                 display_region=display_region, mainlight_rgba=mainlight_rgba, mainlight_hpr=mainlight_hpr,
                 ambient_rgba=ambient_rgba):

        self.save = True
        logfile = filedialog.asksaveasfilename(initialfile='_latency_log', title='Save log file as', defaultextension='.csv', filetypes=[('csv files', '*.csv')])
        if len(logfile) == 0:
            print('No log file specified, will continue without saving')
            self.save = False
        else:
            self.datafile = open(logfile, 'w', encoding='utf-8',  newline='')
            self.logger = csv.writer(self.datafile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            self.logger.writerow(['timestamp', 'input trigger count', 'stim state', 'stim mode pulsed'])
        
        ShowBase.__init__(self)

        self.flicker_interval = 60 # frames
        self.nstimchannels = 8
        self.stim_state = [False]*self.nstimchannels
        self.framecounter = 0
        self.framecount_2p = 0
        self.stim_pulse_duration = 0.05
        self.stim_intensitiy = 10
        self.stim_state_8bitcode = 0.
        self.stim_mode_pulsed_8bitcode = 0.

        # Full-screen card
        cm = CardMaker("fullscreen_card")
        cm.set_frame(-1, 1, -1, 1)
        self.fullscreen_card = self.render.attach_new_node(cm.generate())
        self.fullscreen_card.set_color(0, 0, 0, 1)

        self.use_timer = use_timer
        self.serial_port = serial_port

        if self.use_timer:
            self.teensy = teensytimer.TeensyTimer(self.serial_port)
            self.teensy.receive_timeout = serial_timeout
            self.teensy.open()

        self.end_vr = False

        builtins.base.disableMouse()
        builtins.base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        
        # -*- starting position
        builtins.base.camera.setPos(0,0,0)

        self.taskMgr.add(self.spinCameraTask, 'SpinCameraTask')

        self.accept('escape', self.exitVR)

        """
        ################
        Screen-Splitting 
        ################
        """
        builtins.base.camLens.setFov(projector_fov) # originally 40, but tank walls angles indicate projectors are at 60 degrees to each other
        builtins.base.camLens.setNear(0.001)
        builtins.base.camLens.setFar(200)
        builtins.base.setAspectRatio(projector_aspect_ratio)

        builtins.base.camNode.setActive(0)
        
        [builtins.base.makeCamera(builtins.base.win, displayRegion=display_region[i], lens=builtins.base.camLens) for i in range(ncameras)]
        [builtins.base.camList[i+1].setHpr(*projector_hpr[i]) for i in range(ncameras)]

        self.camlist = builtins.base.camList

        mainLight = DirectionalLight("main light")
        mainLight.setColor(Vec4(*mainlight_rgba))
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(*mainlight_hpr)
        self.render.setLight(self.mainLightNodePath)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(*ambient_rgba))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)
        self.render.setShaderAuto()


    def setKey(self, key, value):
        self.keyMap[key] = value


    def updateStimState(self):

        if self.stim_state == 'off':
            self.stim_state = [False]*self.nstimchannels
        elif self.stim_state == 'on':
            self.stim_state = [True]*self.nstimchannels


    def setTrigState(self):

        self.updateStimState()

        if self.use_timer:
            self.teensy.stim_duration = self.stim_pulse_duration
            self.teensy.stim_intensity = self.stim_intensitiy
            self.teensy.trig_stim[0:self.nstimchannels] = self.stim_state
            self.teensy.trig_mode_pulsed[0:self.nstimchannels] = [True]*self.nstimchannels


    def syncTimer(self):
        if self.use_timer:
            if not self.end_vr:
                self.teensy.sync()
                self.framecount_2p = self.teensy.frameclock
            else:
                self.teensy.trig_2p_start = False
                self.teensy.trig_2p_end = True
                self.teensy.trig_stim = [False]*8
                self.teensy.trig_mode_pulsed = [False]*8
                self.teensy.sync()    
            self.stim_state_8bitcode = self.teensy.trig_stim_float
            self.stim_mode_pulsed_8bitcode = self.teensy.trig_mode_pulsed_float

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):

        self.framecounter += 1
        fctoggle = (self.framecounter % self.flicker_interval)

        if fctoggle == 0:
            self.stim_state = [True]*self.nstimchannels
        else:
            self.stim_state = [False]*self.nstimchannels

        if fctoggle < 5:
            self.win.set_clear_color((1, 1, 1, 1))
        else:
            self.win.set_clear_color((0, 0, 0, 1))

        self.frame_onset_time = globalClock.getFrameTime()
        self.frame_dt = builtins.globalClock.getDt()

        self.setTrigState()

        self.syncTimer()

        if self.save:
            ['timestamp', 'input trigger count', 'stim state', 'stim mode pulsed']
            self.logger.writerow([self.frame_onset_time, self.framecount_2p, self.stim_state_8bitcode, self.stim_mode_pulsed_8bitcode])

        return Task.cont


    def exitVR(self):
        
        self.end_vr = True

        if self.save:
            self.datafile.close()

        if self.use_timer:
            self.syncTimer()
            self.teensy.close()

        print('Exiting VR')
        sys.exit()


if __name__ == "__main__":
    vr = ZebrafishVirtualReality()
    vr.run()