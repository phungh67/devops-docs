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

# Draft reasoning

```Plaintext
for question 1a, the best metric maybe the geometrical aggregate value (produce of 3 speed up, then take the cubic root). Since as in the example (image 2), the qsort is definitely the dominant test, the cycles are larger than gsm and jpeg. So the weight or the average is simply not suitable. With that reasoning, both question 1a and 1b are solved. 2a and 2b. For exhaustive, the are 3 parameters, and 4 values for each, so the space should be: 4 to the power 3. But exhaustive is quite expensive to execute, so the experiment should be done buy: fixed the block size, change only the size of cache (resulted in the associative set). Lastly, a bigger cache does not necessary mean faster execution time, since larger cache requires more time to accessing and fetching, hence improving latency
```

```Plaintext
qsort requires 92,281,803 cycles, which completely dwarfs gsm-untoast at 22,361,246 cycles. A simple sum or weighted average would effectively make this a "qsort optimization lab," ignoring the performance gains of the other two applications entirely.   Here is a quick refinement of your answers for Section 2:2a (Parameter Space): Your logic for calculating the exhaustive space is correct in principle, but double-check the number of block size options. You have 4 cache sizes (4KB, 8KB, 16KB, 32KB) and 4 associativities (1-way, 2-way, 4-way, 8-way). However, the lab instructions for the final tables only specify 2 block sizes (32B and 128B). This makes the exhaustive design space $4 \times 4 \times 2 = 32$ total configurations, not 64.   2b (Navigation Methodology): Fixing the block size and sweeping the cache size by strictly controlling the nsets is exactly what the lab mandates to isolate the effect of a single parameter. You establish a baseline, change one variable at a time, and measure the delta.   The Latency Trade-off (2c/3b): Your final insight is the core lesson of the entire lab. As Table 2 outlines, upgrading to a 32-KB 8-way associative cache imposes a 4-cycle hit latency. If an application already fits comfortably in an 8-KB cache with a 2-cycle hit time, throwing more capacity at it will not reduce misses, it will only force the processor to wait longer for every single cache hit, ultimately degrading execution time.   
```