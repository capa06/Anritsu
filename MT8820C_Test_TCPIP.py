# Sample MT8870A automation Python script for remote MT8870A control using sockets
# v0 - Juan Hidalgo (juan.hidalgo@anritsu.com) - Anritsu EMEA, Marketing
# Based on MD8475A automation by Patrick Chiang, Anritsu, parick.chiang@anritsu.com

from datetime import datetime
import time, socket, sys

## CONSTANTS ##
ip = "10.21.141.234" # Configure to IP Address of MT8820C
port = 56001 # MT8820C Phone 1 - use 56002 for Phone 2
terminator = "\n" # End of line character
SYST_LANG = "SCPI"

# Open socket connection to MT8820C
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) # Creates a socket
s.settimeout(120) # Sets timeout
s.connect((ip, port))
print("Connected to " + ip + ":" + str(port))

s.send("*IDN?\n")

l = True
while l == True:
    data = s.recv(100)
    print data, 'EOF'
    
    find_this = "\n"
    if find_this in data:
        l = False

print("End")