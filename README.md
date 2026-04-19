# SDN ARP Handling using POX Controller

##  Overview

This project implements *ARP handling in SDN* using the *POX controller* and *Mininet*.

The controller:

* Intercepts ARP packets
* Learns IP–MAC mappings
* Generates ARP replies
* Forwards packets between hosts

---

##  Topology


h1 —— s1 —— h2


* h1 → Host 1 (10.0.0.1)
* h2 → Host 2 (10.0.0.2)
* s1 → Switch
* POX → Controller

---

##  Setup & Run

### 1. Run POX Controller

```bash
cd ~/pox
./pox.py misc.arp_sdn
```

---

### 2. Run Mininet

```bash
sudo mn -c
sudo mn --topo single,2 --switch ovsk --controller remote,port=6633
```

---

### 3. Test

```bash
mininet> h1 ping h2
```

---

##  Working

1. h1 sends ARP request
2. Controller receives it
3. Learns MAC and IP
4. If unknown → flood
5. If known → send ARP reply
6. Packets are forwarded

---

## Expected Output

```
MAC LEARNED: ...
ARP LEARNED: ...
ARP FLOOD: ...
ARP REPLY: ...
FORWARD: ...
```

---

##  Conclusion

The controller learns host information dynamically, handles ARP requests, and enables communication between hosts efficiently.

---
