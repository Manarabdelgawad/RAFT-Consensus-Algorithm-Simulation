# -*- coding: utf-8 -*-


import threading
import random
import time

class RaftNode:
    def __init__(self, ip, port, cluster):
        self.ip = ip
        self.port = port
        self.cluster = cluster  # List of all nodes in the cluster
        self.state = 'FOLLOWER'
        self.current_term = 1
        self.voted_for = None
        self.log = []  # List to store log entries
        self.leader_id = None
        self.election_timeout = random.randint(150, 300) / 1000  # Timeout in seconds
        self.heartbeat_interval = 0.2  # Heartbeat interval for the leader
        self.vote_count = 0

    def start(self):
        """Start the Raft node."""
        print(f"Node {self.ip}:{self.port} started as {self.state}.")
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        """Main loop for the node."""
        while True:
            if self.state == 'FOLLOWER':
                self.run_follower()
            elif self.state == 'CANDIDATE':
                self.run_candidate()
            elif self.state == 'LEADER':
                self.run_leader()

    def run_follower(self):
        """Behavior of a follower."""
        print(f"Node {self.ip}:{self.port} is a FOLLOWER. Waiting for heartbeat...")
        timeout_start = time.time()
        while self.state == 'FOLLOWER':
            if time.time() - timeout_start >= self.election_timeout:
                print(f"Node {self.ip}:{self.port} timed out. Starting election.")
                self.state = 'CANDIDATE'
                break
            time.sleep(0.1)

    def run_candidate(self):
        """Behavior of a candidate during an election."""
        self.current_term += 1
        self.vote_count = 1  # Vote for self
        self.voted_for = self.ip
        print(f"Node {self.ip}:{self.port} started an election for term {self.current_term}.")

        # Request votes from other nodes
        threads = []
        for node in self.cluster:
            if node != self:
                t = threading.Thread(target=self.request_vote, args=(node,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        # Check if the node becomes a leader
        if self.vote_count > len(self.cluster) // 2:
            self.state = 'LEADER'
            self.leader_id = self.ip
            print(f"Node {self.ip}:{self.port} became the LEADER.")
        else:
            print(f"Node {self.ip}:{self.port} failed to become LEADER.")
            self.state = 'FOLLOWER'

    def run_leader(self):
        """Behavior of the leader."""
        print(f"Node {self.ip}:{self.port} is the LEADER. Sending heartbeats...")
        while self.state == 'LEADER':
            # Append a new log entry to the leader's log
            log_entry = f"Entry-{len(self.log)+1} from {self.ip}:{self.port}"
            self.log.append(log_entry)
            print(f"Leader {self.ip}:{self.port} added log: {log_entry}")

            # Send heartbeats with log entries to followers
            for node in self.cluster:
                if node != self:
                    threading.Thread(target=self.send_heartbeat, args=(node, log_entry)).start()
            time.sleep(self.heartbeat_interval)

    def request_vote(self, node):
        """Request a vote from another node."""
        print(f"Node {self.ip}:{self.port} requesting vote from {node.ip}:{node.port}.")
        if node.grant_vote(self.current_term):
            print(f"Node {node.ip}:{node.port} granted vote to {self.ip}:{self.port}.")
            self.vote_count += 1

    def grant_vote(self, term):
        """Grant a vote if the term is valid."""
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
        if self.voted_for is None or self.voted_for == self.ip:
            self.voted_for = self.ip
            return True
        return False

    def send_heartbeat(self, node, log_entry):
        """Send a heartbeat to another node."""
        print(f"Node {self.ip}:{self.port} sending heartbeat with log: {log_entry} to {node.ip}:{node.port}.")
        node.receive_heartbeat(self.current_term, self.ip, log_entry)

    def receive_heartbeat(self, term, leader_id, log_entry):
        """Receive a heartbeat from the leader."""
        if term >= self.current_term:
            self.current_term = term
            self.leader_id = leader_id
            self.state = 'FOLLOWER'
            # Append the log entry if not already in the log
            if log_entry not in self.log:
                self.log.append(log_entry)
                print(f"Node {self.ip}:{self.port} appended log: {log_entry}")

if __name__ == "__main__":
    # Simulate a cluster of 4 nodes
    cluster = []
    for i in range(4):
        node = RaftNode(ip=f"127.0.0.{i+1}", port=5000 + i, cluster=cluster)
        cluster.append(node)

    # Start all nodes
    for node in cluster:
        node.start()

    # Run the simulation for 10 seconds
    time.sleep(10)