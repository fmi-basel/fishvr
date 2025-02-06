"""
TODO:
1) DOCUMENTATION
2) Implement screen splitting based on tank geometry to allow different configurations
3) Known limitations:
    a) Only one stimulus trigger can be configured per trial
    b) Stimulation zones can only be defined as circles of a specified radius 

DONE:
1) Save trial info ------ json format, add fields as necessary
2) Separate trial index and trial iteration. 
    Potential bug in counting. Could not reproduce. Fixed by blocking trial index update during intertrials? That was likely it. Hasn't happened since then
    a) move to next index only if a certain percentage of current trial has been completed
    b) wait for keyboard input to initiate experiment and move forward from the first trial
    c) Optional manual input to move ahead from current trial
3) Print trial info during experiment ------ add info as needed
4) Forcibly end 2P acquisition while exiting VR
5) Save data ------ save VR data as one long continuous block which can be chunked later. Data saved as csv
6) Make it optional to trigger 2P acquisition
7) Modes of triggering 2P : once every trial or once every experiment
8) Resize screens and aspect ratio to match VR projectors
9) Fix trial start bug where teleportation occurs the next frame after fade ------ fixed by updating x, y and heading when new scene is loaded 
10) Add 'location' trigger for pulsed stimulation in addition to 'time', 'crossing' and 'zone' modes
11) Load parameters from config file
    a) Initialize and setup panda3D in code and not from file
    b) load experiment specific parameters from file
    c) save a copy of loaded parameters in the trial info file
    d) Take a call on how to do 
        i) repetitions of trials
        ii) deal with trial index exceeding trial count in param file
12) Implement TV cards to show landmarks/movies
    ------ Current method for mirroring landmarks may have unknown issues but works in a limited context
13) Implement collision handling
    ------ Collision checks with complex visible geometries slows down frame rate
14) Implement UDP communication with tail tracking code 
        a) Clear out all data in the buffer when reading ------ Done
        b) dtheta and dvelocity will be zero when no values are received from the tail tracking code.
           This will result in jerky update to position and heading but should ideally not occur when
           panda3D framerate is lower than the tail tracking frame rate. 
           udp sync status is saved in csv to a) keep log and align VR with high speed video
                                              b) assess performance and find processing bottlenecks
                                              c) find a working set of parameters (frame rates and timeouts for serial and udp communication)
15) Handle overwriting of data (easy fix but must be done)
    ------ User input requested to overwrite and proceed or abort
16) Optimize tracking parameters for speed. A workable set of parameters has been found. 
    Parameters on laptop:
                         a) VR fps: 60Hz
                         b) Tail tracking tested with video file. 100-150 fps should work, test with camera
                         c) Teensy sync timeout of 0.004 seconds
                         b) UDP timeout of 0.001 seconds and UDP buffer size of 64 bytes
17) Implement ptic flow stimulus delivery and trialwise gloabal gain setting
"""

from pathlib import Path
import sys
import socket
import struct
import builtins
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.LerpInterval import LerpColorScaleInterval
from panda3d.core import AmbientLight, DirectionalLight, Vec4, ClockObject, loadPrcFileData
from panda3d.core import CardMaker, TextureStage
from panda3d.core import CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32
import teensytimer
import numpy as np
import json
import csv
from datetime import datetime

######################
# Initialize panda3D #
######################

framerate = 60      # Will apply only when syncvideo is False
syncvideo = False   # Decouple spinCameraTask from monitor refresh (False sets user specified fps, True clamps to monitor refresh)
use_timer = False   # Use teensy timer for synchronization
saveas = "log/date_fishX_sessionY"  # Save data to this directory with the given prefix (replace 'date' with date, X and Y with fish and session numbers)

projection_width = 1040 # combined width of screen across 3 projectors
projection_height = 260 # height of screen

window_origin_x = 400   # panda3D window position
window_origin_y = 100

globalClock = ClockObject.getGlobalClock()
globalClock.setMode(ClockObject.MLimited)
globalClock.setFrameRate(framerate) 

loadPrcFileData('', 'win-size {} {}'.format(projection_width, projection_height))
loadPrcFileData('', 'win-origin {} {}'.format(window_origin_x, window_origin_y))
loadPrcFileData('', 'sync-video {}'.format(syncvideo))
loadPrcFileData('', 'threading-model Cull/Draw')

######################
#        END         #
######################


class ZebrafishVirtualReality(ShowBase):

    def __init__(self, configfile="exp_configs/defaultconfig.json", save=True, saveas=saveas,
                 use_timer=use_timer, serial_port="COM4", serial_timeout=0.004,
                 udp_ip="127.0.0.1", udp_port=5005, udp_buffer_size=64, udp_timeout=0.001):

        ShowBase.__init__(self)

        self.configfile = configfile
        self.save = saveas
        self.saveas = saveas

        if save:

            jsonfile = self.saveas + "_vrinfo.json"
            logfile = self.saveas + "_vrlog.csv"

            while True:
                if Path(logfile).is_file() or Path(jsonfile).is_file():
                    user_input = input("Filename exists. Enter y/n to overwrite data or quit: ")
                else:
                    break

                if user_input.lower() == 'y':
                    print("Input received, overwriting data")
                    break
                elif user_input.lower() == 'n':
                    print("Input received, aborting experiment")
                    sys.exit()
                else:
                    print("Invalid input, enter y to overwrite or n to abort")
            
            
            date_and_time = datetime.now().strftime("%y%m%d_%H:%M:%S")

            self.infofile = open(jsonfile, 'w', encoding='utf-8')
            self.infofile.write("{\"timestamp\": \"%s\",\n" % date_and_time)
            self.infofile.write("\"trials\":[\n")

            self.datafile = open(logfile, 'w', encoding='utf-8',  newline='')
            self.logger = csv.writer(self.datafile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            self.logger.writerow(['trial', 'trial index', '2p framecount', 'timestamp',
                                   'xpos', 'ypos', 'heading', '2p state', 'optic flow state', 
                                   'optic flow direction', 'optic flow velocity', 'stim state',
                                   'stim state pulsed', 'tail tracking framecount', 'vr gain'])

        self.trial = 0
        self.repcount = 0
        self.trial_index = 0
        self.force_progress = False

        self.loadConfig()

        self.frame_onset_time = 0.
        self.frame_dt = 0.
        self.XPos = 0.
        self.YPos = 0.
        self.ZPos = 0.
        self.heading = 0.
        self.prevX = 0.
        self.prevY = 0.
        self.trial_displacement = 0.

        self.use_timer = use_timer
        self.serial_port = serial_port

        if self.use_timer:
            self.teensy = teensytimer.TeensyTimer(self.serial_port)
            self.teensy.receive_timeout = serial_timeout
            self.teensy.open()

        self.state = "intertrial" # "trial" or "intertrial"
        self.state_onset_time = 0.
        self.initialized = False
        self.start_trial = False
        self.start_2p = False
        self.end_2p = False
        self.optic_flow_state = False
        self.stim_state = False
        self.stim_state_pulsed = False
        self.framecount_2p = 0.
        self.twopstate = False
        self.end_vr = False

        #Fade in and out while teleporting
        self.fade_timer = 0.
        self.fade_out = False
        self.fade_in = False

        #Landmarks
        self.landmark_nodes = [] #container to hold all landmark nodes
        self.landmark_nodes_mirrored = [] #container to hold mirrored copies of landmarks on the other side of a corridor
        self.textures = []

        #UDP port and socket for communicating with tail tracking code
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.udp_buffer_size = udp_buffer_size
        self.udp_timeout = udp_timeout #setting this parameter to 0 is equivalent to non-blocking mode
        self.tail_tracking_framecount = 0

        #Variables from tail tracking code
        self.velocity = 0.
        self.theta = 0.

        """
        ######################
        Definition of movement 
        ######################
        """
        builtins.base.disableMouse()
        builtins.base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        
        # -*- starting position
        builtins.base.camera.setPos(*self.init_position)

        self.taskMgr.add(self.spinCameraTask, 'SpinCameraTask')

        if self.use_keyboard:
            self.keyMap = {
            'forward': 0, 'backward': 0, 'right': 0, 'left': 0}
            self.accept('arrow_up', self.setKey, ['forward', True])
            self.accept('arrow_down', self.setKey, ['backward', True])
            self.accept('arrow_right', self.setKey, ['right', True])
            self.accept('arrow_left', self.setKey, ['left', True])
            # Detect when keys are released:
            self.accept("arrow_up-up", self.setKey, ["forward", False])
            self.accept('arrow_down-up', self.setKey, ['backward', False])
            self.accept("arrow_right-up", self.setKey, ["right", False])
            self.accept("arrow_left-up", self.setKey, ["left", False])
        else:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
            self.udp_socket.bind((self.udp_ip, self.udp_port))
            # self.udp_socket.setblocking(0) # using settimeout(0.0) is equivalent to setblocking(0) 
            self.udp_socket.settimeout(self.udp_timeout)


        # self.accept('w', self.updateTrialIndexWithKey)
        self.accept('keystroke', self.updateTrialIndexWithKey)
        self.accept('escape', self.exitVR)


        """
        ###############################
        Parameters for Screen-Splitting 
        ###############################
        """
        builtins.base.camLens.setFov(40)  # originally 40
        builtins.base.camLens.setNear(0.001)  # originally 0.1
        builtins.base.camLens.setFar(1000)
        builtins.base.setAspectRatio(1.33)
        builtins.base.camNode.setActive(0)
        builtins.base.makeCamera(builtins.base.win, displayRegion=(0.33, 0.66, 0, 1),
                                lens=builtins.base.camLens)
        builtins.base.makeCamera(builtins.base.win, displayRegion=(0, 0.33, 0, 1),
                                lens=builtins.base.camLens)
        builtins.base.makeCamera(builtins.base.win, displayRegion=(0.66, 0.99, 0, 1),
                                lens=builtins.base.camLens)

        builtins.base.camList[1].setH(0)
        builtins.base.camList[2].setH(40)
        builtins.base.camList[3].setH(-40)

        self.camlist = builtins.base.camList

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(0, 0, -90)
        self.render.setLight(self.mainLightNodePath)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.6, 0.6, 0.6, 1))  # 0.8, 0.8, 0.8, 1
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)
        self.render.setShaderAuto()

        self.setupScene()


    def loadConfig(self):
        with open(self.configfile, 'r') as f:
            self.expconfig = json.load(f)        
        f.close()

        self.ntrials = len(self.expconfig['trials'])
        self.setParamsForCurrentTrial()


    def setParamsForCurrentTrial(self):

        self.trialconfig = self.expconfig['trials'][self.trial_index]

        self.trial_id                   = self.trialconfig['trial_id']
        self.repeats                    = self.trialconfig['repeats']
        self.use_keyboard               = self.trialconfig['use_keyboard']
        self.keyboard_gain              = self.trialconfig['keyboard_gain']
        self.keyboard_heading_increment = self.trialconfig['keyboard_heading_increment']
        self.vr_gain                  = self.trialconfig['vr_gain']
        self.enable2d                   = self.trialconfig['enable2d']
        self.displacement_restart       = self.trialconfig['displacement_restart']
        self.displacement_trial_start   = self.trialconfig['displacement_trial_start']
        self.model                      = self.trialconfig['model']
        self.init_position              = self.trialconfig['init_position']
        self.init_hpr                   = self.trialconfig['init_hpr']
        self.scale                      = self.trialconfig['scale']
        self.intertrial_duration        = self.trialconfig['intertrial_duration']
        self.max_trial_duration         = self.trialconfig['max_trial_duration']

        #imaging triggers
        self.do2p               = self.trialconfig['do2p']
        self.continuous2p       = self.trialconfig['continuous2p']

        #Fade in and out while teleporting
        self.fade_duration      = self.trialconfig['fade_duration']

        #Stimulation triggers
        self.stimulation        = self.trialconfig['stimulation']
        self.stimulation_mode   = self.trialconfig['stimulation_mode']
        self.stim_intensitiy    = self.trialconfig['stim_intensity']
        self.stim_coord         = self.trialconfig['stim_coord']
        self.crossing_direction = self.trialconfig['crossing_direction']
        self.stim_radius        = self.trialconfig['stim_radius']
        self.stim_onset_time    = self.trialconfig['stim_onset_time']
        self.stim_duration      = self.trialconfig['stim_duration']

        #Optic flow
        self.optic_flow                 = self.trialconfig['optic_flow']
        self.optic_flow_reference_frame = self.trialconfig['optic_flow_reference_frame']
        self.optic_flow_direction       = self.trialconfig['optic_flow_direction']
        self.optic_flow_velocity        = self.trialconfig['optic_flow_velocity']
        self.optic_flow_mode            = self.trialconfig['optic_flow_mode']
        self.optic_flow_coord           = self.trialconfig['optic_flow_coord']
        self.optic_flow_radius          = self.trialconfig['optic_flow_radius']

        #Cue cards for showing landmarks and displaying video
        self.show_landmarks     = self.trialconfig['show_landmarks']
        self.mirror_landmarks   = self.trialconfig['mirror_landmarks']
        self.mirror_distance    = self.trialconfig['mirror_distance']
        self.landmark_number    = self.trialconfig['landmark_number']
        self.landmark_position  = self.trialconfig['landmark_position']
        self.landmark_hpr       = self.trialconfig['landmark_hpr']
        self.landmarks          = self.trialconfig['landmarks']
        self.landmark_flag      = self.trialconfig['landmark_flag']

        #Collision handling
        self.handle_collisions  = self.trialconfig['handle_collisions']
        self.collision_radius   = self.trialconfig['collision_radius']
        self.collider_flag      = self.trialconfig['collider_flag']  
        self.hide_collider      = self.trialconfig['hide_collider']


    def setupScene(self):
    
        if self.trial > 0:
            self.scene.removeNode()

        # Load the environment model.
        self.scene = self.loader.loadModel(self.model)
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(*self.scale)
        self.scene.setTwoSided(True)  # rendering related. mostly has no consequence

        self.drawLandmarks() # this function can be called dynamically to toggle landmark visibility using flags    

        # self.scene.setPos(*self.init_position)  
        builtins.base.camera.setPos(*self.init_position)
        builtins.base.camera.setHpr(*self.init_hpr)
        self.YPos = builtins.base.camera.getY()
        self.XPos = builtins.base.camera.getX()
        self.heading = builtins.base.camera.getH()

        # set up collision handling
        if self.trial == 0:
            self.initializeColliderObject()

        self.updateCollisionPushers()

        self.formatTrialInfo()

        if self.save:
            if self.trial > 0:
                self.infofile.write(',\n')
            json.dump(self.trialinfo, self.infofile, ensure_ascii=False)
            self.infofile.flush()


    def getNodes(self):
        try:
            self.nodes = dict([(x.getName(), list(x.getPos())) for x in self.scene.getChildren()])
        except:
            self.nodes = []
    

    def formatTrialInfo(self):
        self.getNodes()
        self.trialinfo = {"trial_number" : self.trial, "trial_index" : self.trial_index,
                          "repeat" : self.repcount, "trial_config" : self.trialconfig,
                          "nodes" : self.nodes}
        

    def drawLandmarks(self):
        #Landmarks can be redrawn dynamically in spinCameraTask by setting flags accordingly
        #This can be used to introduce closed-loop contigencies for implementing learning assays
        #Hint: 1) use a function to check what to do with landmarks in each loop of spinCameraTask
        #      2) redraw landmarks when they need to be changed
        cm = CardMaker('card')
        self.landmark_nodes = []
        self.landmark_nodes_mirrored = []
        self.textures = []
        for i in range(self.landmark_number):
            
            tex, lm, lm2 = self.initializeLandmarkNode(cm, self.landmarks[i], self.landmark_flag[i], self.landmark_position[i], 
                                                       self.landmark_hpr[i], self.mirror_landmarks[i], self.mirror_distance[i])

            self.textures.append(tex)
            self.landmark_nodes.append(lm)
            self.landmark_nodes_mirrored.append(lm2)


    def initializeLandmarkNode(self, cardmaker, texture_file, flag, position, hpr, mirror=False, mirror_distance=0):
        lmtex =  self.loader.loadTexture(texture_file)
        lmnode = None
        lmnode2 = None
        if flag:
            lmnode = self.render.attachNewNode(cardmaker.generate())
            lmnode = self.centerPivot(lmnode)
            lmnode.setDepthTest(1)
            lmnode.setDepthWrite(1)
            lmnode.setColor(Vec4(1, 1, 1, 1))
            lmnode.setPos(tuple(position))
            lmnode.setHpr(tuple(hpr))
            lmnode.setScale(1, 1, 1)
            lmnode.setTexture(lmtex, 1)

            if mirror:
                pos_mirror = [x+y for x,y in zip(position,[mirror_distance,0,0])]
                h_mirror = [-hpr[0],hpr[1],hpr[2]]

                lmnode2 = self.render.attachNewNode(cardmaker.generate())
                lmnode2 = self.centerPivot(lmnode2)
                lmnode2.setDepthTest(1)
                lmnode2.setDepthWrite(1)
                lmnode2.setColor(Vec4(1, 1, 1, 1))
                lmnode2.setPos(tuple(pos_mirror))
                lmnode2.setHpr(tuple(h_mirror))
                lmnode2.setScale(1, 1, 1)
                lmnode2.setTexScale(TextureStage.getDefault(),-1,1)
                lmnode2.setTexture(lmtex, 1)

            if texture_file.split('.')[-1] in ['avi','mov','mp4']:
                lmtex.play()

        return lmtex, lmnode, lmnode2
    

    def centerPivot(self, cardnode):
        """https://discourse.panda3d.org/t/again-rotation-question/2004/8"""
        pivot=cardnode.getBounds().getCenter()
        parent=cardnode.getParent()
        # create the new parent node under the original parent
        newnode=parent.attachNewNode('theName')
        # bring the new parent to the center
        newnode.setPos(pivot)
        # and relocate the node without changing any of it's transformation
        cardnode.wrtReparentTo(newnode)
        return newnode
    

    def initializeColliderObject(self):

        self.cTrav = CollisionTraverser()

        self.collider_node = CollisionNode("fish")

        self.collider_node.addSolid(CollisionSphere(self.XPos, self.YPos, self.init_position[2], self.collision_radius))
        self.collider_node.setCollideMask(BitMask32.bit(0))
        self.collider_object = builtins.base.camera.attachNewNode(self.collider_node)

        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.collider_object, builtins.base.camera)


    def updateCollisionPushers(self):
        
        self.cTrav.clearColliders()

        if self.handle_collisions:

            self.collider_node_list = []
            hide = []
            for i in range(len(self.collider_flag)):
                p = self.collider_flag[i]
                matches = list(self.scene.findAllMatches('**/*{}*;+h'.format(p)))
                self.collider_node_list += matches
                hide += [self.hide_collider[i]]*len(matches)

            [x.setCollideMask(BitMask32.bit(0)) for x in self.collider_node_list]       

            self.cTrav.addCollider(self.collider_object, self.pusher)

            [self.collider_node_list[x].hide() for x in range(len(self.collider_node_list)) if hide[x]]


    def setKey(self, key, value):
        self.keyMap[key] = value

    
    def updateTrialIndexWithKey(self, keyname):
        
        if self.state == 'trial':

            if keyname == 'w':
                self.force_progress = True
                print("Will progress to next trial regardless of outcome")
            if keyname == 's':
                self.force_progress = False
                print("Will progress only if trial completed")


    def updateCameraWithKeyboard(self):

        if self.keyMap["forward"]:
            builtins.base.camera.setY(builtins.base.camera, self.keyboard_gain * self.frame_dt)

        elif self.keyMap["backward"]:
            builtins.base.camera.setY(builtins.base.camera, -self.keyboard_gain * self.frame_dt)

        if self.keyMap["right"]:
            builtins.base.camera.setH(builtins.base.camera, -self.keyboard_heading_increment * self.frame_dt)

        elif self.keyMap["left"]:
            builtins.base.camera.setH(builtins.base.camera, self.keyboard_heading_increment * self.frame_dt)

        if self.optic_flow_state == True:

            if self.optic_flow_reference_frame == 'allocentric':
                current_h = builtins.base.camera.getH() # get current heading
                builtins.base.camera.setH(self.optic_flow_direction) # set heading to the desired optic flow direction
                builtins.base.camera.setY(builtins.base.camera, self.optic_flow_velocity * self.frame_dt)
                builtins.base.camera.setH(current_h) # reset heading to fish heading

            if self.optic_flow_reference_frame == 'egocentric':
                builtins.base.camera.setY(builtins.base.camera, self.optic_flow_velocity * self.frame_dt)


    def updateCameraWithTailTracking(self):
        data, addr = None, None

        # Read all data in the buffer and clear it out. Most recent values will be used for updating VR
        # Number of packets stuck in the buffer can be minimized by setting a broadcast rate close to the framerate of panda3D
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(self.udp_buffer_size) # buffer size is 24 bytes
            except:
                break
        
        if data is not None:
            self.velocity, self.theta, self.tail_tracking_framecount = struct.unpack('>ddi', data)
        else:
            self.velocity, self.theta = 0, 0

        builtins.base.camera.setY(builtins.base.camera, self.velocity * self.frame_dt * self.vr_gain)
        if self.enable2d:
            builtins.base.camera.setH(builtins.base.camera, self.theta * self.frame_dt * self.vr_gain)

        if self.optic_flow_state == True:

            if self.optic_flow_reference_frame == 'allocentric':
                current_h = builtins.base.camera.getH() # get current heading
                builtins.base.camera.setH(self.optic_flow_direction) # set heading to the desired optic flow direction
                builtins.base.camera.setY(builtins.base.camera, self.optic_flow_velocity * self.frame_dt * self.vr_gain)
                builtins.base.camera.setH(current_h) # reset heading to fish heading
                
            if self.optic_flow_reference_frame == 'egocentric':    
                builtins.base.camera.setY(builtins.base.camera, self.optic_flow_velocity * self.frame_dt * self.vr_gain)


    def setOpticFlowState(self):

        if self.state == "trial":

            if self.optic_flow == True:

                if self.optic_flow_mode == "trial" and self.optic_flow_state == False:
                        self.optic_flow_state = True

                if self.optic_flow_mode == "zone":
                    distance = np.linalg.norm(np.array([self.XPos,self.YPos]) - np.array(self.optic_flow_coord))
                    if distance <= self.optic_flow_radius:
                        self.optic_flow_state = True
                    else:
                        self.optic_flow_state = False
        else:
            self.optic_flow_state = False


    def setTrigState(self):

        if self.stimulation:

            if self.state == "trial":

                if self.stimulation_mode == "location":
                    prev_distance = np.linalg.norm(np.array([self.prevX,self.prevY]) - np.array(self.stim_coord)) #euclidean distance between points
                    distance = np.linalg.norm(np.array([self.XPos,self.YPos]) - np.array(self.stim_coord))
                    if prev_distance > self.stim_radius and distance >= self.stim_radius:
                        self.stim_state_pulsed == True
                    else:
                        self.stim_state_pulsed == False
                
                if self.stimulation_mode == "crossing":
                    if self.crossing_direction == "x":
                        if self.prevX <= self.stim_coord[0] and self.XPos >= self.stim_coord[0]:
                            self.stim_state_pulsed = True
                        else:
                            self.stim_state_pulsed = False

                    if self.crossing_direction == "y":
                        if self.prevY <= self.stim_coord[1] and self.YPos >= self.stim_coord[1]:
                            self.stim_state_pulsed = True
                        else:
                            self.stim_state_pulsed = False

                elif self.stimulation_mode == "zone":
                    distance = np.linalg.norm(np.array([self.XPos,self.YPos]) - np.array(self.stim_coord))
                    if distance <= self.stim_radius:
                        self.stim_state = True
                    else:
                        self.stim_state = False

                elif self.stimulation_mode == "time":
                    if (self.frame_onset_time - self.state_onset_time >= self.stim_onset_time and 
                        self.frame_onset_time - self.stim_onset_time - self.state_onset_time <= self.stim_duration):
                        self.stim_state = True
                    else:
                        self.stim_state = False

            else:
                self.stim_state = False
                self.stim_state_pulsed = False

        else:
            self.stim_state = False
            self.stim_state_pulsed = False

        if self.use_timer:
            self.teensy.stim_duration = self.stim_duration
            self.teensy.stim_intensity = self.stim_intensitiy
            self.teensy.trig_stim = self.stim_state
            self.teensy.trig_stim_pulsed = self.stim_state_pulsed
            self.teensy.trig_2p_start = self.start_2p
            self.teensy.trig_2p_end = self.end_2p
            if self.stimulation_mode == "crossing" or self.stimulation_mode == "location":
                self.teensy.stim_mode = 1
            else:
                self.teensy.stim_mode = 0

        if self.start_2p:
            self.twopstate = True
        if self.end_2p:
            self.twopstate = False

        self.start_2p = False
        self.end_2p = False


    def syncTimer(self):
        if self.use_timer:
            if not self.end_vr:
                self.teensy.sync()
            else:
                self.teensy.trig_2p_start = False
                self.teensy.trig_2p_end = True
                self.teensy.trig_stim = False
                self.teensy.trig_stim_pulsed = False
                self.teensy.sync()

            self.framecount_2p = self.teensy.frameclock

    
    def logData(self):

        """
        Write data in the same order as row headers (see above)
        """
        if self.save:
            self.logger.writerow([self.trial, self.trial_index, self.framecount_2p, self.frame_onset_time,
                                  self.XPos, self.YPos, self.heading, self.twopstate, self.optic_flow_state, 
                                  self.optic_flow_direction, self.optic_flow_velocity, self.stim_state,
                                  self.stim_state_pulsed, self.tail_tracking_framecount, self.vr_gain])
            

    def printTrialInfo(self):
        if self.trial_index == 0:
            print("Starting trial: {}, index: {}, id: {}, repeat: until user presses w".format(self.trial, self.trial_index, self.trial_id))
        else:
            print("Starting trial: {}, index: {}, id: {}, repeat: {} of {}".format(self.trial, self.trial_index, self.trial_id, self.repcount, self.repeats-1))


    def updateTrialParams(self):

        self.trial += 1

        if self.trial_index == 0:
            if self.force_progress == True:
                self.force_progress = False
                self.trial_index += 1
        else:
            if self.trial_displacement >= self.displacement_restart or self.force_progress:
                self.force_progress = False                
                self.repcount += 1

                if self.repcount == self.repeats:
                    self.repcount = 0
                    self.trial_index += 1

        if self.trial_index == self.ntrials:
            print("All trials executed. Ending experiment...")
            self.exitVR()
        else:
            self.setParamsForCurrentTrial()


    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        
        self.frame_onset_time = globalClock.getFrameTime()
        self.frame_dt = builtins.globalClock.getDt()

        if self.use_keyboard:
            self.updateCameraWithKeyboard()
        else:
            self.updateCameraWithTailTracking()

        self.YPos = builtins.base.camera.getY()
        self.XPos = builtins.base.camera.getX()
        self.ZPos = builtins.base.camera.getZ()
        self.heading = builtins.base.camera.getH()
        self.trial_displacement = np.linalg.norm(np.array([self.XPos,self.YPos]) - np.array(self.init_position[0:1]))

        if self.initialized == False:
            self.initialized = True
            self.state_onset_time = self.frame_onset_time
            self.state = "trial"
            # Use first trial to find FOV, acquire reference stack and set up motion correction
            # No triggered 2P acquisition needed in this phase. 
            # Remember to toggle self.do2p to turn off imaging trigger. 
            # Uncomment the block below for consistency in case imaging is needed for the very first trial
            # if self.do2p:
            #     self.start_2p = True
            self.printTrialInfo()

        if self.state == "trial":
            if (self.frame_onset_time - self.state_onset_time >= self.max_trial_duration or 
                self.trial_displacement >= self.displacement_restart):

                self.updateTrialParams()

                self.printTrialInfo()

                self.state = "intertrial"
                self.state_onset_time = self.frame_onset_time
                if self.do2p and not self.continuous2p:
                    self.end_2p = True
                self.fade_out = False
                self.fade_in = False

        if self.state == "intertrial":
            
            if self.fade_out == False:
                LerpColorScaleInterval(self.render, self.fade_duration, (0, 0, 0, 1.0)).start()
                self.fade_timer = self.frame_onset_time
                self.fade_out = True

            if self.frame_onset_time - self.fade_timer >= self.fade_duration and self.fade_in == False:
                self.setupScene()
                LerpColorScaleInterval(self.render, self.fade_duration, (1, 1, 1, 1.0)).start()
                self.fade_in = True  

            if (self.frame_onset_time - self.state_onset_time >= self.intertrial_duration or 
                self.trial_displacement >= self.displacement_trial_start and self.fade_in == True):
                self.state = "trial"
                self.state_onset_time = self.frame_onset_time
                if self.do2p:
                    if self.continuous2p and self.twopstate == False:
                        self.start_2p = True
                    else:
                        self.start_2p = True
                    

        self.setOpticFlowState()

        self.setTrigState()

        self.syncTimer()

        self.logData()

        self.prevX = self.XPos
        self.prevY = self.YPos

        #Lock ZPosition in case it changes with collisions
        if self.ZPos != self.init_position[2]:
            builtins.base.camera.setZ(self.init_position[2])

        return Task.cont


    def exitVR(self):
        
        self.end_vr = True

        if self.use_timer:
            self.syncTimer()
            self.teensy.close()

        if self.save:
            self.infofile.write("\n]}")
            self.infofile.close()
            self.datafile.close()

        print('Exiting VR')
        sys.exit()


if __name__ == "__main__":
    vr = ZebrafishVirtualReality()
    vr.run()