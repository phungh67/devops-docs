#include "App.h"
#include "TinyTimber.h"
#include "canTinyTimber.h"
#include "sciTinyTimber.h"

// custom incl
#include <stdlib.h>
#include <string.h>

extern App app;
extern Can can0;
extern Serial sci0;

#define DAC_PORT (*(char *)0x4000741C)
#define MIN_VOLUME 0
#define MAX_VOLUME 20

#define DEBUG 0

void receiver(App *self, int unused)
{
  CANMsg msg;
  CAN_RECEIVE(&can0, &msg);
  SCI_WRITE(&sci0, "Can msg received: ");
  SCI_WRITE(&sci0, msg.buff);
}

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
    n = -1;
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
    buffer[i] = '\0';
  }

  for (int j = 0; j < i / 2; j++)
  {
    char temp = buffer[j];
    buffer[j] = buffer[i - j - 1];
    buffer[i - j - 1] = temp;
  }
}

void tone_generator(App *self, int state)
{
  if (self->mute == 1)
  {
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nReceive mute signal, surpress tone generator...\n");
    }
    DAC_PORT = 0;
    return;
  }

  // change the DAC bit
  int next_state = state ? 0 : 1;

  if (next_state == 1){
    DAC_PORT = self->val;
  } else {
    DAC_PORT = 0;
  }
  
  // generate tone
  AFTER(USEC(500), self, tone_generator, next_state);
}

void volume_control(App *self, int input)
{
  if (self->val + input > MAX_VOLUME)
  {
    // over max volume
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nMax volume exceeded, cap the value at max...\n");
    }
    self->val = MAX_VOLUME;
    return;
  }
  if (self->val + input < MIN_VOLUME)
  {
    if (DEBUG)
    {
      SCI_WRITE(&sci0, "\nMin volume exceeded, cap the value at min...\n");
    }
    self->val = MIN_VOLUME;
    return;
  }
  // handle normally
  self->val = self->val + input;
}

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
    return;
  }
  // newline == end input
  if (controL_character == '\n' || controL_character == '\r'){
    self->buffer[self->pos++] = '\0';
    int value = atoi(self->buffer);
    volume_control(self, value);

    char current_volume[12];
    int_to_string(self->val, current_volume);
    SCI_WRITE(&sci0, "\nCurrent volume: ");
    SCI_WRITE(&sci0, current_volume);
    SCI_WRITE(&sci0, "\n");
    self->pos = 0;
  } else if (self->pos < 12){
    self->buffer[self->pos++] = controL_character;
    SCI_WRITECHAR(&sci0, controL_character);
  }
}

void reader(App *self, int c)
{
  if (self->mode == 1){
    if (DEBUG) {
      SCI_WRITE(&sci0, "\nDefault mode, currently in volume mode...\n");
    }
    volume_control_handler(self, (char)c);
    return;
  }

  switch (c)
  {
  case 'v':
    /* code */
    if (DEBUG){
      SCI_WRITE(&sci0, "\nEnter volume mode, input value to adjust volume.\n");
    }
    self->mode = 1;
    self->pos = 0;
    SCI_WRITE(&sci0, "\nInput the volume, end with enter: ");
    break;
  case 's':
    self->mute = 1;
    break;
  default:
    break;
  }
}

void startApp(App *self, int arg)
{
  CANMsg msg;

  CAN_INIT(&can0);
  SCI_INIT(&sci0);
  SCI_WRITE(&sci0, "This is tone generator, it has 2 functions: \n");
  SCI_WRITE(&sci0, "The tone will be automatically run, can be stopped with 's'.\n");
  SCI_WRITE(&sci0, "Press 'v' to begin increase or decrease the voume.\n");
  SCI_WRITE(&sci0, "Press 'b' to adjust background payload period...\n");

  self->mute = 0;
  tone_generator(self, 1);
}

int main()
{
  INSTALL(&sci0, sci_interrupt, SCI_IRQ0);
  INSTALL(&can0, can_interrupt, CAN_IRQ0);
  TINYTIMBER(&app, startApp, 0);
  return 0;
}
