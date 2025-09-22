#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <utmp.h>
#include <time.h>
#include <string.h>


// int main()
// {
//     printf("test\n");

//     const char* s = getenv("USER");
//     const char* s1 = getenv("LOGNAME");

//     // If the environment variable doesn't exist, it returns NULL
//     printf("USER :%s\t LOGNAME :%s\n", (s != NULL) ? s : "getenv returned NULL", (s1 != NULL) ? s1 : "getenv returned NULL");

//     printf("end test\n");
// }

int main(int argc, char* argv[]){
    int ret;
    char* options = "hl";
    int long_opt = 0;
    
    struct option longopts[] = {
        {"help", no_argument, NULL, 'h'},
        {"long", no_argument, NULL, 'l'},
        {NULL, 0, NULL, 0}
    };

    setutent(); // open the file at /var/run/utmp
    /**
     * ❯ sudo cat /var/run/utmp
    [sudo] password for huyhoang-ph:
    ~~~reboot6.6.87.2-microsoft-standard-WSL2�T�h��5~~~runlevel6.6.87.2-microsoft-standard-WSL2�T�h14�
    consoleconsLOGIN��T�h�Htty1tty1LOGIN�T�h�H8pts/1/1huyhoang-ph��T�h\��,pts/4ts/4huyhoang-ph�]�ha�% 
     */
    struct utmp *current_record;

    while((ret = getopt_long(argc, argv, options, longopts, NULL)) != -1){
        switch(ret){
            case 'h':
                printf("This is the help message for %s prgram.\n", argv[0]);
                printf("This program will print the current logged in users.\n");
                printf("Supported operator are: -h, -l.\n");
                printf("-h --help:  print the help message for this program.\n");
                printf("-l --long:  print each user in one line with details (login time and tty).\n");
                exit(EXIT_SUCCESS);
            case 'l':
                long_opt = 1;
                break;
            case '?':
                fprintf(stderr, "Unknown option: %c\n", optopt);
                printf("Use -h or --help to see the help message.\n");
                exit(EXIT_FAILURE);
            default:
                fprintf(stderr, "Error parsing options\n");
                exit(EXIT_FAILURE);
        }
    }

    while ((current_record = getutent()) != NULL){
        if(current_record->ut_type == USER_PROCESS){
            printf("%s", current_record->ut_user); // username
            if(long_opt){
                printf("\t%s", current_record->ut_line); // tty
                // print login time
                time_t login_time = current_record->ut_tv.tv_sec;
                struct tm *tm_info = localtime(&login_time);
                char time_buffer[26];
                strftime(time_buffer, 26, "%Y-%m-%d %H:%M", tm_info);
                printf("\t%s", time_buffer);

                // list any remote host
                if(strlen(current_record->ut_host) > 0){
                    printf("\t(%s)", current_record->ut_host);
                }
            }

            printf("\n");
        }
    }

    endutent(); // close the file at /var/run/utmp
    return 0;
}