
''' To Do'''

''' How to transmit video over connection'''

#TCP requires data in the form of a stream of bytes.


#Currently client sends request and server handles it.
#   choose device in client, limit to 480p, - use opencv


# since gui uses a process to check for events, to be able to interact with tkinter whilst
#opencv is recording(also a while loop), need multiprocessing
#or use opencv highgui as a gui

#\\\\	Client	\\\\

# send http requests to server
#   -send in form required by server
#   receive 'connection established etc'

#create ui
# show device in UI
# dropdown box for device,quality,port,server ip

#Variables:
#Select video device, quality, port, server ip.


#\\\\	Server:	\\\\\\\\
#Variables:
#Accept

#- Create TCP server.
#   - make server
#   - receive data - how?
#       - create socket that receives data stream
#       - use https requests/ requests.post
#   - performs specified method in the request.

#- Create sockets on start-up that are in a listening state

#- create a unique socket for each client connection in a child process/thread, when they connect.
