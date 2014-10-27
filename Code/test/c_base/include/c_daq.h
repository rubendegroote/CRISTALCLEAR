/*

  Data acquisition for ISOLDE.
  kieran.renfrew.campbell@cern.ch
  ruben.degroote@cern.ch

 */

#ifndef DAQ_TRIGGER_BASE_H
#define DAQ_TRIGGER_BASE_H

#include "NIDAQmxBase.h"


/*
  Defines all parameters which need to be passed to here at runtime
  by the user (using python)
*/

struct UserData {
  char readChannel[256]; // analogue input channel
  char writeChannel[256];

  int reportEvery; // call back to python every ; not yet implemented

} userData;

/*
Holds all the variables needed by
DAQmxBaseWriteAnalogF64 but that we don't
want to make global.
*/
struct WriteData {
  TaskHandle taskHandle;

  uInt64 samplesPerChan;
  float64 gtimeout;
  int32 gpointsWritten;
  char gerrBuff[2048];

} writeParams;

/*
  channel: counter channel for digital data acquisition,
  so in this case "Dev1/ctr1" for PFI3

  contReport: continuously reports back to python

  reportEvery: callback to function every n loops

*/
void setParameters(char* readChannel, char* writeChannel, 
		   int reportEvery);


void printAllInfo(void);

/* Begins data acquisition */
void acquire(void (*pyCallbackFunc)(uInt32),
	     double (*pyVoltFunc)(uInt32),
	     _Bool (*isFinished)(uInt32));


#endif
