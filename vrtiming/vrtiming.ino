const int trig_2p_start_pin = 2;
const int trig_2p_end_pin = 3;
const int trig_stim_pin = 4;     
const int analog_pin = 5;         // analog output for stimulus intensity control
const int fc_in_pin = 16;         // frame clock input pin
const int acq_in_pin = 17;        // acquisition clock input pin (frame clock inputs coming in when acquisition clock is low are ignored)

boolean trig_2p_start = false; 
boolean trig_2p_end = false;
boolean trig_stim_pulsed = false;
int stim_duration = 0; // in milliseconds
boolean trig_stim = false;
int stim_mode = 0; // 0: continuous, 1: pulsed
int intensity = 0; //percentage of maximum
int intensity_temp = 0;
volatile boolean fc_in = false;
volatile boolean acq_in = false;
volatile long fc_count = 0;

const int trig_duration = 50; // msec, trigger pulse duration
boolean trig_2p_start_state = LOW;
boolean trig_2p_end_state = LOW;
boolean trig_stim_pulsed_state = LOW;
boolean trig_stim_state = LOW;
elapsedMillis trigPulseTimer = 0; // stimulus trigger timing must be specified by panda3D. 2P trigger is a brief pulse.
elapsedMillis stimulusTimer = 0.;

//serial transmission
const int nPars = 7;           // expected number of parameters from panda3D
const int pollInterval = 200;  // microseconds, polling interval for serial port communication. Determine limits experimentally.
const int timeout = 1000;      // milliseconds to reset parameter index to zero if no update is received. Failsafe against non-ideal termination of serial transmission from the PC.
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


void setup() {

  pinMode(trig_2p_start_pin, OUTPUT);
  pinMode(trig_2p_end_pin, OUTPUT);
  pinMode(trig_stim_pin, OUTPUT);
  pinMode(fc_in_pin, INPUT);
  pinMode(acq_in_pin, INPUT);

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

          trig_2p_start     = boolean(dataTemp[0]);
          trig_2p_end       = boolean(dataTemp[1]);
          trig_stim_pulsed  = boolean(dataTemp[2]);
          stim_duration     = int(dataTemp[3]*1000);
          trig_stim         = boolean(dataTemp[4]);
          stim_mode         = int(dataTemp[5]);
          intensity_temp    = int(dataTemp[6]);
          
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

        if (trig_stim_pulsed_state == LOW && trig_stim_pulsed) {
            trig_stim_pulsed_state = HIGH;
            digitalWrite(trig_stim_pin, trig_stim_pulsed_state);
            stimulusTimer = 0;
          }

        if (trig_stim_state != trig_stim) {
            trig_stim_state = trig_stim;
            digitalWrite(trig_stim_pin, trig_stim_state);
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

  if (stimulusTimer > stim_duration && stim_mode == 1) {
    trig_stim_pulsed_state = LOW;
    digitalWrite(trig_stim_pin, trig_stim_pulsed_state);
  }

}

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