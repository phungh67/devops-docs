#include "App.h"
#include "TinyTimber.h"
#include "canTinyTimber.h"
#include "sciTinyTimber.h"

// constant
const int brother_john_melodies[32] = {
    0, 2, 4, 0, 0, 2, 4, 0,
    4, 5, 7, 4, 5, 7, 7, 9,
    7, 5, 4, 0, 7, 9, 7, 5,
    4, 0, 0, -5, 0, 0, -5, 0};

const int periods[25] = {
    2024, 1911, 1803, 1702, 1607, // Indices -10 to -6
    1517, 1432, 1351, 1276, 1204, // Indices -5 to -1
    1136, 1073, 1012, 955, 902,   // Indices 0 to 4
    851, 803, 758, 716, 675,      // Indices 5 to 9
    638, 602, 568, 536, 506       // Indices 10 to 14
};

const int beat_lengths[32] = {
    2, 2, 2, 2, 2, 2, 2, 2, // a a a a a a a a
    4, 2, 2, 4,             // b a a b
    1, 1, 1, 2, 2,          // c c c a a
    1, 1, 1, 2, 2, 2, 2,    // c c c a a a a
    4, 2, 2, 4              // b a a b
};

const MIN_SHIFT - 10

    extern App app;
extern Can can0;
extern Serial sci0;

// internal helper function

// get the shifted value with input key
int get_period(int note_pos, int key_offset)
{
  int base = brother_john_melodies[note_pos]; // original frequent of the indicate note

  int shifted = base + key_offset;

  int actual_index = shifted - MIN_SHIFT;

  // error catch
  if (actual_index < 0)
    actual_index = 0;
  if (actual_index > 24)
    actual_index = 24;

  return periods[actual_index];
}

void receiver(App *self, int unused)
{
  CANMsg msg;
  CAN_RECEIVE(&can0, &msg);
  SCI_WRITE(&sci0, "Can msg received: ");
  SCI_WRITE(&sci0, msg.buff);
}

void reader(App *self, int c)
{
  SCI_WRITE(&sci0, "Rcv: \'");
  SCI_WRITECHAR(&sci0, c);
  SCI_WRITE(&sci0, "\'\n");
}

void startApp(App *self, int arg)
{
  CANMsg msg;

  CAN_INIT(&can0);
  SCI_INIT(&sci0);
  SCI_WRITE(&sci0, "Hello, hello...\n");

  msg.msgId = 1;
  msg.nodeId = 1;
  msg.length = 6;
  msg.buff[0] = 'H';
  msg.buff[1] = 'e';
  msg.buff[2] = 'l';
  msg.buff[3] = 'l';
  msg.buff[4] = 'o';
  msg.buff[5] = 0;
  CAN_SEND(&can0, &msg);
}

int main()
{
  INSTALL(&sci0, sci_interrupt, SCI_IRQ0);
  INSTALL(&can0, can_interrupt, CAN_IRQ0);
  TINYTIMBER(&app, startApp, 0);
  return 0;
}
