# ARP Handling in SDN using Ryu



## Objective



To implement ARP handling using Ryu controller.



## Tools Used



* Mininet

* Ryu Controller

* Ubuntu VM



## Steps to Run



1. Run controller:

   python3 -m ryu.cmd.manager arp_controller.py



2. Run Mininet:

   sudo mn --controller=remote --switch=ovsk,protocols=OpenFlow13



3. Test:

   pingall



## Output



* ARP packets captured

* Successful communication between hosts



## Conclusion



ARP handling successfully implemented.


