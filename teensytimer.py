import serial
import serial.tools.list_ports
import struct
import time

class TeensyTimer():

    def __init__(self, port):

        self.trig_2p_start = 0.
        self.trig_2p_end = 0.
        self.trig_stim_pulsed = 0. # 0 or 1 to initiate fixed duration stumulus pulse
        self.stim_duration = 0.
        self.trig_stim = 0.
        self.stim_mode = 0. # 0 or 1 to indicate continuous or pulsed
        self.stim_intensity = 0.
        self.frameclock = 0.

        self.port = port
        self.receive_timeout = .004 #empirically determined to balance speed and reliability

        #Proof reading and correction is done only for pulsed triggers
        #Stimulation triggers span much longer durations in time and do not have adverse consequences when sync events fail rarely
        self.trigger_execution_flag = False
        self.cached_triggers = []


    def trigger_pulses_to_excecute(self):
        return self.trig_2p_start + self.trig_2p_end + self.trig_stim_pulsed
    

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

        value = [self.trig_2p_start, self.trig_2p_end, self.trig_stim_pulsed, self.stim_duration, self.trig_stim, self.stim_mode, self.stim_intensity]

        if self.trigger_execution_flag:
            value[0] = max(value[0], self.cached_triggers[0])
            value[1] = max(value[1], self.cached_triggers[1])
            value[2] = max(value[2], self.cached_triggers[2])

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
                        self.cached_triggers = [self.trig_2p_start, self.trig_2p_end, self.trig_stim_pulsed]
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