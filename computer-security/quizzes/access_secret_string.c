
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

int main() {
  bool print_key = false;
  char input[4] = {0};
  printf("Input:");
  gets(input);

  printf("Input was: %s\n", input);
  if (print_key) {
    char hidden_answer[];
    printf("Answer is: %s\n", hidden_answer);
  }

  return 0;
}
