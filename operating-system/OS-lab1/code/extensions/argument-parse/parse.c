#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int* parse_arguments(int argc, char *argv[]){
    // will return an array, first element is the opt_result, indicate the arguments passed
    // the second element is the position to read the actual command's parameter.
    int* result_array = (int*)(malloc (2*sizeof(int)));
    int opt_result = 0; // default is 0, no option was passed and the command will print the short list.
    int param_postion = 1; // since the first position is for the program name, should count from 1.
    // debug message, comment it when testing for ... less text printed
    /*     printf("The number of the arguments passed: %d\n", argc);
    for (int i = 0; i < argc; i++){
        printf("Argument %d: %s\n", i, argv[i]);
    } */

    // begin to parse the arguments
    int opt;
    int flag = 0;
    while ((opt = getopt(argc, argv, "lah")) != -1)
    {
        switch (opt)
        {
        case 'h':
            printf("This command is used to list information about the directory, default is listing the current directory or the directory you passed to this command.\n");
            printf("Usage: %s [-l] [-a] [-h]\n", argv[0]);
            printf("  -l           Use a long listing format\n");
            printf("  -a           Include directory entries whose names begin with a dot (.) - or a hidden one.\n");
            printf("  -h           Display this help message\n");
            flag = 1;
            exit(EXIT_SUCCESS);
        case 'l':
            // long listing format
            // debug message
            // printf("Long listing format...\n");
            opt_result += 1;
            flag = 1;
            break;
        case 'a':
            // include the hidden file and the parent directory
            // debug message
            // printf("Including hidden files...\n");
            opt_result += 2;
            flag = 1;
            break;
        case '?':
            fprintf(stderr, "Unknown option: %c\n", optopt);
            printf("Use -h to see the help message.\n");
            exit(EXIT_FAILURE);
        default:
            fprintf(stderr, "Error parsing options\n");
            exit(EXIT_FAILURE);
        }
    }

    param_postion += flag;

    // scan all for all arguments passed
    // if (optind < argc)
    // {
    //     printf("Positional arguments:\n");
    //     for (int i = optind; i < argc; i++)
    //     {
    //         printf(" %s\n", argv[i]);
    //     }
    // }

    // debug message
    // printf("The result of parsing the arguments: %d\n", opt_result);
    result_array[0] = opt_result;
    result_array[1] = param_postion;
    return result_array;
}

int main(int argc, char *argv[]){
  return 0;
}