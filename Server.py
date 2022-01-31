from queue import *
import threading
import logging
import socketSendAndReceive
import Packet as packet

' Musings '
# Use cookie as a way of identification

' Plan of action'
# create Handler that creates a thread for each request     - CURRENT
#- placing stuff from buffer into their own lists
# create server ui

'Current'

#Play around with threading and see how to sort the packets

# might need to implement a pause function to impose fps
# might need to figure out how to update framecache while 'While' loop is running?
# might have to consider when thread deletes from ClientDict, then same thread runs before it is updated by the main

# KeyError 255: which is a lookup error in the dictionary for python, caused when While added? Some thread-sharing
#issues?
# might want to consider deleting the value at key value, not key itself to preserve thread.

#inserts integer 255 after first attempt at print(CLientdict[key[0]])
#why? max value of an 8-byte value

# after 'del' on first run-through, creates clientList key:value again, but key is now [255]?

# progression of key[0]
# '192.167.1.191 > [255] > 255 > error
#!!! related to being in the while loop, not updating?

# Thread(1):
    #while ProcessFrames():
        #CacheandClearDict()

# Error [255] occurs when CacheAndClearDict runs, deletes, then runs again before ClientDict is refilled.
# so the question is considering thread order and such

' Current'
# frames not displaying at fps between threads
#   fix time
#   how do we ensure there is sufficient pause between frames - a pause which also allows threads to switch.
#   sleep() function
#   make function to determine fps
#       say we sleep for difference in current time and desired break time - what if thread isn't immediatedly taken up?
#       thus how to solve when threads cannot keep up fps?
# work on threading and handling incoming packets
#   as long as frames are deposited/processed FIFO, we only need locks when appending to dictionary, since information
#only flows one way - tree


# In range(len(list)): can the list value change between iterations if list is modified?
# will need to check payloadAssembler with a bigger packet at some point


def request_handler():
    ''' Solution?
    # Buffer will be a global variable
    # Multiple threads can access it using a lock system of some sort, thus each thread will be doing the
    # 'sorting' per say, iterating through buffer to grab frames valid for it?
    '''

    # receive individual packet, with ip data

    # append each packet to a list defined by ip
    #create thread to deal with list defined by ip:
    #If list has to be created then spawn thread? Else, just append to list

    # maybe turn this into a bool state, then thread can be created in that file
    socketSendAndReceive.socketReceive()




# need to change file name?
if __name__ == "__main__":

    # set variables
    queue = Queue()
    format1 = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format1, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # spawn thread for request_handler
    x = threading.Thread(target=request_handler, args=())
    x.start()

    # spawn thread for tkinter gui
    #later

    # have button in the gui to stop listening - join() request_handler thread.
    #x.join()

# UI

#window = tk.Tk()

# add widgets here

#window.title('Hello Python')
#window.geometry("300x200+10+20")
#window.mainloop()


'later'
    #IIS on windows 10, app pools
    #iostream




''' //// TIMELINE /////

# need to find separate send/receive functions in scapy
#/send and sniff?
#/payload might not be in the right form - https://stackoverflow.com/questions/39225108/send-scapy-packets-through-raw-sockets-in-python
# OSError: [WinError 10057] A request to send or receive data was disallowed because the socket is not
#connected and (when sending on a datagram socket using a sendto call) no address was supplied

#send at layer 2/3 and how to receive? Does the sniffer sniff the receiving socket or?
# it seems sniffing happens on layer 2 - interface

# might have to create a sniffing thread
#0000 Ether / IP / UDP 192.168.1.160:57688 > 239.255.255.250:ssdp / Raw
#0000 Ether / IP / UDP 51.178.185.84:5152 > 192.168.1.160:5060 / Raw
#which implies we're not receiving on a dedicated port/socket?

# This is our packet - study this:
#<Sniffed: TCP:0 UDP:0 ICMP:0 Other:1>
# 00:00:40:11:39:7f > 45:00:00:24:00:01 (0x7f00) / Raw

# these look like mac addresses?
#/ thus being sent locally between 2 devices on same network - layer 2.
#*correct* was being sent at layer 2

# try fiddling with filters, starting with none to see if I'm receiving packets whatsoever
#/looks like mac address may still be being used despite send layer 3
#/removing filters means server doesn't flush buffer?

#Clearly not getting my packets, but other interesting ones:
#/57621 - spotify
# Lots of ipv6 packets sent to/from *pc* ipv6 address and default gateway, for domains open in chrome.
#/So we can see access to and from the default gateway to our PC, is there a way to sniff packets sent/received
#from default gateway on the other side?

# So we are not getting packets - fiddle with things:
#Possibilities: packet payload of the wrong form, packet header is of the wrong form, sent the wrong way. +?

#Diagonosing:
# Checking of client-side: definitely sending UDP; get summary -
# IP / UDP 127.0.0.1:10002 > 192.168.1.160:10003 / Raw
# Check integrity of payload:
# ip source/dest all correct, udp port all correct, payload is fine before sending client-side
# It is simply not getting there - issue with method of transport.

#
# have i bound the udp ports correctly? bind_layers()
# do i need to define the route taken?

# What am i trying to do? Simulate multiple clients with different source ip's on packets.
#/this can be done server-side after receiving IF modifying on client prior to sending screw up sending.
#/Test

#simply get it to send.
# same network so send via layer 2?
# or define sockets to help send

#does sniffer work on stuff coming from network loopback?
# test different ifaces
# test with python.socket to receive data on

#test with python.socket: try out differnt ifaces
# can we use two ports on same interface, or the rerouted to the loopback interface?
# tried with interface on client, maybe try changing server-side - sniff(), sniffs interfaces by default

# Sending from packet from same address to another port works with sockets, but not with scapy - common issue -
#but I'm not using loopback and sending to source address doesn't seem to be related.

#https://stackoverflow.com/questions/65466433/scapy-sniffed-udp-packets-can-not-be-received-after-sending-to-another-host
# use wireshark to determine what is actually happening
# It seems packet transferred from same address > different ports use for the loopback, thus running into
#problems with scapy.
#SO Wireshark now sees the packet being transferred, but scapy.sniff() doesn't see it - explore

#Server still doesn't receive - 'icmp protocol message - port unreachable'
# Socket not ready to receive on server end? Or invalid port number?

#try sending with scapy and receiving with socket
#YATTA! Can build a packet with specified source ip in scapy, and it is received with same source ip!!!

'''

#What were the nuances behind the cookie?
# since UDP is connectionless, we want a a way to record interaction with a client, thus rather than using IP,
#we can use this cookie for client identification
# So do we just use the value of the integer and compare to last values?
#what if packet are received out-of-order?
#what if multiple client connect at the time, thus having same cookie value?
# Solution - cookie made up of id integer and tracker value: cookie = (id, tracker)
#id value can be made as a random 2^32 value, with error catching clause if by chance 2 clients have the same value
#by comparing the tracker, number too, which happening simultaneously would only happen if client is used by *large*
#amount of people, with concentrated peak times.

#generate identity code when client starts program, which is then attached to each packet header cookie