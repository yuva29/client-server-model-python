import socket
import sys
import uuid

"""
Author: Yuvarani Shankar
Date: 02/22/2014
Description: Client-Server architecture to perform file operations(read/update/delete) from the client side
"""

import json 

def is_json(json_data):
    try:
        json_object = json.loads(json_data)
    except ValueError, e:
        return False
    return True

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
uuid = "bfd99f05-befb-4b9d-8fd1-e5f517b30685"

try:
    while 1:
        request = raw_input("Command : ")
        try:
            sock.sendall(request+"EOReq")
            #unique_str = '{"key":"%s"}' % (str(uuid.uuid4()))
            #sock.sendall(unique_str)
            #sock.sendall("EOReq")
            if request == 'quit': break
        except:
            print "Invalid request for the server"
            continue
        data = ''
        while 1:
            temp = sock.recv(1024)
            data+=temp
            if "EOResp" in temp:
                data = data[:-6] ## To remove the end of data signal "##END##"
                if is_json(request)!=True:
                    print data
                    break
                else: print json.dumps(json.loads(data), sort_keys=True, indent=1),"\n"
                data = ''
            if uuid in temp:
                break
        
finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
