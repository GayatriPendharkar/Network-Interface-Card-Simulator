Compilation Instructions for NIC Simulator:
Language: Python 2.7
External packages needed: numpy 1.10.4

1. Open NicSim.py in any linux machine with the following command:
	$ python NicSim.py
2. Upon execution it'll ask for the following prompts: 
	Please enter desired simulation time in seconds: 10
	Please enter the mean number of messages per second for Send module: 3000
	Please enter the mean number of messages per second for Internet:600
	Enter Packet Processor Queue size in KB:448
3. Enter desired values for the prompts as given above
4. It'll display the results as follows:
	Rpp processing rate is:  137.438544215 ns/bit
	Tpp processing rate is:  1.92611990391 ns/bit
	Tx throughput is:  519.151999344 Mbps
	Rx throughput is:  7.26744023226 Mbps
	Packet loss at Receiver is:  0.0 %
	Message loss at Packet Queue is:  15.2133333333 %
	Average delay in NIC for each message processed in send module is:  3045.96816335 microseconds
	Average delay in NIC for each packet processed in RM is:  3.8423318977 microseconds
5. log files for SM,MM and RM will be generated in the same directory

Note: 
>If a value less than 64 or greater than 448 is given for PQ size the program will round it off to 64 or 448 depending on whichever is closest
>If 0 is given as input for simulation time, it'll be considered as 1 second
>If negative values are given as inputs, the program will consider it's absolute value
>If fractional values are given as inputs, the program will round them off to the nearest integer value
>The log files submitted in this directory are for the inputs given above
