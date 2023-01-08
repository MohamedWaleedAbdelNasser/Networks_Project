from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('', 8122))
tcpSerSock.listen(1)

try:
    while 1:
        # Start receiving data from the client
        print('\nReady to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('Received a connection from:', addr)
        message = tcpCliSock.recv(2048)
        print(message)

        empty = 0
        if message == b'':
            empty = 1
            print("Nothing typed.")
            break

        if message != b'':
            # Extract the filename, hostname, and URL from the given message
            filename = message.split()[1].decode("utf-8").rpartition("/")[2]
            hostn = message.split()[4].decode("utf-8")
            URL = message.split()[1].decode("utf-8")

        print("Hostname: " + hostn)
        print("Filename: " + filename)
        print("URL is: " + URL)

        # cache the file
        fileExist = "false"
        filetouse = './cache' + filename
        print(filetouse)

        # check if file is blocked or not in the list of blocked urls of the server
        URL_flag = 1
        with open('blocked_urls.txt') as f:
            for line in f:
                if URL in line:
                    print("URL is blocked!")
                    URL_flag = 0
                    break
                else:
                    URL_flag = 1
        if URL_flag == 0:
            break

        try:
            # Check whether the file exist in the cache
            f = open(filetouse[1:], "rb")
            outputdata = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n")
            for line in outputdata:
                tcpCliSock.send(line)
            f.close()

        # Error handling for file not found in cache
        except IOError:
            try:
                if fileExist == "false":
                    # Create a socket on the proxyserver
                    c = socket(AF_INET, SOCK_STREAM)
                    print(hostn)
                    c.connect((hostn, 80))
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobjwrite = c.makefile('w', None)
                    fileobjwrite.write("GET " + message.split()[1].decode("utf-8") + " HTTP/1.0\n\n")
                    fileobjwrite.close()
                    # read response
                    fileobj = c.makefile('rb', None)
                    buffer = fileobj.readlines()
                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                    File = open('./cache/' + filename, "wb+")
                    # Fill in start.
                    for line in buffer:
                        File.write(line)
                        tcpCliSock.send(line)
                    File.close()
                    c.close()
            except:
                print("Illegal request")
    else:
        # HTTP response message for file not found
        tcpCliSock.send(b"HTTP/1.0 404 sendError\r\n")
        tcpCliSock.send(b"Content-Type:text/html\r\n")
        # Close the client and the server sockets
        tcpCliSock.close()
        print("Sockets Closed")
except:
    print('Connection Closed')
    tcpCliSock.close()
    sys.exit()