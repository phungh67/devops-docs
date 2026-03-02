#ifndef _APP_H
#define _APP_H

#include "TinyTimber.h"

typedef enum
{
  CONTROL_MODE = 0,
  VOLUME_MODE = 1,
  BACKGROUND_LOAD_MODE = 2,
  DEADLINE_CONTROL_MODE = 3
} Mode;

typedef struct
{
  Object super;         // inherit from Object
  Timer timer;          // inherit from Timer
  char buffer[32];      // buffer for user input
  Mode mode;             // 0: default, 1: volume control, 2: background load adjust
  int pos;
  int val;
  int mute;             // set mute to 1 to stop tone generator, set to 0 to start it
  int deadline;         // the deadline for the deadline control mode
} App;

typedef struct
{
  Object super;         // inherit from Object
  int val;               // the value of the tone, determined by the volume control
  int mute;             // set mute to 1 to stop tone generator, set to 0 to start it
  int deadline;         // the deadline for the deadline control mode
} ToneTask;

#define initToneTask() {initObject(), 0, 0, 0}

// Get methods (fetch current state)

int get_volume(ToneTask *);
int get_mute(ToneTask *);
int get_deadline(ToneTask *);

// Set methods (change object's state)
void set_volume(ToneTask *, int);
void set_mute (ToneTask *, int);
void set_deadline (ToneTask *, int);

// Self invoke method
void tone_generator(ToneTask *, int);

#define initApp() {initObject(), initTimer(), {0}, 0, 0, 0, 0, 0}

void reader(App *, int);
void receiver(App *, int);
void startApp(App *, int);

/*
Definition for load task - background finite loops
Implemented: 
  - loop range: hom many loops should be doen
  - period: like all other objects, should have some period
  - deadline: to have some priority since TinyTimber uses deadline to determine priority, EDF
*/
typedef struct
{
  /* data */
  Object super;
  int background_loop_range;    // the range of the background loop
  int period;
  int deadline;
} LoadTask;

int get_range(LoadTask *);
void adjust_range(LoadTask *, int amount);

int get_bg_deadline(LoadTask *);
void set_bg_deadline(LoadTask*, int);


#define initLoadTask() {initObject(), 0, 1300, 0}

#endif
