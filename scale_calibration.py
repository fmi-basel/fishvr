"""
Angle of view calculator for scaling VR to match blender units across setups
"""

import numpy as np

"""
1) Set Panda3D scale to a known value, say [1.,1.,1.]
2) Measure the size of a calibration object on the projection screen when it is placed in VR at a known distance from the observer.
   For example, what is the size on screen of a 1m sized object in VR placed 2m from the observer?
3) Enter the values for scale used (step 1) and measurements made (step 2) in the calculation below to get the adjusted scale value to use in Panda3D.
4) Take this scaling into account while determining position and coordinates in the VR environment. 
   For example, stimulation zones and coordinates triggering other events in the VR world should be scaled accordingly from the Blender units.
"""

calibrationscale = 1.           # scale parameter in Panda3d used for calibration step 2 
calobjectsize = 2.0             # size of the calibration object in metres
calobjectvrdistance = 2.5       # distance of observer from the calibration object in metres
d_screen_to_observer = 0.095    # distance of observer from the VR projection screen in metres
calobject_size_on_screen = 0.076 # measured size of calibration object on the VR projection screen in metres

calobject_halfangularsize = np.rad2deg(np.arctan(calobjectsize/(2*calobjectvrdistance)))

calobject_target_size = np.tan(np.deg2rad(calobject_halfangularsize)) * d_screen_to_observer * 2

target_scale = calibrationscale * calobject_target_size / calobject_size_on_screen

print("angle subtended by calibration object = {} degrees".format(np.round(2*calobject_halfangularsize,2)))
print("target size of calibration object on screen = {} metres".format(np.round(calobject_target_size,3)))
print("VR scale = {}" .format(target_scale))


