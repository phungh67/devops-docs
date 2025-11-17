package mr

import (
	"errors"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"sync"
	"time"
)

var (
	unstarted  Status = "unstarted"
	inprogress Status = "inprogress"
	completed  Status = "completed"
)

type Coordinator struct {
	// Your definitions here.
	mapTasks        map[string]*TaskMetadata // a map of map task
	reduceTasks     map[string]*TaskMetadata //a map of reduce task
	cond            *sync.Cond               //condition variable (mutex)
	mapRemaining    int
	reduceRemaining int
	numbeOfReduce   int // number of "reduce" workes, used in pair with partition key
}

// Your code here -- RPC handlers for the worker to call.

// an example RPC handler.
//
// the RPC argument and reply types are defined in rpc.go.

type Status string // indicate the status, done, undone,...

type TaskMetadata struct {
	number    int // the sequence number to mark a task, i.e: taks 1-1, task 1-2 (task 1, partition 1, task 1 partition 2)
	startTime time.Time
	status    Status
}

// get task
func (c *Coordinator) GetMapTask() (string, int) {
	for task := range c.mapTasks {
		if c.mapTasks[task].status == unstarted {
			c.mapTasks[task].startTime = time.Now().UTC()
			c.mapTasks[task].status = inprogress
			return task, c.mapTasks[task].number
		}
	}
	return "Null", -1
}

// get reduce task
func (c *Coordinator) GetReduceTask() (string, int) {
	for task := range c.reduceTasks {
		if c.reduceTasks[task].status == unstarted {
			c.reduceTasks[task].startTime = time.Now().UTC()
			c.reduceTasks[task].status = inprogress
			return task, c.reduceTasks[task].number
		}
	}
	return "Null", -1
}

// get task reply
func (c *Coordinator) GetTask(args *GetTaskArgs, reply *GetTaskReply) error {
	c.cond.L.Lock() // lock the conditional variable when accessing shared variable
	// check map task
	if c.mapRemaining != 0 {
		// check if we still have map task
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
			reply.Name = mapTask                    // name of the task
			reply.Number = numberOfMapTask          // total number of tasks
			reply.Type = mapType                    // type of task, of course it is map
			reply.PartitionNumber = c.numbeOfReduce // number of partition to assign
			c.cond.L.Unlock()                       // complete the critical selection
			return nil
		}
	}
	// check reduce task
	if c.reduceRemaining != 0 {
		reduceTask, numberOfReduceTask := c.GetReduceTask()
		for reduceTask == "" {
			if c.reduceRemaining == 0 {
				c.cond.L.Unlock()
				return errors.New("All tasks are completed, no more remaining.")
			}
			c.cond.Wait()
			reduceTask, numberOfReduceTask = c.GetReduceTask()
		}
		// dont have to fetch the queue because reduce task can be taken from output of map
		reply.Name = reduceTask
		reply.Number = numberOfReduceTask
		reply.Type = reduceType
		c.cond.L.Unlock()
		return nil
	}

	c.cond.L.Unlock()
	return errors.New("All tasks are completed, no more remaining.")
}

// start a thread that listens for RPCs from worker.go
func (c *Coordinator) server() {
	rpc.Register(c)
	rpc.HandleHTTP()
	//l, e := net.Listen("tcp", ":1234")
	sockname := coordinatorSock()
	os.Remove(sockname)
	l, e := net.Listen("unix", sockname)
	if e != nil {
		log.Fatal("listen error:", e)
	}
	go http.Serve(l, nil)
}

// main/mrcoordinator.go calls Done() periodically to find out
// if the entire job has finished.
func (c *Coordinator) Done() bool {
	ret := false

	// Your code here.

	return ret
}

// create a Coordinator.
// main/mrcoordinator.go calls this function.
// nReduce is the number of reduce tasks to use.
func MakeCoordinator(files []string, nReduce int) *Coordinator {
	mapTask := map[string]*TaskMetadata{}
	for i, file := range files {
		mapTask[file] = &TaskMetadata{
			number: i,
			status: unstarted,
		}
	}

	reduceTask := map[string]*TaskMetadata{}
	for i := 0; i < nReduce; i++ {
		reduceTask[fmt.Sprintf("%d", i)] = &TaskMetadata{
			number: i,
			status: unstarted,
		}
	}

	mu := sync.Mutex{}

	cond := sync.NewCond(&mu)

	c := Coordinator{
		mapTasks:        mapTask,
		reduceTasks:     reduceTask,
		mapRemaining:    len(files),
		reduceRemaining: nReduce,
		numbeOfReduce:   nReduce,
		cond:            cond,
	}

	// Your code here.

	c.server()
	return &c
}
