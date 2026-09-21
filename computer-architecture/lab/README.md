# Instruction

In this repository, there are serveral helper scripts so that we don't have to manually change the parameter and run the simulation everytimes.

The base command to invoke the simulation is:

```Bash
./runsim_sim <path_to_configuration_directory> <name_of_config_file_no_extension>
```

For better structural, each configuration should be created within its own directory, for example, Lab1-Task1 has 2 configuration: the base config and the config with "idea" cache, so inside Lab1-Task1, there should be 2 directories: base and idea. Now, the command should be:

```Bash
./runsim_sim Lab1-Task1/base base1
# since the script automatically includes the configs path
```

# Important files

`base1.txt` - the base file, provided by TAs, keep this file as the main template, then change the corresponding parameters to achieve the desire model (processor, memory,...)

`auto-generate-config-cache.sh`- the script to batch running the simulation to find out the "best" memory (sweep the cache size, sweep the associativity of the cache,...)

# Note about the cache config on Lab 1, Task 2

The `cache` contains a text file, decribes the desire cache model. Then the script will creat the corresponding directory inside the `configs/Lab1-Task2/config_name`.

The main script also invokes some util scipts to parse the final result, and calculte some metrics (for benchmarking purpose) - still needs some tweak.