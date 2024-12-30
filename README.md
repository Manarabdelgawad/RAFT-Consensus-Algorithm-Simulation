# RAFT-Consensus-Algorithm-Simulation

this project simulates the RAFT consensus algorithm, demonstrating how distributed systems achieve leader election and maintain consistency.

The simulation models a cluster of nodes that can transition between FOLLOWER, CANDIDATE, and LEADER states to ensure fault-tolerant coordination.

Key Features

Simulates leader election among nodes.

Implements log replication from the leader to followers.

Models heartbeat signals to maintain leadership and prevent unnecessary elections.

Demonstrates dynamic state transitions based on timeouts and votes.

How It Works

A cluster of nodes is created and initialized.

Each node begins as a FOLLOWER and waits for a heartbeat.

If no heartbeat is received within a random timeout, the node starts an election and becomes a CANDIDATE.

The node that receives the majority of votes transitions to LEADER and begins sending heartbeats to followers.

Log entries are replicated to ensure all nodes maintain the same state.
