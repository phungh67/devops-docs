#include "App.h"
#include "TinyTimber.h"
#include "canTinyTimber.h"
#include "sciTinyTimber.h"

// custom incl
#include <stdlib.h>
#include <string.h>

extern App app;
extern ToneTask tone_task;
extern Can can0;
extern Serial sci0;
extern LoadTask load_obj;

#define DAC_PORT (*(char *)0x4000741C)
#define MIN_VOLUME 0
#define MAX_VOLUME 20

#define MAX_TASK 80000
#define MIN_TASK 1000

#define DEBUG 0

void receiver(App *self, int unused)
{
  CANMsg msg;
  CAN_RECEIVE(&can0, &msg);
  SCI_WRITE(&sci0, "Can msg received: ");
  SCI_WRITE(&sci0, msg.buff);
}

// helper function to print menu
void print_helper(App *self)
{
  (void)self;
  SCI_WRITE(&sci0, "\n=== Tone Generator Console ===\n");
  SCI_WRITE(&sci0, "Enter a command and press Enter.\n");
  SCI_WRITE(&sci0, "\nMain commands:\n");
  SCI_WRITE(&sci0, "  v | volume            Set volume (0-20)\n");
  SCI_WRITE(&sci0, "  s | mute              Mute tone output\n");
  SCI_WRITE(&sci0, "  r | unmute            Resume tone output\n");
  SCI_WRITE(&sci0, "  b | bg | background   Adjust background load\n");
  SCI_WRITE(&sci0, "  d | deadline          Enable deadline mode\n");
  SCI_WRITE(&sci0, "  e | nd | nodeadline   Disable deadline mode\n");
  SCI_WRITE(&sci0, "  h | help              Show this help\n");
  SCI_WRITE(&sci0, "\nIn volume mode:\n");
  SCI_WRITE(&sci0, "  Enter a number 0-20, then Enter\n");
  SCI_WRITE(&sci0, "  e               Return to main menu\n");
  SCI_WRITE(&sci0, "\nIn background mode:\n");
  SCI_WRITE(&sci0, "  +               Increase background load\n");
  SCI_WRITE(&sci0, "  -               Decrease background load\n");
  SCI_WRITE(&sci0, "  e               Return to main menu\n");
  SCI_WRITE(&sci0, "Choice: ");
}

// convert int to string, store in buffer
void int_to_string(int n, char *buffer)
{
  int i = 0, is_negative = 0;
  if (n == 0)
  {
    buffer[i++] = '0';
    buffer[i] = '\0';
    return;
  }
  if (n < 0)
  {
    is_negative = 1;
    n = -n;
  }
  while (n != 0)
  {
    buffer[i++] = (n % 10) + '0';
    n = n / 10;
  }
  if (is_negative)
  {
    // add sign
    buffer[i++] = '-';
  }
  buffer[i] = '\0';

  for (int j = 0; j < i / 2; j++)
  {
    char temp = buffer[j];
    buffer[j] = buffer[i - j - 1];
    buffer[i - j - 1] = temp;
  }
}

// a background task with specific period
void background_task(LoadTask *self, int unused)
{
  for (int i = 0; i < self->background_loop_range; i++)
  {
    asm("nop");     // do nothing, just insert "no operation" isntruction to CPU
  }

  if (self->deadline)
  {
    // in deadline mode: periodic release with relative deadline
    SEND(USEC(self->period), USEC(1300), self, background_task, 0);
  }
  else
  {
    // no-deadline mode: periodic release only (best-effort)
    AFTER(USEC(self->period), self, background_task, 0);
  }
}

// hanlder for loop range adjust
void background_loop_handler(App *self, LoadTask *task, char c)
{
  if (c == 'e')
  {
    // to menu
    self->mode = 0;
    SCI_WRITE(&sci0, "\nReturn to main menu...\n");
    print_helper(self);
    return;
  }
  // adjustment
  if (c == '+')
  {
    SYNC(&load_obj, adjust_range, 500);
  }
  else if (c == '-' && task->background_loop_range >= 500)
  {
    SYNC(&load_obj, adjust_range, -500);
  }
  else
  {
    return;
  }

  char buff[12];
  int current_range = SYNC(&load_obj, get_range, 0);
  int_to_string(current_range, buff);
  SCI_WRITE(&sci0, "\nBackground loop range: ");
  SCI_WRITE(&sci0, buff);
  SCI_WRITE(&sci0, "\n");
}

// tone generator
// object's method

// get volume value
int get_volume(ToneTask *self){
  return self->val;
}

// method to access and set the val property
void set_volume(ToneTask *self, int value){
  if (value > MAX_VOLUME){
    self->val = MAX_VOLUME;
  } else if (value < MIN_VOLUME) {
    self->val = MIN_VOLUME;
  } else {
    self->val = value;
  }
}

// method to access mute status
int get_mute(ToneTask *self){
  return self->mute;
}

// method to set the mute 
void set_mute(ToneTask *self, int enable){
  self->mute = enable;
}

// method to get deadline status
int get_deadline(ToneTask *self){
  return self->deadline;
}

// method to toogle deadline
void set_deadline(ToneTask *self, int enable){
  self->deadline = enable;
}


void tone_generator(ToneTask *self, int state)
{
  // check if muted
  if (get_mute(self)){
    if (DEBUG){
      SCI_WRITE(&sci0, "\nReceive the mute signal, surpress tone generator...\n");
    }
    DAC_PORT = 0;
    if (get_deadline(self)){
      SEND(USEC(500), USEC(100), self, tone_generator, state);
    } else {
      AFTER(USEC(500), self, tone_generator, state);
    }
    return;
  }


  // change the DAC bit
  int next_state = state ? 0 : 1;

  if (next_state == 1)
  {
    DAC_PORT = get_volume(self);
  }
  else
  {
    DAC_PORT = 0;
  }

  /* generate tone, it will execute every 500 microseconds,
     which means the frequency is 1kHz (since we toggle the bit
     every time, the period is 1ms) */
  if (get_deadline(self))
  {
    // deadline mode: periodic release with relative deadline
    // SEND(USEC(931), USEC(100), self, tone_generator, next_state);    // this is for 539 Hz tone
    // SEND(USEC(650), USEC(100), self, tone_generator, next_state);    // this is for 769 Hz tone
   SEND(USEC(500), USEC(100), self, tone_generator, next_state);      // this is for 1000 Hz tone
  }
  else
  {
    // no-deadline mode: periodic release only (best-effort)
    // AFTER(USEC(931), self, tone_generator, next_state);      // this is for 539 Hz tone, around 1500 loop
    // AFTER(USEC(650), self, tone_generator, next_state);      // this is for 769 Hz tone, arond 3000 loop
    AFTER(USEC(500), self, tone_generator, next_state);      // this is for 1000 Hz tone, around 4000 loop

  }
}

// control the volume (logic)
void volume_control(int input, ToneTask *tone_task)
{
  SYNC(tone_task, set_volume, input);
}

// handler for volume controller
void volume_control_handler(App *self, char controL_character)
{
  if (DEBUG)
  {
    SCI_WRITE(&sci0, "\nBegin volume control handler...\n");
  }

  if (controL_character == 'e')
  {
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nExit volume control handler...\n");
    }
    self->mode = 0;
    self->pos = 0;
    SCI_WRITE(&sci0, "\nReturn to main menu...\n");
    print_helper(self);
    return;
  }
  // newline == end input
  if (controL_character == '\n' || controL_character == '\r')
  {
    self->buffer[self->pos++] = '\0';
    int value = atoi(self->buffer);

    volume_control(value, &tone_task);


    char current_volume[12];
    int current_val = SYNC(&tone_task, get_volume, 0);
    int_to_string(current_val, current_volume);
    SCI_WRITE(&sci0, "\nCurrent volume: ");
    SCI_WRITE(&sci0, current_volume);
    SCI_WRITE(&sci0, "\n");
    self->pos = 0;
  }
  else if (self->pos < (int)(sizeof(self->buffer) - 1))
  {
    self->buffer[self->pos++] = controL_character;
    SCI_WRITECHAR(&sci0, controL_character);
  }
}

void deadline_control_tone_handler(ToneTask *self, int enable)
{
  if (enable)
  {
    set_deadline(self, enable);
  }
  else
  {
    set_deadline(self, 0);
  }
}

int get_bg_deadline(LoadTask *self){
  return self->deadline;
}

void set_bg_deadline(LoadTask* self, int enable){
  self->deadline = enable;
}

int get_range(LoadTask *self){
  return self->background_loop_range;
}

void adjust_range(LoadTask *self, int amount){
  self->background_loop_range += amount;
  if (self->background_loop_range > MAX_TASK) {
    self->background_loop_range = MAX_TASK;
  }
  if (self->background_loop_range < 500){
    self->background_loop_range = 500;
  }
}

void deadline_control_bg_handler(LoadTask *self, int enable)
{
  if (enable)
  {
    set_bg_deadline(self, enable);
    SCI_WRITE(&sci0, "\nEnable deadline deadline_control_bg_handler mode...\n");
  }
  else
  {
    set_bg_deadline(self, 0);
    SCI_WRITE(&sci0, "\nDisable deadline deadline_control_bg_handler mode...\n");
  }

}

void command_handler(App *self, char character)
{
  if (DEBUG)
  {
    SCI_WRITE(&sci0, "\nEnter command handler...\n");
  }

  if (character == '\n' || character == '\r')
  {
    self->buffer[self->pos] = '\0';

    // Normalize command to lowercase in-place.
    for (int i = 0; self->buffer[i] != '\0'; i++)
    {
      if (self->buffer[i] >= 'A' && self->buffer[i] <= 'Z')
      {
        self->buffer[i] = self->buffer[i] - 'A' + 'a';
      }
    }

    if (self->pos == 0)
    {
      print_helper(self);
      return;
    }

    if (strcmp(self->buffer, "v") == 0 || strcmp(self->buffer, "volume") == 0)
    {
      self->mode = VOLUME_MODE;
      self->pos = 0;
      SCI_WRITE(&sci0, "\nInput the volume, end with enter: ");
      return;
    }

    if (strcmp(self->buffer, "s") == 0 || strcmp(self->buffer, "mute") == 0)
    {
      SYNC(&tone_task, set_mute, 1);
      self->pos = 0;
      SCI_WRITE(&sci0, "\nMuting tone generator...\n");
      print_helper(self);
      return;
    }

    if (strcmp(self->buffer, "r") == 0 || strcmp(self->buffer, "unmute") == 0)
    {
      SYNC(&tone_task, set_mute, 0);
      self->pos = 0;
      SCI_WRITE(&sci0, "\nUnmuting tone generator...\n");
      print_helper(self);
      return;
    }

    if (strcmp(self->buffer, "b") == 0 || strcmp(self->buffer, "bg") == 0 || strcmp(self->buffer, "background") == 0)
    {
      self->mode = BACKGROUND_LOAD_MODE;
      self->pos = 0;
      SCI_WRITE(&sci0, "\nAdjusting background load (use '+' or '-' to change): ");
      return;
    }

    if (strcmp(self->buffer, "d") == 0 || strcmp(self->buffer, "deadline") == 0)
    {
      // load_obj.deadline = true;
      // tone_task.deadline = true;
      SYNC(&tone_task, deadline_control_tone_handler, 1);
      SYNC(&load_obj, deadline_control_bg_handler, 1);
      self->pos = 0;
      SCI_WRITE(&sci0, "\nEnable deadline control mode...\n");
      print_helper(self);
      return;
    }

    if (strcmp(self->buffer, "e") == 0 || strcmp(self->buffer, "nd") == 0 || strcmp(self->buffer, "nodeadline") == 0)
    {
      // load_obj.deadline = false;
      // tone_task.deadline = false;
      SYNC(&tone_task, deadline_control_tone_handler, 0);
      SYNC(&load_obj, deadline_control_bg_handler, 0);
      self->pos = 0;
      SCI_WRITE(&sci0, "\nDisable deadline control mode...\n");
      print_helper(self);
      return;
    }

    if (strcmp(self->buffer, "h") == 0 || strcmp(self->buffer, "help") == 0)
    {
      self->pos = 0;
      print_helper(self);
      return;
    }

    self->pos = 0;
    SCI_WRITE(&sci0, "\nUnknown command. Type 'help' for valid commands.\n");
    print_helper(self);
    return;
  }
  else if (self->pos < (int)(sizeof(self->buffer) - 1))
  {
    self->buffer[self->pos++] = character;
    SCI_WRITECHAR(&sci0, character);
  }
}

// handler for sci interrupt, read user input and call corresponding handler
void reader(App *self, int c)
{
  // if currently in volume cotrol mode, call volume control handler
  if (self->mode == VOLUME_MODE)
  {
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nCurrently in volume mode...\n");
    }
    volume_control_handler(self, (char)c);
    return;
  }

  // if currently in background load adjust mode, call background load handler
  if (self->mode == BACKGROUND_LOAD_MODE)
  {
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nCurrently in background load mode...\n");
    }

    background_loop_handler(self, &load_obj, (char)c);
    return;
  }

  // otherwise, it is in control mode
  command_handler(self, (char)c);

}

void startApp(App *self, int arg)
{
  CAN_INIT(&can0);
  SCI_INIT(&sci0);

  self->mute = 0;   // set default to unmuted
  self->mode = CONTROL_MODE;   // set default mode

  print_helper(self);   /* print help info */

  ASYNC(&tone_task, tone_generatortone_generator, 1);
  ASYNC(&load_obj, background_task, 0);
}

int main()
{
  INSTALL(&sci0, sci_interrupt, SCI_IRQ0);
  INSTALL(&can0, can_interrupt, CAN_IRQ0);
  TINYTIMBER(&app, startApp, 0);
  return 0;
}
