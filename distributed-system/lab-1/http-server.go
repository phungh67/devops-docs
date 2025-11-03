package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

const MAX_CONNECTION = 10

type server struct {
	connectionCount atomic.Int32
	wg              sync.WaitGroup
	listener        net.Listener
	shutdown        chan struct{}
	connection      chan net.Conn
}

func newServer(address string) (*server, error) {
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return nil, fmt.Errorf("failed to listen on address %s : %w", address, err)
	}

	return &server{
		listener:   listener,
		shutdown:   make(chan struct{}),
		connection: make(chan net.Conn, MAX_CONNECTION),
	}, nil
}

// handle the "accept connection phase"
func (s *server) acceptConnections() {
	defer s.wg.Done()

	for {
		select {
		case <-s.shutdown:
			return
		default:
			conn, err := s.listener.Accept()
			if err != nil {
				continue
			}
			s.connection <- conn
		}
	}
}

func (s *server) worker() {
	defer s.wg.Done()

	for conn := range s.connection {
		s.handleConnection(conn)
	}
}

func (s *server) handleConnection(conn net.Conn) {
	defer conn.Close()

	currentConn := s.connectionCount.Add(1)
	log.Printf("Total active connection is: %d", currentConn)

	time.Sleep(5 * time.Second)

	remainingConn := s.connectionCount.Add(-1)
	log.Printf("Handling a connection completed, remaining: %d", remainingConn)
}

func (s *server) Start() {
	s.wg.Add(MAX_CONNECTION)
	for i := 0; i < MAX_CONNECTION; i++ {
		go s.worker()
	}

	go s.acceptConnections()
}

func (s *server) Stop() {
	close(s.shutdown)
	s.listener.Close()

	done := make(chan struct{})
	go func() {
		s.wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		return
	case <-time.After(5 * time.Second):
		fmt.Println("Time out waiting remaining connections to be finished.")
		return
	}
}

func main() {
	arguments := os.Args
	if len(arguments) == 1 {
		fmt.Println("Input a valid port number!")
		return
	}

	PORT := ":" + arguments[1]
	s, error := newServer(PORT)
	if error != nil {
		fmt.Println(error)
		os.Exit(1)
	}

	s.Start()
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	fmt.Println("Shutting down the server ...")
	s.Stop()
	fmt.Println("Server stopped.")
}
