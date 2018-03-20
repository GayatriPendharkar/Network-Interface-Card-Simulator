import numpy as np
import random

PackProcQueue=[]
TransQueue =[]
ReceiveBuffer = []
packet = []
Internetpackets=[]
receiverDrop = []
PPDrop = []
receiveCount = []
tppclock=[]
rppclock = []
txclock = []
Rxclock = []
numberofframes = []
Messageentertime = []
messageexittime = []
packetentertime = []
packetexittime = []
sendlog=open('SM-log.txt','wb')
maclog = open('Controller-log.txt','wb')
receivelog = open('receivebuffer-log.txt','wb')


#Packet Processor Queue
def enqueuepq(packet): #To enqueue messages to Packet Processor Queue
    if len(packet)>64000*8: #To truncate message to 64KB
        packet = packet[:64000*8-1]
    size=0
    for i in range(len(PackProcQueue)):
        size += len(PackProcQueue[i])
    if 256000*8-size>len(packet):
        PackProcQueue.append(packet)
        Messageentertime.append(clock)
    else:
        PPDrop.append(1)
def dequeuepq(): #To dequeue messages from Packet Processor Queue
    return PackProcQueue.pop(0)

#Packet Processor
def packetprocessor(packet):
    temp = []
    if len(packet)<=1500*8:
        temp.append(packet.zfill(1526*8))
    elif len(packet)>1500*8:
        while len(packet)>1500*8:
            temp.append(packet[:(1500*8)-1].zfill(1526*8))
            packet = packet[(1500*8):]
        temp.append(packet.zfill(1526*8))
    numberofframes.append(len(temp))
    for i in range(len(temp)):
        enqueuetq(temp[i])

#Transmitter Queue
def enqueuetq(frame): #To enqueue packets to transmitter queue
    TransQueue.append(frame)

def dequeuetq(clock): #To dequeue packets from transmitter queue
    clock = str(clock)
    sendlog.write('packet left SM at'+clock+'\n')
    return TransQueue.pop(0)

#Transmitter
def transmittertx(clock):
    if len(TransQueue)>=1:
        Tx=dequeuetq(clock)
        txclock.append(clock)
        return Tx
    else:
        return 0

#Receiver
def receiverrx(packet,clock):
    Rxclock.append(clock)
    choice = ['receive', 'drop']
    Prob = [0.5, 0.5]
    decision = np.random.choice(choice, p=Prob)
    #To send packets meant for the correct address
    if decision == 'receive':
        if len(ReceiveBuffer)<3: #To drop packets if the receiver queue is full
            ReceiveBuffer.append(packet)
            rxclock = str(clock+12.208*10**-6)
            logstr='Packet received from MM at'+ rxclock+'\n'
            receivelog.write(logstr)
        else:
            receiverDrop.append(1)
            packetentertime.pop()
        return 'Correct address'
    else:
        return 'Incorrect address'

#Receiver packet processor
def receivepp(r,clock):
    message=''
    for i in range(r): #to join 'r' frames together
        message=message+str(ReceiveBuffer.pop(0))
        receiveCount.append(1)
        packetexittime.append(clock)

#Mac Module
def mac(clock, framenumber, messagenumber):
    while Internetpackettime[0]<clock:
        Internetpackettime.pop(0)
        message = bytearray(1526)
        message.zfill(1526)
        Internetpackets.append(message)
    if len(TransQueue)== len(Internetpackets): #to calculate probaility Pr
        Pr = 0.5
    else:
        Pr=len(Internetpackets)/(len(TransQueue)+len(Internetpackets))
    choice = ['busy','idle']
    probability = [Pr,1-Pr]
    decision = np.random.choice(choice,p=probability) #to switch modes based on Pr
    if decision == 'idle': #to receive packets from Send Module and send to internet if packets are available
        packet.append(transmittertx(clock))
        if packet[0] == 0:
            packet.pop(0)
        else:
            macclock = str(clock+12.8*10**-6)
            logstr = 'Packet received from SM at'+ macclock+'\n'
            maclog.write(logstr)
            packet.__delitem__(0)
            if framenumber == numberofframes[messagenumber]:
                messageexittime.append(macclock)
                messagenumber += 1
                framenumber = 1
            else:
                framenumber += 1
                
            
    else: #to receive packets from internet and send to Receiver Module if packets are available
        if len(Internetpackets) > 0:
            packet.append(Internetpackets.pop(0))
            addr = receiverrx(packet,clock)
            if addr == 'Correct address':
                logstr = 'Packet sent to RM with '+addr+ 'at'+ str(clock) + '\n'
                packetentertime.append(clock)
            else:
                logstr = 'Packet sent to RM with '+addr+ 'at'+ str(clock) + '\n'
            maclog.write(logstr)
            packet.pop(0)

    return framenumber, messagenumber

if __name__ == '__main__':
    clock = 0
    SimulationTime= abs(int(raw_input('Please enter desired simulation time in seconds: ')))
    lamd = abs(int(raw_input('Please enter the mean number of messages per second for Send module:')))
    lamd2 = abs(int(raw_input('Please enter the mean number of messages per second for Internet:')))
    PQSize = abs(int(raw_input('Enter Packet Processor Queue size in KB:')))
    if PQSize<64:
        PQSize = 64
    if PQSize>448:
        PQSize = 448
    if SimulationTime <1:
        SimulationTime = 1
    PQSize = PQSize*1000
    TQSize = 512000-PQSize
    Interarrivaltime = [random.expovariate(lamd) for i in range(lamd*SimulationTime)]
    Internetarrivaltime = [random.expovariate(lamd2) for i in range(lamd2*SimulationTime)]
    Internetpackettime=[]
    Internettime = 0
    delayrm = []
    delay = []

    messagenumber = 0
    framenumber = 1

    for i in range(len(Internetarrivaltime)):
        Internettime = Internettime+Internetarrivaltime[i]
        Internetpackettime.append(Internettime)
    if Internettime<SimulationTime:
        Internetpackettime.append(SimulationTime+0.1)
    Timeforeachpacket = []
    totaltime = 0
    pptime = 0
    mactime = 0
    rptime = 0
    clockincrement = 10**-6
    for i in range(len(Interarrivaltime)):
        totaltime = totaltime+Interarrivaltime[i]
        Timeforeachpacket.append(totaltime)
    if totaltime<SimulationTime:
        Timeforeachpacket.append(SimulationTime+0.1)
    while clock<=SimulationTime: #loop to iterate over the desired Simulation time
        clock += clockincrement
        if len(Timeforeachpacket)>0:
            while Timeforeachpacket[0]<clock: #handling the arriving messages
                Timeforeachpacket.pop(0)
                lenofMessage = int(np.random.exponential(32000)) #to achieve Ls=32KB
                if lenofMessage == 0:
                    lenofMessage = 32000
                message = bin(random.getrandbits(lenofMessage*8))
                message = message[2:]
                messagepptime = len(message)*2*10**-9
                if pptime <= 0: #check if pp is free and send message to pp or packet queue accordingly
                    packetprocessor(message)
                    Messageentertime.append(clock)
                    tppclock.append(clock)
                    pptime += messagepptime
                else:
                    enqueuepq(message)

        
        if pptime>0:
            pptime = pptime-clockincrement
            if 256000-(len(TransQueue)*1526) < 1526: #making pp wait for TQ to be free
                pptime = pptime+clockincrement
            if pptime <= 0: #to make pp process a message from queue
                if len(PackProcQueue)>0:
                    msg = dequeuepq()
                    packetprocessor(msg)
                    tppclock.append(clock)
                    msgpptime = len(msg)*2*10**-9
                    pptime += msgpptime

        if mactime<=0: #to run MM
            framenumber, messagenumber = mac(clock, framenumber, messagenumber)
            mactime = 12.8*10**-6
        else:
            mactime = mactime-clockincrement

        if rptime <= 0: #to run Receiver processor
            if len(ReceiveBuffer)>0:
                r=random.randint(1,3)
                if len(ReceiveBuffer) < r:
                    rptime += clockincrement
                else:
                    receivepp(r,clock)
                    rppclock.append(clock)
                    rptime += r*61.04*10**-6
        if rptime>0:
            rptime -= clockincrement
    for i in range(len(messageexittime)):
        delay.append(float(messageexittime[i])-Messageentertime[i])
    for i in range(len(packetexittime)):
        delayrm.append(float(packetexittime[i]-packetentertime[i]))
    Rpprate = float((rppclock[len(rppclock)-1]-rppclock[0]))/float((len(Rxclock))*1526*8)
    Tpprate = float((tppclock[len(tppclock)-1]-tppclock[0]))/float((len(txclock)+len(TransQueue))*1526*8)
    Txthroughput = float(len(txclock)*1526*8)/float(txclock[len(txclock)-1]-txclock[0])
    Rxthroughput = float(len(Rxclock)*1526*8)/float(Rxclock[len(Rxclock)-1]-Rxclock[0])
    Packetloss = float(len(receiverDrop))/float(len(receiverDrop)+len(receiveCount)+len(ReceiveBuffer))
    Messageloss = float(len(PPDrop))/float(len(Interarrivaltime))
    print 'Rpp processing rate is: ',Rpprate*10**9,'ns/bit'
    print 'Tpp processing rate is: ',Tpprate*10**9,'ns/bit'
    print 'Tx throughput is: ',Txthroughput*10**-6,'Mbps'
    print 'Rx throughput is: ',Rxthroughput*10**-6,'Mbps'
    print 'Packet loss at Receiver is: ',Packetloss*100,'%'
    print 'Message loss at Packet Queue is: ',Messageloss*100,'%'
    print 'Average delay in NIC for each message processed in send module is: ',(np.mean(delay))*10**6,'microseconds'
    print 'Average delay in NIC for each packet processed in RM is: ',(np.mean(delayrm)*10**6),'microseconds'
