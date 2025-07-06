const int trig_2p_start_pin = 2;
const int trig_2p_end_pin = 3;
const int trig_stim_pins[] = {4,6,7,8,9,10,11,12}; // pin 5 is reserved for analog out to remain compatible with previous versions of code and physical connections in interfacing hardware
const int nstimouts = 8;
const int analog_pin = 5;         // analog output for stimulus intensity control
const int fc_in_pin = 16;         // frame clock input pin
const int acq_in_pin = 17;        // acquisition clock input pin (frame clock inputs coming in when acquisition clock is low are ignored)

boolean trig_2p_start = false; 
boolean trig_2p_end = false;

boolean trig_stim[] = {false,false,false,false,false,false,false,false};
boolean stim_mode_pulsed[] = {false,false,false,false,false,false,false,false}; // false: continuous, true: pulsed
float trig_stim_float_from_serial = 0.;        // variable to receive float from VR code. Will be decoded to update trig_stim
float stim_mode_pulsed_float_from_serial = 0.; // variable to receive float from VR code. Will be decoded to update stim_mode_pulsed 
int stim_duration = 0;                         // in milliseconds, common for all stim pulses
int intensity = 0;                             //percentage of maximum, only one analog output channel
int intensity_temp = 0;
volatile boolean fc_in = false;
volatile boolean acq_in = false;
volatile long fc_count = 0;

const int trig_duration = 50; // msec, trigger pulse duration
boolean trig_2p_start_state = LOW;
boolean trig_2p_end_state = LOW;
boolean trig_stim_state[] = {LOW,LOW,LOW,LOW,LOW,LOW,LOW,LOW};
elapsedMillis trigPulseTimer = 0; // stimulus trigger timing must be specified by panda3D. 2P trigger is a brief pulse.
elapsedMillis stimulusTimers[nstimouts];

//serial transmission
const int nPars = 6;           // expected number of parameters from panda3D
const int pollInterval = 200;  // microseconds, polling interval for serial port communication. Determine limits experimentally.
const int timeout = 10;       // milliseconds to reset parameter index to zero if no update is received. Failsafe against non-ideal termination of serial transmission from the PC.
elapsedMicros p0 = 0;          // microseconds, time since last polling interval ended
elapsedMicros p1 = 0;          // timer used to clear all parameters if unusual interval between serial inputs is detected
elapsedMillis pto = 0;         // timer used to reset parameter index. Useful in case panda 3D terminates in between transmission.


char foo;

union {
  byte asByte[4];
  float asFloat;
} data1;

static float dataTemp[nPars] = {0.0};
static byte parNo = 0;


void clearSerialInBuffer() {
  while (Serial.available()>0) {  
    foo = Serial.read();
  }  
}

void fc_in_ISR() {
  fc_in = true;  
}

void acq_in_ISR_RISING() {
  acq_in = true;  
  attachInterrupt(digitalPinToInterrupt(acq_in_pin), acq_in_ISR_FALLING, FALLING);    
}

void acq_in_ISR_FALLING() {
  acq_in = false;
  fc_count = 0;  
  attachInterrupt(digitalPinToInterrupt(acq_in_pin), acq_in_ISR_RISING, RISING);
}

void floatToBools(float input, bool output[8], bool reverse = false) {
  // Convert float to 8-bit integer
  // Default if MSB to LSB, order is reversed if reverse == true
  uint8_t value = static_cast<uint8_t>(input);

  // Extract bits based on the reverse flag
  for (int i = 0; i < 8; i++) {
    int bitIndex = reverse ? i : (7 - i);
    output[i] = (value & (1 << bitIndex)) != 0;
  }
}


void setup() {

  pinMode(trig_2p_start_pin, OUTPUT);
  pinMode(trig_2p_end_pin, OUTPUT);
  pinMode(fc_in_pin, INPUT);
  pinMode(acq_in_pin, INPUT);

  for (int i = 0; i < nstimouts; i++) {
    pinMode(trig_stim_pins[i], OUTPUT);
    stimulusTimers[i] = 0.;
  }

  Serial.begin(460800); // baud rate specified here will be ignored, teensy will default to the fastest supported speed.
  clearSerialInBuffer();  

  analogWriteFrequency(analog_pin, 500000);
  analogWrite(analog_pin, int(255*(intensity/100.0)));

  attachInterrupt(digitalPinToInterrupt(fc_in_pin), fc_in_ISR, RISING);
  attachInterrupt(digitalPinToInterrupt(acq_in_pin), acq_in_ISR_RISING, RISING);

}

void loop() {

  if (fc_in) {
    if (acq_in) {
      fc_count += 1;      
    }
    fc_in = false;
  }

  if (pto > timeout) {
    parNo = 0;
  }
  
  // Setting parameters with serial input
  if (p0 > pollInterval) {    // periodically check for parameter updates
    
    if (Serial.available()>3) {
      
      for (int x=0; x<4; x++) data1.asByte[x] = Serial.read();
      dataTemp[parNo] = data1.asFloat;
      
      if (parNo == 0) {
        p1 = 0;
        pto = 0;
      }     

      parNo++;
      
      if (parNo==nPars) {

          parNo = 0;

          trig_2p_start                      = boolean(dataTemp[0]);
          trig_2p_end                        = boolean(dataTemp[1]);
          stim_mode_pulsed_float_from_serial = dataTemp[2];
          stim_duration                      = int(dataTemp[3]*1000);
          trig_stim_float_from_serial        = dataTemp[4];
          intensity_temp                     = int(dataTemp[5]);

          //update trig_stim and stim_mode_pulsed
          floatToBools(trig_stim_float_from_serial, trig_stim);
          floatToBools(stim_mode_pulsed_float_from_serial, stim_mode_pulsed);
          
          Serial.println(fc_count,1); // send frame count between successive requests to panda3D
          Serial.send_now();          // schedule immediate transmission
          fc_count = 0;               // reset frame counter once value has been transmitted

        if (trig_2p_start_state == LOW && trig_2p_start) {
            trig_2p_start_state = HIGH;
            digitalWrite(trig_2p_start_pin, trig_2p_start_state);
            trigPulseTimer = 0;
          }

        if (trig_2p_end_state == LOW && trig_2p_end) {
            trig_2p_end_state = HIGH;
            digitalWrite(trig_2p_end_pin, trig_2p_end_state);
            trigPulseTimer = 0;
          }

        for (int i = 0; i < nstimouts; i++) {
          
          if (stim_mode_pulsed[i]) {

            if (trig_stim[i] == HIGH) {
              trig_stim_state[i] = trig_stim[i];
              digitalWrite(trig_stim_pins[i], trig_stim_state[i]);
              stimulusTimers[i] = 0;
            }

          }

          else {
          
            if (trig_stim_state[i] != trig_stim[i]) {
              trig_stim_state[i] = trig_stim[i];
              digitalWrite(trig_stim_pins[i], trig_stim_state[i]);
            }
          
          }

        }

        if (intensity_temp != intensity) {
            intensity = intensity_temp;
            analogWrite(analog_pin, int(255*(intensity/100.0)));
        }
      }
      
    }
    p0 = 0;
  }

  if (trigPulseTimer > trig_duration) {

    if (trig_2p_start_state == HIGH) {
      trig_2p_start_state = LOW;
      digitalWrite(trig_2p_start_pin, trig_2p_start_state);      
    }

    if (trig_2p_end_state == HIGH) {
      trig_2p_end_state = LOW;
      digitalWrite(trig_2p_end_pin, trig_2p_end_state);      
    }

  }

  for (int i = 0; i < nstimouts; i++) {
    if (stim_mode_pulsed[i] && trig_stim_state[i] == HIGH) {
      if (stimulusTimers[i] >= stim_duration) {
        trig_stim_state[i] = LOW;
        digitalWrite(trig_stim_pins[i], trig_stim_state[i]);
      }
    }
  }

}