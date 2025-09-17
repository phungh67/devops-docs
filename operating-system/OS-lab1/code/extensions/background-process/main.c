#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        exit(EXIT_FAILURE);
    }

    if (pid > 0) {
        // Parent process
        printf("Parent is still running, child PID = %d\n", pid);
        // Parent can continue doing other things
        return 0;
    }

    // Child process
    if (setsid() < 0) {  // detach from terminal
        perror("setsid failed");
        exit(EXIT_FAILURE);
    }

    // Optional: go to root dir
    chdir("/");

    // Redirect stdio to /dev/null
    freopen("/dev/null", "r", stdin);
    freopen("/dev/null", "w", stdout);
    freopen("/dev/null", "w", stderr);

    // Exec the new program in background
    char *args[] = {"/bin/sleep", "60", NULL};
    execvp(args[0], args);

    // If execvp fails
    perror("exec failed");
    exit(EXIT_FAILURE);
}
