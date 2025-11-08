#TCP #server #socket-programing
>[! Overview]
>Create a simple TCP server with Golang, only use the basic Network Socket programming library (basic `net` lib of Golang) to spin up a server, then implement some basic methods including `GET` and `POST` to handle `HTTP` contents. When handling these contents, additional libraries can be used, but not for constructing the server.

# 1. Checklist for the server
- [x] A simple server that handle TCP connections.
- [x] Can handle connections concurrently, but does not spawn infinities (has connection cap).
- [x] Server HTTP content (and of course, must be from the supported list)
- [x] Gracefully stop (advanced) to not leave any zombie or orphan processes.
# 2. Server's journal

This is the notes during construction process
## 2.1. Simple server that can server TCP connections

Requirements are the same level in the **Computer Network**, instead of using C programming language, we use Golang.
There are several steps that must be done before running the server:
- Using `net` library to create the server.
- The server must handle connections as first in first out and must be blocked if the number of incoming connections are larger than its limit. These connections should be waited till a free slot is released.

The first problem, creating a server is not too challenge. The `net` library provides a method to create a server (on a specific port) `net.Listen(network string, address string)`. This function allows the listening for incoming traffic on the `localhost` with a port `address`.

```Go
func newServer(address string) (*server, error) {
    listener, err := net.Listen("tcp", address)
    if err != nil {
        return nil, fmt.Errorf("failed to listen on address %s : %w", address, err)
    }

    return &server{
        listener:   listener,
        shutdown:   make(chan struct{}),
        connection: make(chan net.Conn),
    }, nil
}
```
Along with listens and accepts any incoming request, our basic `Server` (created under the form of a `struct`) should have control method: `start`, `stop` (gracefully and must handle the remaining connections before shutting down).
 ```Go
 func (s *server) Start() {
    s.wg.Add(1)
    go s.acceptConnections()
  /*
  Other methods to handle concurrently connection go in here
  */
}
``` 
The `Start` function above add a `wait.group`, indicates that this function is blocked indefinitely till all its `gorountines` are completed. The keyword `go` marks the beginning of a new `gorountines` [official-document](https://go.dev/tour/concurrency/1), it is very similar to thread in the operating system, but more lightweight.

As the requirement stated, at least 2 go-rountines are needed: one for listening the request (running and accept all incoming traffics) and other to handle them. But this is concurrency server, more threads are needed.

```Go
    s.wg.Add(MAX_CONNECTION)

    for i := 0; i < MAX_CONNECTION; i++ {

        go s.worker()

    }
```
This code created `worker` to handle the incoming connection, each worker will be responsible for a request, it also ensures that no more than `MAX_CONNECTION` are created. 

Why this can ensure the server's characteristics: no more than `MAX_CONNECTION` connections inside the server at any instance? This because of the `channel` in the Go lang only "By default, sends and receives block until the other side is ready. This allows goroutines to synchronize without explicit locks or condition variables" [Channel](https://go.dev/tour/concurrency/2) The server starts with `MAX_CONNECTION` number of workers, each worker acts as an destination to receive the input from the channel `connection` inside the `server` object. So this command:
```go
func (s *server) acceptConnections() {
    defer s.wg.Done()
    for {
        conn, err := s.listener.Accept()
		// error handling...
        s.connection <- conn
    }
}
```
 `s.connection <- conn` will be blocked until there is 1 free worker.
 Once the connection is accepted by the server, it will be handled depending on its original `method` (GET, POST).
## 2.2. Implement Proxy

The basic code can be reused, the proxy also has a concurrency limit (equals to the limit of the basic server, 10) and only server GET request. So that any request (that can be handled by the server should not go through the proxy).

```Go
func (s *server) proxyHandler(conn net.Conn){
	...
        backendHost := req.Host
        if _, _, err := net.SplitHostPort(backendHost); err != nil {
            backendHost = net.JoinHostPort(backendHost, "80")
        }

        log.Printf("Proxy request for %s to %s", req.URL, backendHost)
        backendConn, err := net.Dial("tcp", backendHost)
	...
}
```
The code above is a simple logic for the proxy, it should stand between client and actual server. Whenever it receives a request from client, I should "dial" to the host. We can further implement logging, filter or caching contents through this proxy, but the assignment only requires a simple one for `GET` request, so this will be the main logic:
```Go
switch req.Method {
    case "GET":
		// Handling GET logic
    default:
        log.Printf("Method %s is not implemented", req.Method)
        s.handleError(conn, http.StatusNotImplemented)
    }
	...
```
Inside the main, we should check what mode the server will be started on:
```Go
...
    if *isProxy {
        log.Printf("Proxy mode, listening on port %d...", actualPort)
        s.Start(true)
    } else {
        log.Printf("Server mode, listening on port %d...", actualPort)
        s.Start(false)
    }
...
```
Modify the `worker` a little:
```Go
func (s *server) worker(handler func(net.Conn)) {
    defer s.wg.Done()
    for conn := range s.connection {
        handler(conn)
    }
}
```
The worker's behavior depends on which type of the server, it will take `handleConnection(conn net.Conn)` as the handler, otherwise, it will be `proxyHandledConnection(...)`
