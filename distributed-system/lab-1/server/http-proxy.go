package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"time"
)

const MAX_TIMEOUT = 10

func (s *server) proxyHandleConnection(conn net.Conn) {
	defer conn.Close()

	currentConn := s.connectionCount.Add(1)
	log.Printf("Total active connection: %d", currentConn)

	conn.SetReadDeadline(time.Now().Add(MAX_TIMEOUT * time.Second))

	reader := bufio.NewReader(conn)

	req, err := http.ReadRequest(reader)
	if err != nil {
		if err != io.EOF {
			log.Printf("Error parsing request: %v", err)
			fmt.Fprintf(conn, "HTTP/1.1 400 Bad Request\r\n\r\n")
		}
		s.connectionCount.Add(-1)
		return
	}

	conn.SetReadDeadline(time.Time{})
	backendHost := req.Host
	if _, _, err := net.SplitHostPort(backendHost); err != nil {
		backendHost = net.JoinHostPort(backendHost, "80")
	}

	log.Printf("Proxy request for %s to %s", req.URL, backendHost)
	backendConn, err := net.Dial("tcp", backendHost)
	if err != nil {
		log.Printf("Failed to dial with the backend '%s': %v", backendHost, err)
		fmt.Fprintf(conn, "HTTP/1.1 502 Bad Gateway\r\n\r\n")
		s.connectionCount.Add(-1)
		return
	}

	defer backendConn.Close()

	if err := req.Write(backendConn); err != nil {
		log.Printf("Failed to write request to backend: %v", err)
		return
	}

	if _, err := io.Copy(conn, backendConn); err != nil {
		log.Printf("Error copying response to client: %v", err)
	}

	remainingConn := s.connectionCount.Add(-1)
	log.Printf("Handling a connection completed, remaining: %d", remainingConn)
}
