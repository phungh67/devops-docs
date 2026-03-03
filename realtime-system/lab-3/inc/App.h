#ifndef _APP_H
#define _APP_H

#include "TinyTimber.h"

typedef struct
{
  Object super;
  char buffer[32];   // receive command
  int buffer_pos;    // pointer to buffer position
  int current_index; // current tone index to play
  int key;           // shifted key
  int tempo;         // length to play
  int mute;          // indicate mute or not
} App;

#define initApp() {initObject(), {0}, 0, 0, 0, 120, 0}

void reader(App *, int);
void receiver(App *, int);
void startApp(App *, int);

void play_note(App *, int);
void stop_note(App *, int);

typedef struct
{
  Object super;
  int val;    // value for the volume
  int mute;   // mute or not
  int period; // period
} ToneTask;

#define initToneTask() {initObject(), 0, 0, 0};

// set method
void tone_set_mute(ToneTask *);
void tone_set_period(ToneTask *);
void tone_set_volume(ToneTask *);

#endif
