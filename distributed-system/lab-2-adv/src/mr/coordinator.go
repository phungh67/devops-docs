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

const timeOutCoefficient = 10

var (
	unstarted  Status = "unstarted"
	inprogress Status = "inprogress"
	completed  Status = "completed"
)

type Coordinator struct {
	// Your definitions here.
	mapTasks         map[string]*TaskMetadata // a map of map task
	reduceTasks      map[string]*TaskMetadata //a map of reduce task
	cond             *sync.Cond               //condition variable (mutex)
	mapRemaining     int
	reduceRemaining  int
	numbeOfReduce    int      // number of "reduce" workes, used in pair with partition key
	mapTaskAddresses []string // addressbook of all map workers
	workers          map[int]*WorkerInfor
	nextWorkerID     int
}

type Status string // indicate the status, done, undone,...

type TaskMetadata struct {
	name      string
	number    int // the sequence number to mark a task, i.e: taks 1-1, task 1-2 (task 1, partition 1, task 1 partition 2)
	startTime time.Time
	status    Status
	workerID  int
}

type WorkerInfor struct {
	workerID   int
	lastUpTime time.Time
	address    string
	isFailed   bool
}

func (c *Coordinator) Register(args *RegisterArgs, reply *RegisterReplyArgs) error {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()

	c.nextWorkerID++
	id := c.nextWorkerID

	c.workers[id] = &WorkerInfor{
		workerID:   id,
		lastUpTime: time.Now(),
		address:    args.WorkerAddress,
		isFailed:   false,
	}

	reply.WorkerID = id
	return nil
}

func (c *Coordinator) HealthCheckWorker(args *HealthCheckArgs, reply *HealthCheckReply) error {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()

	if w, ok := c.workers[args.WorkerID]; ok {
		w.lastUpTime = time.Now()
	}
	return nil
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
	return "", -1
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
	return "", -1
}

// get task reply (for worker called to coordinator)
func (c *Coordinator) GetTask(args *GetTaskArgs, reply *GetTaskReply) error {
	c.cond.L.Lock() // lock the conditional variable when accessing shared variable
	// check map task
	if w, ok := c.workers[args.WorkerID]; ok {
		w.lastUpTime = time.Now()
	}

loop:
	if c.mapRemaining > 0 {
		for name, task := range c.mapTasks {
			if task.status == unstarted {
				task.status = inprogress
				task.workerID = args.WorkerID
				task.startTime = time.Now()

				reply.Name = name
				reply.Number = task.number
				reply.Type = mapType
				reply.PartitionNumber = c.numbeOfReduce
				reply.MapAddresses = make([]string, len(c.mapTaskAddresses))
				copy(reply.MapAddresses, c.mapTaskAddresses)

				c.cond.L.Unlock()
				return nil
			}
		}

		c.cond.Wait()
		goto loop
	}

	if c.reduceRemaining > 0 {
		for name, task := range c.reduceTasks {
			if task.status == unstarted {
				task.status = inprogress
				task.workerID = args.WorkerID
				task.startTime = time.Now()

				reply.Name = name
				reply.Number = task.number
				reply.Type = reduceType
				reply.MapAddresses = c.mapTaskAddresses

				c.cond.L.Unlock()
				return nil
			}
		}

		if c.mapRemaining > 0 {
			goto loop
		}

		c.cond.Wait()
		if c.mapRemaining > 0 {
			goto loop
		}
		goto loop
	}

	reply.Type = exitType
	c.cond.L.Unlock()
	return errors.New("all tasks are completed, no more remaining")
}

// update the status for map or reduce task
func (c *Coordinator) UpdateTaskStatus(args *UpdateTaskStatusArgs, reply *UpdateTaskStatusReply) error {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()

	if w, ok := c.workers[args.WorkerID]; ok && w.isFailed {
		return nil
	}

	if args.Type == mapType { // must collect the information of the map worker first
		if task, ok := c.mapTasks[args.Name]; ok {
			if task.status != completed {
				task.status = completed
				task.workerID = args.WorkerID
				c.mapRemaining--
				if task.number >= 0 && task.number < len(c.mapTaskAddresses) {
					c.mapTaskAddresses[task.number] = args.WorkerAddress
				}
				c.cond.Broadcast()
			}
		}
	} else if args.Type == reduceType {
		if task, ok := c.reduceTasks[args.Name]; ok {
			if task.status != completed {
				task.status = completed
				c.reduceRemaining--
				c.cond.Broadcast()
			}
		}
	}
	return nil
}

func (c *Coordinator) ReportMapWorkerFailure(args *ReportFailureArgs, reply *ReportFailureReply) error {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()

	var foundTask *TaskMetadata
	for _, task := range c.mapTasks {
		if task.number == args.MapTaskIndex {
			foundTask = task
			break
		}
	}

	if foundTask != nil && foundTask.status == completed {
		foundTask.status = unstarted
		foundTask.workerID = -1
		c.mapRemaining++

		c.cond.Broadcast()
	}
	return nil
}

func (c *Coordinator) FailTask(args *FailTaskArgs, reply *FailTaskReplyArgs) error {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()

	if args.Type == mapType {
		if task, ok := c.mapTasks[args.Name]; ok {
			if task.workerID == args.WorkerID && task.status == inprogress {
				task.status = unstarted
				task.workerID = -1
				c.cond.Broadcast()
			}
		}
	} else if args.Type == reduceType {
		if task, ok := c.reduceTasks[args.Name]; ok {
			if task.workerID == args.WorkerID && task.status == inprogress {
				task.status = unstarted
				task.workerID = -1
				c.cond.Broadcast()
			}
		}
	}
	return nil
}

func (c *Coordinator) CrashDetector() {
	for {
		time.Sleep(500 * time.Millisecond)
		c.cond.L.Lock()

		if c.mapRemaining == 0 && c.reduceRemaining == 0 {
			c.cond.L.Unlock()
			return
		}

		now := time.Now()
		needBroadcast := false

		for id, worker := range c.workers {
			if worker.isFailed {
				continue
			}
			if now.Sub(worker.lastUpTime) > timeOutCoefficient*time.Second {
				log.Printf("worker %d is dead", id)
				worker.isFailed = true

				for _, task := range c.mapTasks {
					if task.workerID == id {
						if task.status == inprogress {
							task.status = unstarted
							task.workerID = -1
							needBroadcast = true
						} else if task.status == completed {
							task.status = unstarted
							task.workerID = -1
							c.mapRemaining++
							needBroadcast = true
						}
					}
				}

				for _, task := range c.reduceTasks {
					if task.workerID == id && task.status == inprogress {
						task.status = unstarted
						task.workerID = -1
						needBroadcast = true
					}
				}
			}
		}

		if needBroadcast {
			c.cond.Broadcast()
		}

		c.cond.L.Unlock()
	}
}

// function to just signal the "main" program that we have done

// main/mrcoordinator.go calls Done() periodically to find out
// if the entire job has finished.
func (c *Coordinator) Done() bool {
	c.cond.L.Lock()
	defer c.cond.L.Unlock()
	return c.mapRemaining == 0 && c.reduceRemaining == 0
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

// create a Coordinator.
// main/mrcoordinator.go calls this function.
// nReduce is the number of reduce tasks to use.
func MakeCoordinator(files []string, nReduce int) *Coordinator {
	mapTask := map[string]*TaskMetadata{}
	for i, file := range files {
		mapTask[file] = &TaskMetadata{
			name:     file,
			workerID: -1,
			number:   i,
			status:   unstarted,
		}
	}

	reduceTask := map[string]*TaskMetadata{}
	for i := 0; i < nReduce; i++ {
		reduceTask[fmt.Sprintf("%d", i)] = &TaskMetadata{
			number:   i,
			status:   unstarted,
			workerID: -1,
		}
	}

	mu := sync.Mutex{}

	cond := sync.NewCond(&mu)

	c := Coordinator{
		mapTasks:         mapTask,
		reduceTasks:      reduceTask,
		mapRemaining:     len(files),
		reduceRemaining:  nReduce,
		numbeOfReduce:    nReduce,
		cond:             cond,
		mapTaskAddresses: make([]string, len(files)), // space equals to length of the passed files
		workers:          make(map[int]*WorkerInfor),
	}

	// Your code here.

	// start a new rountine for the rescheduler (constanly check for exceeded time task independently)
	go c.CrashDetector()

	c.server()
	return &c
}
