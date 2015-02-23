"""
Author: Yuvarani Shankar
Date: 02/22/2014
Description: Client-Server architecture to perform file operations(read/update/delete) from the client side
"""
import socket
import sys
import json

"""
To read the content from from specified file, from specified offset
"""
def read(filename, offset, num_chars):
    data = ''
    try:
        fread_handler = open(filename, 'r')
        fread_handler.seek(offset) ## To read from particular offset
        if num_chars == -1:
            data = fread_handler.read() ## If no.of characters is not specified read the complete file
        else:
            data = fread_handler.read(num_chars) ## Read only the specified characters
        return data
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]
    finally:
        fread_handler.close()

"""
To read the data from end of the file
"""
def readE(filename,num_chars):
    try:
        fread_handler = open(filename, 'r')
        try:
            fread_handler.seek(-1*num_chars,2)
        except:
            fread_handler.seek(0) ## num_characters>total no.of characters in the file, read the complete file
        return fread_handler.read()
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]
    finally:
        fread_handler.close()
        
"""
To update the given content into the specified file
"""
def update(filename, data, start_offset, end_offset):
    try:
        file_handler = open(filename, 'r')
        prev_data  = file_handler.read(start_offset) ## Read the characters till the offset
        if end_offset>-1:
            file_handler.seek(end_offset) ## Ignore the characters from start and end offset and update it with the user specified data
        else:
            file_handler.seek(start_offset) 
        next_data = file_handler.read()
        file_handler = open(filename, 'w')
        file_handler.write(prev_data + data + next_data) ## Ignore the date between start and end offset, update it with the user specified data
        return "File updated successfully"
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]

"""
To update data at the end, Exactly like appending data to the file
"""
def updateE(filename, data):
    try:
        fwrite_handler = open(filename, 'a')
        fwrite_handler.write(data) ## Ignore the date between start and end offset, update it with the user specified data
        return "File updated successfully"
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]
    finally:
        fwrite_handler.close()

"""
To delete the content of the file from specified offset
"""
def delete(filename, start_offset, end_offset, num_chars):
    delete_all = 0
    try:
        file_handler = open(filename, 'r')
        prev_data = file_handler.read(start_offset)
        if end_offset!=-1: ## Delete characters from start and end_offset
            file_handler.seek(end_offset)
        elif num_chars!=0: ## Delete specifed no of chars from the start_offset
            file_handler.seek(start_offset+num_chars)
        elif start_offset == 0 and end_offset == -1 and num_chars == 0: ## Delete all the contents of the file
            delete_all = 1

        next_data = file_handler.read()
        file_handler = open(filename, 'w')
        if delete_all!=1: file_handler.write(prev_data + next_data) ## Remove only the user requested characters/between start and end offset
        elif delete_all == 1: file_handler.write("") ## Delete all the contents from the file, if the user has specified no offset or characters to be deleted
        return "Requested file contents deleted successfully"        
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]
    finally:
        file_handler.close()

"""
To delete characters from end of the file
"""
def deleteE(filename, num_chars):
    try:
        file_handler = open(filename, 'r')
        data = file_handler.read()
        file_handler.seek(0) ## as it as read data till the end, it is at the EOF now
        num_chars_to_read = len(data)-num_chars

        if num_chars_to_read>0: new_data = file_handler.read(num_chars_to_read)
        else: new_data = ''
        
        file_handler = open(filename, 'w')
        file_handler.write(new_data)  
        return "Requested file contents deleted successfully"
    
    except IOError as e:
        return "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        return "Unexpected error:", sys.exc_info()[0]
    finally:
        file_handler.close()
    
"""
Performs the user requested operation on the specified file (read/update/delete)
"""
def execute_command(func_name, func_args):
    try:
        try: fun = globals()[func_name]
        except: return "Requested operation is not supported at the server"       

        if func_args['filename']!=None: filename = func_args['filename']
        else: return "Speicify file name"
        
        if func_name == 'read': ## Read request
            offset = 0
            num_chars = -1

            if "offset" in func_args:
                if type(func_args['offset']) is not int: return "Invalid offset. Specify valid offset e.g offset: 4"
                offset = func_args['offset']

            if "num_chars" in func_args:
                if type(func_args['num_chars']) is not int: return "Invalid num_chars. Specify valid num_chars e.g num_chars: 4"
                num_chars = func_args['num_chars']

            if "end" in func_args and func_args['end'] == 1:
                if num_chars!= -1: return readE(filename,num_chars)
                else: return "Specify 'num_chars' to read contents from the end"

            return fun(filename, offset, num_chars)
        
        elif func_name == 'update': ## Update request, includes writing from begining of the file, writing from specified offset or modify the contents between the start and end offset
            start_offset = 0
            end_offset = -1
            data = ''

            if "data" in func_args: data = func_args['data']
            else: return "Specify data to be updated"

            if "start_offset" in func_args:
                if type(func_args['start_offset']) is not int: return "Invalid start_offset. Specify valid offset e.g start_offset: 4"
                start_offset = func_args['start_offset']
                
            if "end_offset" in func_args:
                if type(func_args['end_offset']) is not int: return "Invalid end_offset. Specify valid offset e.g end_offset: 4"
                end_offset = func_args['end_offset']
                
            if "end" in func_args and func_args['end']==1:
                if data!='': return updateE(filename,data)
                else: return "Specify 'data' to be appended to the file"
                
            if start_offset!= 0 and end_offset!=-1 and start_offset>end_offset:
                return "Specify valid start and end offset"
            
            return fun(filename, data, start_offset, end_offset)
        
        elif func_name == 'delete': ## Delete request
            start_offset = 0
            end_offset = -1
            num_chars = 0

            #if "end_offset" in func_args and "num_chars" in func_args: return "Specify either end_offset or num_chars but not both"

            if "start_offset" in func_args:
                if type(func_args['start_offset']) is not int: return "Invalid start_offset. Specify valid offset e.g start_offset: 4"
                start_offset = func_args['start_offset']

            if "end_offset" in func_args:
                if type(func_args['end_offset']) is not int: return "Invalid end_offset. Specify valid offset e.g end_offset: 4"
                end_offset = func_args['end_offset']            

            if "num_chars" in func_args:
                if type(func_args['num_chars']) is not int: return "Invalid num_chars. Specify valid num_chars e.g num_chars: 4"
                num_chars = func_args['num_chars']

            if "end" in func_args and func_args['end']==1:
                if num_chars!=-1: return deleteE(filename,num_chars)
                else: return "Specify 'num_chars' to delete contents from the end"

            if start_offset!= 0 and end_offset!=-1 and start_offset>end_offset:
                return "Specify valid start and end offset"
            
            return fun(filename, start_offset, end_offset, num_chars)
    except:
        return "Invalid request"

def is_json(json_data):
    try:
        json_object = json.loads(json_data)
    except ValueError, e:
        return False
    return True

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
uuid = "bfd99f05-befb-4b9d-8fd1-e5f517b30685"
while True:
    # Wait for a connection
    print >>sys.stderr, 'Waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'Connection from', client_address
        while 1:
            request = ''
            while 1: #reading the request from the client
                temp = connection.recv(1024)
                request+=temp
                if "EOReq" in temp: ## End of Request
                    request = request[:-5] ## To remove the end of data signal "##END##"
                    break
                
            print >>sys.stderr, 'Received "%s"' % request
            if(request == 'quit'): break
            print "Sending response.."
            if is_json(request)!=True: ## Not a valid json
                resp = '{"Request": "%s", "Response": "Invalid request format"}' %(request)
                resp = json.dumps(resp, indent = 1, encoding="utf8")
                print json.dumps(json.loads(resp), sort_keys=True, indent=1),"\n"
                resp+= "EOResp"
                connection.sendall(resp)
                continue
            
            decoded_command = json.loads(request)
            for func_name, func_args in decoded_command.iteritems():
                for arg in func_args:
                    response = execute_command(func_name, arg)
                    resp = '{"Request": "%s(%s)", "Response": "%s"}' %(func_name,func_args,response)
                    resp = json.dumps(resp, indent = 1, encoding="utf8")
                    print json.dumps(json.loads(resp), sort_keys=True, indent=1),"\n"
                    resp+="EOResp"
                    connection.sendall(resp)
            connection.sendall(uuid)
        connection.close()  
    finally:
        connection.close()
    
