/*

  Data acquisition for ISOLDE.
  kieran.renfrew.campbell@cern.ch
  ruben.degroote@cern.ch

 */


#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>


#include "NIDAQmxBase.h"
#include "daq_trigger_base.h"
#include "eltime.h"

#define DAQmxErrChk(functionCall) { if( DAQmxFailed(error=(functionCall)) ) { goto Error; } }


/*
  channel: channel for analogue data acquisition (eg "/Dev1/ai8")
  sampleRate: rate for analogue data acquisition
  triggerSource: channel for the trigger (eg "/Dev1/PFI0")
  noTriggers: number of triggers to record data for. If -1 loop is infinite */  
void setParameters(char* channel, float64 sampleRate, 
		   char* triggerSource, int noTriggers,
		   _Bool contReport) {

  strcpy (userData.channel, channel);
  strcpy(userData.triggerSource, triggerSource);

  userData.sampleRate = sampleRate;
  userData.noTriggers = noTriggers;

  userData.contReport = contReport;
}

void printAllInfo(void) {
  printf("Channel: %s \n", userData.channel);
  printf("Trigger source: %s \n", userData.triggerSource);
  printf("Sample rate: %f \n", userData.sampleRate);
  printf("Numer of triggers: %d \n", userData.noTriggers);
  printf("Continuous reporting: %d \n", userData.contReport);
}

void acquire(void (*pyCallbackFunc)(float64[data_per_trigger]))
{
    // Task parameters
    int32       error = 0;
    TaskHandle  taskHandle = 0;
    char        errBuff[2048]={'\0'};
    //   int32       i;
    time_t      startTime;

    // Channel parameters

    float64     min = -10.0;
    float64     max = 10.0;

    // Timing parameters
    char        clockSource[] = "OnboardClock";
    uInt64      samplesPerChan = data_per_trigger; // only using 1 channel
    
    // Triggering parameters
    uInt32      triggerSlope = DAQmx_Val_RisingSlope;

    // Data read parameters
    #define     bufferSize (uInt32)data_per_trigger
    float64     data[bufferSize];
    int32       pointsToRead = bufferSize;
    int32       pointsRead;
    float64     timeout = 10.0;
    int32       totalRead = 0;

    // Timing stuff
    struct timeval tvBegin, tvEnd, tvDiff;


    char taskCreate[] = "Creating base task\n";
    char voltageCreate[] = "Creating voltage channel\n";
    char configTiming[] = "Configuring device timing\n";
    char configTrig[] = "Configuring rising edge trigger\n";

    int count = 0;
    
    startTime = time(NULL);

    /* create the task */
    printf(taskCreate);
    DAQmxErrChk (DAQmxBaseCreateTask("",&taskHandle));

       /* create voltage channel */
    printf(voltageCreate);
    DAQmxErrChk (DAQmxBaseCreateAIVoltageChan(taskHandle,
					      userData.channel,"",
					      DAQmx_Val_Cfg_Default,
					      min,max,
					      DAQmx_Val_Volts,NULL));

    /* configure sampe timing */
    printf(configTiming);
    DAQmxErrChk (DAQmxBaseCfgSampClkTiming(taskHandle,
					   clockSource,
					   userData.sampleRate,
					   DAQmx_Val_Rising,
					   DAQmx_Val_FiniteSamps,
					   samplesPerChan));

    /* configure the trigger */
    printf(configTrig);
    DAQmxErrChk (DAQmxBaseCfgDigEdgeStartTrig(taskHandle,
					      userData.triggerSource,
					      triggerSlope));

    startTime = time(NULL);

    // Begin loop time
    gettimeofday(&tvBegin, NULL);
 
    /* Loop for desired number of triggers or infinitely if set to -1 */
    for(; count < userData.noTriggers || userData.noTriggers == -1; ++count) {

      // start and read data
      DAQmxErrChk (DAQmxBaseStartTask(taskHandle));
      DAQmxErrChk (DAQmxBaseReadAnalogF64(taskHandle,
					  pointsToRead,
					  timeout,
					  DAQmx_Val_GroupByScanNumber,
					  data,
					  bufferSize,
					  &pointsRead,NULL));

      totalRead += pointsRead;
      printf("Level %d \n", count);

      // callback to python to present data
      if(userData.contReport)
	pyCallbackFunc(data);

      /* // stop task */
      DAQmxErrChk (DAQmxBaseStopTask(taskHandle));

      DAQmxErrChk (DAQmxBaseCfgDigEdgeStartTrig(taskHandle,
      						userData.triggerSource,
      						triggerSlope));

    }

    // work out time difference & print
    gettimeofday(&tvEnd, NULL);
    timeval_subtract(&tvDiff, &tvEnd, &tvBegin);
    printf("%ld.%06ld\n", tvDiff.tv_sec, tvDiff.tv_usec);

    /* stop & delete task */
    DAQmxErrChk (DAQmxBaseStopTask(taskHandle));
    DAQmxErrChk (DAQmxBaseClearTask(taskHandle));

    printf("\nAcquired %ld total samples.\n",totalRead);

Error:
    if( DAQmxFailed(error) )
        DAQmxBaseGetExtendedErrorInfo(errBuff,2048);
    if(taskHandle != 0) {
        DAQmxBaseStopTask (taskHandle);
        DAQmxBaseClearTask (taskHandle);
    }
    if( DAQmxFailed(error) )
		printf ("DAQmxBase Error %ld: %s\n", error, errBuff);
    
}


