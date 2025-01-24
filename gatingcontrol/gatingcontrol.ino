//pin assignments
const int lineclockin = 17;
const int pmtgateout = 2;
const int projectorgateout = 3;
const int auxgateout = 4;

//output pin states
//must be defined correctly, determine by measurement/datasheet for every piece of hardware
//take into account if level shifting circuit inverts signal
boolean pmtoffstate = HIGH;
boolean projectoroffstate = LOW;
boolean auxoffstate = LOW;
boolean pmtgatestate = pmtoffstate;
boolean projectorgatestate = projectoroffstate;
boolean auxgatestate = auxoffstate;

//durations in microseconds
//other devices will be forced off when pmt has to turn on
unsigned long pmtgatedur = 15;          //pmt off duration from the end of line acquisition
unsigned long pmtgateresponsetime = 1;  //duration to wait for pmt to turn off before turning on other light sources
unsigned long projectorgatedur = 11;    //projector on duration
unsigned long auxgatedur = 11;          //auxillary device on duration

//hard-coded delay before turning pmt back on to ensure other devices are off
//the delay is included in pmtgatedur. See setup
const int pmtondelay = 3;

//line frequency and optional skipping to gate longer durations by sacrificing lines of data
int linefreq = 8000;  //Line clock frequency in Hz
int linestoskip = 0;  //how many line clock triggers to skip before initiating a gate sequence
int linecounter = 0;
int linefreq_eff = 0;
unsigned long selftriginterval = 0;

//duration to wait for a line clock trigger before going into the "idle" state. 
//must be greater than max(2*line interval, flyback duration)
unsigned long acquisitiontimeout = 1000;    

//timers
elapsedMicros lctimer;
elapsedMicros pmtgatetimer;
elapsedMicros projectorgatetimer;
elapsedMicros auxgatetimer;
elapsedMicros selftrigtimer;

//state definitions
String state = "idle";         //acquisition or idle
String gatestate = "gateoff";  //gateon or gateoff

//variable to update with an interrupt to catch the falling edge of ScanImage line clock
//change in attachInterrupt() to trigger on rising edge if required
volatile boolean gatetrigger = false;

void setup() {

  pinMode(lineclockin, INPUT);
  pinMode(pmtgateout, OUTPUT);
  pinMode(projectorgateout, OUTPUT);
  pinMode(auxgateout, OUTPUT);

  digitalWrite(pmtgateout, pmtgatestate);
  digitalWrite(projectorgateout, projectorgatestate);
  digitalWrite(auxgateout, auxgatestate);

  attachInterrupt(digitalPinToInterrupt(lineclockin), lctrigISR, FALLING);

  pmtgatedur = pmtgatedur - pmtondelay;  //include delay in pmtgateduration

  if (linestoskip > 0) {
    linefreq_eff = int(linefreq / (linestoskip + 1));
    selftriginterval = int(pow(10,6) / linefreq_eff);
  } 
  else {
    selftriginterval = int(pow(10,6) / linefreq);
  }

  selftrigtimer = 0;
  lctimer = 0;
}

void loop() {

  if (state == "idle" && gatetrigger == true) {
    state = "acquisition";
    lctimer = 0;
    linecounter = 0;
  }

  if (state == "acquisition" && lctimer > acquisitiontimeout) {
    state = "idle";
  }

  if (state == "acquisition" && gatetrigger == true) {

    lctimer = 0;
    linecounter += 1;
    gatetrigger = false;

    if (linecounter > linestoskip) {
      linecounter = 0;
      gatestate = "gateon";
      selftrigtimer = 0;
      pmtgatetimer = 0;
      projectorgatetimer = 0;
      auxgatetimer = 0;
    }
  }

  if (state == "idle" && selftrigtimer >= selftriginterval && gatestate == "gateoff") {
    gatestate = "gateon";
    selftrigtimer = 0;
    lctimer = 0;
    pmtgatetimer = 0;
    projectorgatetimer = 0;
    auxgatetimer = 0;
  }

  if (gatestate == "gateon") {

    if (pmtgatestate != pmtoffstate && pmtgatetimer <= pmtgatedur) {
      pmtgatestate = pmtoffstate;
      digitalWrite(pmtgateout, pmtgatestate);
    }

    if (projectorgatestate == projectoroffstate && projectorgatetimer <= projectorgatedur && pmtgatetimer >= pmtgateresponsetime) {
      projectorgatestate = !projectoroffstate;
      digitalWrite(projectorgateout, projectorgatestate);
    }

    if (auxgatestate == auxoffstate && auxgatetimer <= auxgatedur && pmtgatetimer >= pmtgateresponsetime) {
      auxgatestate = !auxoffstate;
      digitalWrite(auxgateout, auxgatestate);
    }

    if (pmtgatestate == pmtoffstate && pmtgatetimer >= pmtgatedur) {

      pmtgatestate = !pmtoffstate;

      if (projectorgatestate != projectoroffstate) {
        projectorgatestate = projectoroffstate;
        digitalWrite(projectorgateout, projectorgatestate);
      }

      if (auxgatestate != auxoffstate) {
        auxgatestate = auxoffstate;
        digitalWrite(auxgateout, auxgatestate);
      }

      delayMicroseconds(pmtondelay);
      digitalWrite(pmtgateout, pmtgatestate);

      gatestate = "gateoff";
    }

    if (projectorgatestate != projectoroffstate && projectorgatetimer >= projectorgatedur + pmtgateresponsetime) {
      projectorgatestate = projectoroffstate;
      digitalWrite(projectorgateout, projectorgatestate);
    }

    if (auxgatestate != auxoffstate && auxgatetimer >= auxgatedur + pmtgateresponsetime) {
      auxgatestate = auxoffstate;
      digitalWrite(auxgateout, auxgatestate);
    }
  }
}

void lctrigISR() {
  gatetrigger = true;
}