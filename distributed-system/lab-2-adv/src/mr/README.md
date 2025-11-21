
This is the file directory of this project. The implemented of `coordinator` and `worker` alongside with a `rpc` method for inter-communication.
```Bash
❯ ls -la mr/
.
├── coordinator.go
├── rpc.go
├── wc.so
└── worker.go
```

To run this project (inside the main function), we should compile it as a plugin
```Bash
❯ mr/ # inside the mr directory
go build -race -buildmode=plugin ../mrapps/wc.so
```
This will put all these `.go` file and build them into `wc.so`, a socket that contains all necessary instruction for coor, worker and rpc.
A little trick is, because the instruction told us to run the worker with `-race` flag, its socket must be built by passing `-race` flag too, otherwise it can have error `cannot load plugin`

Run the coordinator first, pass a list of file name that you want to run the word count:
```Bash
go run -race mrcoordinator.go pg-*.txt
```
It will create X tasks, X is equal to total number of file which name has "pg-".
In another terminal, run a worker:
```Bash
go run -race mworker.go wc.so
```
If you want to run multiple workers, open as many terminal as you want and run.

## Implementation
### The coordinator
```Go
type Coordinator struct {
    // Your definitions here.
    mapTasks        map[string]*TaskMetadata // a map of map task
    reduceTasks     map[string]*TaskMetadata //a map of reduce task
    cond            *sync.Cond               //condition variable (mutex)
    mapRemaining    int
    reduceRemaining int
    numbeOfReduce   int // number of "reduce" workes, used in pair with partition key
}
```
There are several attributes for a coordinator:
- The list of map task that should be run.
- The list of reduce task.
- A conditional variable (mutex) to protect the shared data (two lists above) from race condition when multiple workers try to get task.
- Number of map and reduce task remaining (the length of the list maybe not match with the remaining, because in that time, a task is till on progress, hence not counted as finished).
- Number of reduce worker. Normally, this number is far less than number of map workers.

The task metadata is just a data of a task, it is essentially to include these properties: name, type, status and time.
```Go
type Status string // indicate the status, done, undone,...

  
type TaskMetadata struct {
    number    int // the sequence number to mark a task, i.e: taks 1-1, task 1-2 (task 1, partition 1, task 1 partition 2)
    startTime time.Time
    status    Status
}
```

A coordinator should be able to fetch the task list (both list) then distributes to workers. But because reduce is the predecessor of the map, so map must be check first. The coordinator should check for map list first, then, reduce list.
```Go
    if c.mapRemaining != 0 {
        // check if we still have map task in the queue
        mapTask, numberOfMapTask := c.GetMapTask()
        for mapTask == "" { // the queue is empty
            if c.mapRemaining == 0 { // no job
                break
            }
            // still have job
            c.cond.Wait() // wait for accquiring the lock
            mapTask, numberOfMapTask = c.GetMapTask()
        }
        if mapTask != "" { // have somthing in the queue
            reply.Name = mapTask                    // name of the task
            reply.Number = numberOfMapTask          // total number of tasks
            reply.Type = mapType                    // type of task, of course it is map
            reply.PartitionNumber = c.numbeOfReduce // number of partition to assign
            c.cond.L.Unlock()                       // complete the critical selection
            return nil
        }
    }
```
If the queue is empty, but still have map job remain, must wait till the map is done. Once every map tasks are done, the reduce can begin. Otherwise, fetch and write a reply to worker.

The coordinator also has a mechanism to reschedule task if it consumed too many time (hanging forever, fault,...)

```Go
func (c *Coordinator) Rescheduler() {
    for {
        time.Sleep(100 * time.Millisecond) // avoid the "spinning" logic ~ busy wait
        c.cond.L.Lock()                    // if we want to change, better accquired the lock first
        if c.mapRemaining != 0 {
            for task := range c.mapTasks {
                currentTime := time.Now().UTC()
                startTime := c.mapTasks[task].startTime
                status := c.mapTasks[task].status
                if status == inprogress {
                    different := currentTime.Sub(startTime)
                    if different > timeOutCoefficient*time.Second {
                        // if the task was running too long, assume that we have 10
                        // log.Printf("Rescheduling a task with name '%s', type of this task '%s'.", task, mapType)
                        c.mapTasks[task].status = unstarted
                        c.cond.Broadcast() // signal the GetTask function, the Wait() function
                    }
                }
            }
        } else if c.reduceRemaining != 0 {
            c.cond.Broadcast() // signal the fetch (GetTask) to get reduce task or wait,...
            for task := range c.reduceTasks {
                currentTime := time.Now().UTC()
                startTime := c.reduceTasks[task].startTime
                status := c.reduceTasks[task].status
                if status == inprogress {
                    different := currentTime.Sub(startTime)
                    if different > timeOutCoefficient*time.Second { // double check for the time, if not specified the second -> take nanosecond -> extremely fast -> create redundant tasks
                        // log.Printf("Rescheduling a task with name '%s', type of this task '%s'.", task, reduceType)
                        c.reduceTasks[task].status = unstarted
                        c.cond.Broadcast()
                    }
                }
            }
        } else {
            c.cond.Broadcast() // if no task remains, then broadcast too
            c.cond.L.Unlock()  // end the accessing shared database
            break
        }
        c.cond.L.Unlock() // simply unlock
    }
}
```

### The RPC
 Remote Produce Call is a communication method, in this scenario, it should include the name, the number of the task (to be indexed in the map phase) as well as the partition number (how many reduce workers)
 ```Go
type GetTaskArgs struct {
}
 
type TaskType string // represent tasktype, either map or reduce task
 
type GetTaskReply struct {
    Name            string // the name of file that acts as the input
    Number          int    // task number (to be refferred each phases, not to be confused with partition ID to put to reduce)
    PartitionNumber int    // partition number, to match with which reducer will take it
    Type            TaskType
}
 
type UpdateTaskStatusArgs struct {
    Name string
    Type TaskType
}
  
type UpdateTaskStatusReply struct {
}
 ```

The empty structs are to satisfy the `net/rpc` requirements

### The worker

First is the map task
```Go
// function for map worker

func ExecuteMapTask(filename string, mapNumber, numberofReduce int, mapf func(string, string) []KeyValue) {
    file, err := os.Open(filename)
    if err != nil {
        log.Fatalf("Cannot open %v", filename)
    }

    content, err := io.ReadAll(file)
    if err != nil {
        log.Fatalf("Cannot read %v", filename)
    }

    file.Close()
    initVal := mapf(filename, string(content)) // map the filename with its content
    mp := map[int]*os.File{}                   // map of output result (cache)
    for _, kv := range initVal {
        // check for each "word"
        currentParition := ihash(kv.Key) % numberofReduce
        f, ok := mp[currentParition]

        if !ok {
            // create new "bucket" if the word is not existed
            f, err = os.CreateTemp("", "tmp")
            mp[currentParition] = f
            if err != nil {
                log.Fatal(err)
            }
        }

        kvj, _ := json.Marshal(kv)
        // fmt.Fprint(f, "%v\n", kvj)
        fmt.Fprintf(f, "%s\n", kvj)

    }
  
    // rename for the reduce phase
    for rNum, f := range mp {
        os.Rename(f.Name(), fmt.Sprintf("mr-%d-%d", mapNumber, rNum))
    }
}
```
Fetch the big file first, open it and consume it, with the help of `mapf` function, change the big body of text (whole file) into words. Then based on the hash function (the `ihash`) it will split these massive list of k-v ("word" - "1") into partition, then be processed by the reduce worker. The line `mp := map[int]*os.File{}` is for creating and mapping file with correct partition number. Finally, we rename it for the next step.

Second is the reduce task
```Go
func ExecuteReduceTask(partitionNumber int, reducef func(string, []string) string) {
    // fetch the filename
    filenames, _ := WalkDir("./", partitionNumber) // look for current directory of all file with reduceNumber pattern
    data := make([]KeyValue, 0)
    for _, filename := range filenames {
        file, err := os.Open(filename)
        if err != nil {
            log.Fatalf("Cannot open file %v, error %s", filename, err)
        }

        content, err := io.ReadAll(file)
        if err != nil {
            log.Fatalf("Cannot read %v, error %s", filename, err)

        }
        file.Close()

  

        // this split string got an error of unexpected EOF in test (wc test)
        kvstrings := strings.Split(string(content), "\n")
        // kv := KeyValue{}
        for _, kvstring := range kvstrings {
            // trimmed the whitespace, end character,...
            trimmed := strings.TrimSpace(kvstring)
            if len(trimmed) == 0 {
                // skip empty line
                continue
            }

            kv := KeyValue{} // allow the kv to get rid of garbage values
            err := json.Unmarshal([]byte(trimmed), &kv)
            if err != nil {
                log.Fatalf("Cannot unmarshal %v, error %s", filename, err)
                // weaker error catching logic
                // log.Printf("Warning: Cannot unmarshal line: %q, error: %v", trimmed, err)
                // continue
            }
            data = append(data, kv)
        }
    }
  
    sort.Sort(ByKey(data))
    oname := fmt.Sprintf("mr-out-%d", partitionNumber)
    ofile, _ := os.Create(oname)
    i := 0

    for i < len(data) {
        j := i + 1
        for j < len(data) && data[j].Key == data[i].Key {
            j++
        }
        values := []string{}
        for k := i; k < j; k++ {
            values = append(values, data[k].Value)
        }
        
        output := reducef(data[i].Key, values)
        fmt.Fprintf(ofile, "%v %v\n", data[i].Key, output)
        i = j

    }
    ofile.Close()
}
```
Try to read all the same partitioned file, parse these value, take all same key from files, sort, append the value `{Key: "Apple", Value: "1 1 1 1 1"}`. Finally, reduce all these value to 1 integer number.

There are several helper function, worker needs to call for task and update the task status for the coordinator.