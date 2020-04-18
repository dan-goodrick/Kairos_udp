#!/usr/bin/env python
import socket
from pprint import pprint
from datetime import date
import time
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, protocol, task

class Serve_UDP(DatagramProtocol):
    def __init__(self):
        self.datagram = None

    def return_msg(self):
        return self.datagram

    def datagramReceived(self, datagram, address):
        self.datagram = datagram
        self.transport.write(datagram, address)

class Client_UDP(protocol.DatagramProtocol):
    def __init__(self, host, port, reactor):
        self.host = host
        self.port = port
        self._reactor = reactor

    def startProtocol(self):
        self.transport.connect(self.host, self.port)

    def stopProtocol(self):
        #on disconnect
        self._reactor.listenUDP(0, self)

    def sendDatagram(self, datagram):
        # datagram = 'Hello world'.encode() #ntp_packet
        try:
            self.transport.write(datagram.encode(), (self.host, self.port))
            # print( "{:0.6f}".format(time.time()))
        except Exception as e:
            print(e)
            pass

    def datagramReceived(self, datagram, host):
        print('Datagram received: ', repr(datagram))
        pass

def get_checksum(string, num_digits=3):
    return abs(hash(string)) % (10 ** num_digits)

def valid_IP(ip):
    segs = ip.split('.')
    if len(segs) != 4:
        return False
    for seg in segs:
        if len(seg) > 3:
            return False
        if not seg.isnumeric():
            return False
        if int(seg) < 0  or int(seg) >= 256:
            return False
    return True

"""Asychronous Processing of received data"""
# not necessary for now
# def ProcessStreamingUDP(SelectedIP, SelectedName):
#     if valid_IP(SelectedIP):
#         strmoutSteering = djJAUSMLTForm.sldrExt(0).Position
#         strmoutThrottle = djJAUSMLTForm.sldrExt(2).Position
#         strmoutBrake = djJAUSMLTForm.sldrExt(1).Position
#         strmoutStateFlags[StateFlags.sfMotion] = OCUMotionEnable
#         msg = BuildStreamingUDP(0, SelectedName)
#         djJAUSMLTForm.wsckStreamingUDP.RemotePort = 7201
#         djJAUSMLTForm.wsckStreamingUDP.RemoteHost = SelectedIP
#         djJAUSMLTForm.wsckStreamingUDP.SendData(msg + vbCrLf)
#         djJAUSMLTForm.cfgEntry[25].Text = msg
#         djJAUSMLTForm.label[255].Caption = CStr(val(djJAUSMLTForm.label(255).Caption) + 1)

def ParseStreamingUDP(msg):
    #   Streaming Protocol Sample
    #   #|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX
    #   0   #                   Header
    #       |                   Delimiter
    #   1   1.0                 Message Version
    #   2   VEH_MHAFB1          Vehicle name
    #   3   CMD                 Command Message to Robotic Asset
    #   4   123                 Session ID
    #   5   45                  Message Sequence
    #   6   56837               Time stamp, ms from midnight
    #   7   0                   Steering Angle, Steering Wheel Centered
    #   8   0                   Throttle Percentage, 0%
    #   9   100                 Brake Percentage, 100%
    #   10  1                   Transmission state, 1=Park
    #   11  0                   Vehicle speed in mph
    #   12  Vehicle State       No Estop, No Pause, Enabled, Manual
    #   13  Vehicle Sequence    Not Initiating or shutting down, No Start, No Steering Cal, No Shifting
    #   14  Vehicle Mode        Progressive Steering, Progressive Braking, No Speed Control
    #   15  XXX                 Default Checksum
    parsed_UDP_msg = msg.split('|')
    # check that msg starts with a proper header character
    if parsed_UDP_msg[0] != '#':
        valid = False
    #verify checksum
    c,checksum = parsed_UDP_msg[15].split(',')
    if c == 'C':
        n = len(parsed_UDP_msg[15]) + 1#-n = start idx of checksum in msg
        chk = get_checksum(msg[:-n])
        if checksum.upper() == 'XXX' or chk == int(checksum):
            valid = True
        else:
            valid = False
    else:
        valid = False
    # populate the stream_in_dictionary
    strminDict = {}
    strminDict['Checksum'] = checksum
    strminDict['Version'] = parsed_UDP_msg[1]
    strminDict['Name'] = parsed_UDP_msg[2]
    strminDict['Type'] = parsed_UDP_msg[3]
    strminDict['Session'] = parsed_UDP_msg[4]
    strminDict['Sequence'] = parsed_UDP_msg[5]
    strminDict['TimeStamp'] = parsed_UDP_msg[6]

    # Get the steering command
    c,val = parsed_UDP_msg[7].split(',')
    if c == 'S':
        strminDict['Steering'] = int(val)
    else:
        valid = False

    # Get the throttle command
    c,val = parsed_UDP_msg[8].split(',')
    if c == 'A':
        strminDict['Throttle'] = int(val)
    else:
        valid = False

    # Get the break command
    c,val = parsed_UDP_msg[9].split(',')
    if c == 'B':
        strminDict['Brake'] = int(val)
    else:
        valid = False

    # Get the transission state (1=Parked)
    c,val = parsed_UDP_msg[10].split(',')
    if c == 'G':
        strminDict['Trans'] = int(val)
    else:
        valid = False

    # Get the velocity
    c,val = parsed_UDP_msg[11].split(',')
    if c == 'V':
        strminDict['Velocity'] = int(val)
    else:
        valid = False

    #break out the state parameters
    state_list = parsed_UDP_msg[12].split(',')
    if state_list.pop(0) == 'X':
        strminDict['State'] ={'Estop':state_list[0],
                              'Paused':state_list[1],
                              'Enable':state_list[2],
                              'Manual':state_list[3],
                              'L1':state_list[4],
                              'L2':state_list[5],
                              'Motion':state_list[6],
                              'Reserved7':state_list[7]}
    else:
        valid = False

    #break out the process parameters
    process_list = parsed_UDP_msg[13].split(',')
    if process_list.pop(0) == 'Y':
        strminDict['Process'] ={'Operation':process_list[0],
                                'Shutdown':process_list[1],
                                'Start':process_list[2],
                                'SteeringCal':process_list[3],
                                'TransShift':process_list[4],
                                'Reserved5':process_list[5],
                                'Reserved6':process_list[6],
                                'Reserved7':process_list[7]}
    else:
        valid = False

    #break out the mode parameters
    mode_list = parsed_UDP_msg[14].split(',')
    if mode_list.pop(0) == 'Z':
        strminDict['Mode'] ={'ProgressiveSteeringDisable':mode_list[0],
                             'ProgressiveBrakingDisable':mode_list[1],
                             'VelocityControlEnable':mode_list[2],
                             'Reserved3':mode_list[3],
                             'Reserved4':mode_list[4],
                             'Reserved5':mode_list[5],
                             'Reserved6':mode_list[6],
                             'Reserved7':mode_list[7]}
    else:
        valid = False
    strminDict['Valid'] = valid
    return strminDict

def BuildStreamingUDP(strmDict):
    #   Streaming Protocol Sample
    #   #|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX
    #   0   #                   Header
    #       |                   Delimiter
    #   1   1.0                 Message Version
    #   2   VEH_MHAFB1          Vehicle name
    #   3   CMD                 Command Message to Robotic Asset
    #   4   123                 Session ID
    #   5   45                  Message Sequence
    #   6   56837               Time stamp, ms from midnight
    #   7   0                   Steering Angle, Steering Wheel Centered
    #   8   0                   Throttle Percentage, 0%
    #   9   100                 Brake Percentage, 100%
    #   10  1                   Transmission state, 1=Park
    #   11  0                   Vehicle speed in mph
    #   12  Vehicle State       No Estop, No Pause, Enabled, Manual
    #   13  Vehicle Sequence    Not Initiating or shutting down, No Start, No Steering Cal, No Shifting
    #   14  Vehicle Mode        Progressive Steering, Progressive Braking, No Speed Control
    #   15  XXX                 Default Checksum

    TimeStamp = int((time.time() - time.mktime(date.today().timetuple()))*1000)
    msg = []
    msg.append('#') # Header
    msg.append('1.0') # Version
    msg.append(strmDict['Name']) # Vehicle Name
    msg.append(strmDict['Type']) # Message Type
    msg.append(str(strmDict['Session'])) #Session ID
    msg.append(str(strmDict['Sequence'])) #Message Number
    msg.append(str(TimeStamp))
    msg.append(','.join(['S', str(strmDict['Steering'])]))
    msg.append(','.join(['A', str(strmDict['Throttle'])]))
    msg.append(','.join(['B', str(strmDict['Brake'])]))
    msg.append(','.join(['G', str(strmDict['Trans'])]))
    msg.append(','.join(['V', str(strmDict['Velocity'])]))
    msg.append(','.join(['X', str(strmDict['State_Estop']),
                              str(strmDict['State_Paused']),
                              str(strmDict['State_Manual']),
                              str(strmDict['State_Enable']),
                              str(strmDict['State_L1']),
                              str(strmDict['State_L2']),
                              str(strmDict['State_Motion']),
                              str(strmDict['State_Reserved7'])]))
    msg.append(','.join(['Y',str(strmDict['Process_Operation']),
                             str(strmDict['Process_Shutdown']),
                             str(strmDict['Process_Start']),
                             str(strmDict['Process_SteeringCal']),
                             str(strmDict['Process_TransShift']),
                             str(strmDict['Process_Reserved5']),
                             str(strmDict['Process_Reserved6']),
                             str(strmDict['Process_Reserved7'])]))
    msg.append(','.join(['Z',str(strmDict['Mode_ProgressiveSteeringDisable']),
                             str(strmDict['Mode_ProgressiveBrakingDisable']),
                             str(strmDict['Mode_VelocityControlEnable']),
                             str(strmDict['Mode_Reserved3']),
                             str(strmDict['Mode_Reserved4']),
                             str(strmDict['Mode_Reserved5']),
                             str(strmDict['Mode_Reserved6']),
                             str(strmDict['Mode_Reserved7'])]))
    chk = get_checksum('|'.join(msg))
    msg.append(','.join(['C',str(chk)]))
    return '|'.join(msg)

def main():

    # port = int(input('Enter port #: '))
    # if port < 1000 or port > 9000:
    #     print(f"{port} is not a valid port.  Exiting...")
    type = 0
    if not type:
        msg = '#|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX'
        strmDict = ParseStreamingUDP(msg)
    type = input("Enter a 1 to build a server or 2 to make a client")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 7201
    if type == '1':
        # if a server, how do I receive the message?  I can print it...
        reactor.listenUDP(port, Serve_UDP())
        reactor.run()
        strmDict = ParseStreamingUDP(msg)
        pprint(strmDict)
    elif type == '2':
        ip = input('Enter IP Address (xxx.xxx.xxx): ')
        if not valid_IP(ip):
            print(f"{ip} is not a valid ip.  Exiting...")
        protocol = Client_UDP(ip, port, reactor)
        t = reactor.listenUDP(0, protocol)
        msg = BuildStreamingUDP(0,'VEH_MHAFB1', strmDict)
        l = task.LoopingCall(protocol.sendDatagram(msg))
        l.start(1.0) # call every second
        reactor.run()
    else:
        print(f"{type} is not a valid option. Exiting...")

if __name__ == "__main__":
    msg = '#|1.0|VEH_MHAFB1|CMD|123|45|56837|S,0|A,0|B,100|G,1|V,0|X,0,1,0,0,0,,,|Y,0,0,0,0,0,,,|Z,0,0,0,,,,,|C,XXX'
    main()
