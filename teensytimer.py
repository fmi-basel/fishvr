import serial
import serial.tools.list_ports
import struct
import time

class TeensyTimer():

    def __init__(self, port):

        self.trig_2p_start = 0.
        self.trig_2p_end = 0.
        self.trig_stim = [False] * 8 # 8 boolean values for stimulation trigger
        self.trig_mode_pulsed = [False] * 8 # 0 or 1 to indicate continuous or pulsed stimulation mode
        self.trig_stim_float = self.bools_to_float(self.trig_stim)
        self.trig_mode_pulsed_float = self.bools_to_float(self.trig_mode_pulsed) # it is assumed that the stimulation mode for a given output channel is not changed within a trial.
        self.stim_duration = 0.5 # in seconds, duration of the stimulation pulse
        self.stim_intensity = 0.
        self.frameclock = 0.

        self.port = port
        self.receive_timeout = .004 #empirically determined to balance speed and reliability

        #Proof reading and correction is done only for pulsed triggers
        #Stimulation triggers span much longer durations in time and do not have adverse consequences when sync events fail rarely
        self.trigger_execution_flag = False
        self.cached_triggers = []


    def bools_to_float(self, bools):
        """
        Converts a list of 8 boolean values to a float, where each boolean 
        represents one of the 8 least significant bits (LSBs) of the float's integer part.
        
        Example:
            [False, False, False, False, False, False, False, True] -> 1.0
            [True, False, False, False, False, False, False, False] -> 128.0
            [True, False, True, False, True, False, True, False]    -> 170.0
        """
        if len(bools) != 8:
            raise ValueError("Input must be a list of 8 boolean values.")
        
        # Convert list of booleans to an integer using bit shifting
        value = sum((int(b) << (7 - i)) for i, b in enumerate(bools))
        
        return float(value)
    

    def float_to_bools(self, value):
        """
        Converts a float whose integer part represents 8 bits into a list of 8 boolean values.
        The output is ordered from MSB to LSB.

        Parameters:
            value (float): Float value where the integer part is between 0 and 255.

        Returns:
            list of bool: 8 boolean values representing the 8 LSBs of the integer.

        Example:
            170.0 -> [True, False, True, False, True, False, True, False]
            128.0 -> [True, False, False, False, False, False, False, False]
            1.0   -> [False, False, False, False, False, False, False, True]
        """
        int_value = int(value)

        if not (0 <= int_value <= 255):
            raise ValueError("Float's integer part must be between 0 and 255.")

        return [(int_value & (1 << (7 - i))) != 0 for i in range(8)]


    def trigger_pulses_to_excecute(self):
        return self.trig_2p_start + self.trig_2p_end + sum(self.trig_mode_pulsed)
    

    def list_ports(self):
        ports = [x.device for x in serial.tools.list_ports.comports()]        
        ports = '\n'.join(ports)
        print("Ports Available:\n" + ports)


    def open(self):
        try:
            self.teensy = serial.Serial(self.port, 460800, timeout=0.001) 
            self.teensy.flush()
            print("Connected to Teensy on {}".format(self.port))

        except:
            print("Unable to connect to Teensy")
            ports_available = self.list_ports()
            print("Port requested: " + self.port) 

    
    def sync(self):

        self.trig_mode_pulsed_float = self.bools_to_float(self.trig_mode_pulsed)
        self.trig_stim_float = self.bools_to_float(self.trig_stim)

        value = [self.trig_2p_start, self.trig_2p_end, self.trig_mode_pulsed_float, self.stim_duration, self.trig_stim_float, self.stim_intensity]

        if self.trigger_execution_flag:
            value[0] = max(value[0], self.cached_triggers[0])
            value[1] = max(value[1], self.cached_triggers[1])
            stimtrigs_from_cache = self.float_to_bools(self.cached_triggers[2])
            value[4] = self.bools_to_float([bool(x+y) for x, y in zip(self.trig_stim, stimtrigs_from_cache)])

        data_sent = True
        triggers_in_queue = self.trigger_pulses_to_excecute()

        for i in range(len(value)):
            byte_array = struct.pack("f", value[i])
            try:
                self.teensy.write(byte_array)
            except:
                data_sent = False
                print("Device Unresponsive")
                return
        
        if data_sent:

            received = None
            s = time.time()
            
            while received is None:     
                try:
                    received = float(self.teensy.readline())
                    if self.trigger_execution_flag:
                        print("Cached trigger(s) from previous frame have been executed")
                        self.trigger_execution_flag = False
                except: pass

                if (time.time() - s) > self.receive_timeout and received is None:
                    print("Timed Out, No data received")
                    if triggers_in_queue > 0:
                        self.cached_triggers = [self.trig_2p_start, self.trig_2p_end, self.trig_stim_float]
                        self.trigger_execution_flag = True
                        print("Failed to execute trigger(s), will attempt again next frame")
                    break
            
            self.frameclock = received
            self.teensy.flush()

    def close(self):
        self.teensy.close()
        print("Communication with Teensy closed on {}".format(self.port))


if __name__ == "__main__":
    t = TeensyTimer("COM4")
    t.open()
    t.sync()    
    t.close()