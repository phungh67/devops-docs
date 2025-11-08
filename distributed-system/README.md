```Markdown
lab-1/ 
├── README.md 
├── client/ 
│ ├── go.mod 
│ └── http-client.go 
└── server/
|   └── advance-server/ 
│       ├── advance-server 
│       ├── http-advance_test.go 
│       └── http-main-core.go 
│   └── basic-server/ 
|	    ├── http-server_test.go 
|	    └── http-server.go 
└── go.mod
```

The sketch above illustrates the structure of this project, a simple TCP server written by Go lang. Refer to the theory and idea by this note [[Lab requirements|Theory and Idea]]

`Basic server` contains the skeletal structure of a TCP server that is capable of serving HTTP contents (and some other file types, check the `var supportedTypes` for more information). Connections are handled in TCP layer, while HTTP contents are processed by the `net\http` library. This server also has a limit of how many concurrency connections can be taken into at any instance of time, any followers after this limit must wait for a free slot. Inside this directory, there is also a test file with basic tests (GET, POST, errors test, ...).

`Advance server` contains source code and a binary-ready-to-run file.

# Usage:

To run the server
```Bash
cd lab1/server/advance-server
./advance-server 8080 #to run as a server, at port 8080

./advance-server -proxy 9080 #to run as a proxy, at port 9080
```

To test before compiling source code:
```Bash
cd lab1/server/advance-server
go test
go build

cd lab1/server/basic-server
go test
go build
```

Several test command from CLI
```Bash
curl -X GET localhost:8080/static/index.html -x localhost:40069
curl -X POST http://localhost:8080/test2.txt -T "dummyfile.txt" # remeber to have the file before testing
curl -X POST http://localhost:8080/test1.txt -d "hello world"
curl -X POST localhost:8080/test3.txt -x localhost:40069 -d "This is a test with not implement method"
```