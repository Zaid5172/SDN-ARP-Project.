# SDN ARP Project



## Objective

Implement ARP request and reply handling using an SDN controller (Ryu).



## Requirements Met

1. Intercept ARP packets

2. Generate ARP responses

3. Enable host discovery

4. Validate communication



## Tools Used

- Mininet (Network Emulator)

- Ryu (SDN Controller)

- Open vSwitch (OpenFlow Switch)

- Python 3



## How to Run



### Terminal 1: Start the Controller
ryu-manager arp_handler.py
### Terminal 2: Start the Network
sudo mn --controller=remote,ip=127.0.0.1 --mac --switch ovsk,protocols=OpenFlow13
### Terminal 2: Run the Test

mininet> h2 ping -c 1 10.0.0.1

mininet> h1 ping -c 1 10.0.0.2


## Expected Output



### Terminal 1 (Controller Logs):

LEARNED: 10.0.0.2 is at 00:00:00:00:00:02

LEARNED: 10.0.0.1 is at 00:00:00:00:00:01

FOUND: 10.0.0.2 is in table. Replying.

### Terminal 2 (Mininet):
1 packets transmitted, 1 received, 0% packet loss

