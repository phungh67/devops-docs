# 🛠️ Applied Systems & DevOps Codebase

![GitHub top language](https://img.shields.io/github/languages/top/phungh67/devops-docs?style=flat-square&logo=c)
![GitHub language count](https://img.shields.io/github/languages/count/phungh67/devops-docs?style=flat-square)
![Forks](https://img.shields.io/github/forks/phungh67/devops-docs?style=flat-square)

Welcome to the implementation warehouse. This repository contains the source code, practical assignments, and engineering projects completed during my Master's studies in **Computer Systems & Cybersecurity** at **Chalmers University of Technology**. 

While theoretical systems design is crucial, this repository is where those concepts are actually built, broken, and debugged.

## 📖 About This Repository

Each directory in this repository corresponds to a core computing domain and contains the actual implemented code (built individually or with teammates). Because the requirements of these domains vary wildly, you will find a multi-language environment here—predominantly **C** (for low-level OS and real-time systems) and **Go** (for highly concurrent distributed systems), alongside Python, C++, and shell scripting.

*Disclaimer: These implementations were built as academic and exploratory exercises. The code prioritizes functional learning over "clean" production-ready enterprise standards. If you use this for inspiration, be prepared to refactor it to fit your own architectural style!*

## 🗂️ Project Directory

The codebase is split into the following operational domains:

* **[`/computer-networking`](./computer-networking/)** - Network protocol implementations, socket programming, and packet manipulation.
* **[`/computer-security`](./computer-security/)** - Applied security exercises and system hardening scripts.
* **[`/data-privacy`](./data-privacy/)** - Algorithms for data masking, including a small-scale *reconstruction attack* implementation.
* **[`/distributed-system`](./distributed-system/)** - High-concurrency engineering. Contains full implementations of complex distributed algorithms including **MapReduce**, **Raft Consensus**, and a **Chord Ring** DHT.
* **[`/operating-system`](./operating-system/)** - Low-level systems programming. Includes custom memory management exercises, concurrency handling (e.g., the *narrow bridge* problem), and a fully customized Bash shell.
* **[`/realtime-system`](./realtime-system/)** - Code for strict timing constraints and deterministic scheduling models.

## 🚀 Key Implementations & Highlights

If you're exploring the codebase, here are a few of the most complex engineering challenges tackled inside:

1. **Custom Bash Shell** (`/operating-system/`)
   Built from the ground up to handle process forking, environment variables, and I/O redirection.
2. **Distributed Algorithms in Go** (`/distributed-system/`)
   Writing a robust implementation of the **Raft consensus algorithm** and **MapReduce** coordinator/worker logic.
3. **Reconstruction Attack** (`/data-privacy/`)
   A programmatic demonstration of how supposedly "anonymized" datasets can be unmasked using overlapping queries.
4. **Concurrency Synchronization** (`/operating-system/`)
   Solving classic deadlock/starvation puzzles like the *Narrow Bridge* problem using mutexes and semaphores in C.

## 👨‍💻 Author

**Huy Hoang Phung**
* *Cloud & DevOps Engineer*
* *M.Sc. Candidate in Computer Systems and Cybersecurity @ Chalmers*
* [GitHub Profile](https://github.com/phungh67)

---
*If any of these implementations help you wrap your head around a complex algorithm, feel free to star the repo!* ⭐
