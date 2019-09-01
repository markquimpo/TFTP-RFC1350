TFTP RFC 1350 in TCP by Mark Quimpo


Files:

*Mage.txt
*README.txt
*TFTP_Client.py
*TFTP_Server.py


================================================================================
RUN:
================================================================================
Server:
$ python3 TFTP_Server.py -a 12000

Client:
RRQ:
$ python3 TFTP_Client.py -l 127.0.0.1 -g Mage.txt -a 12000

WRQ
$ python3 TFTP_Client.py -l 127.0.0.1 -p Mage.txt -a 12000 
================================================================================


NOTE:
I include the file Mage.txt so you can use that to test my program.
You can also use your files and and try multimedia as well.
As far I know, I think I completed the program and no error. 
There's some features that I did not implemented in RFC 1350 like the Timeout.
Other than that, everything is good.  Use the command line above in RUN part to
run the program.


FEATURES:
>Netascii mode
>Opcodes
    -ERRORS:
	[1] Unknown Transfer ID : -Only to execute this on TFTP_Server.py
	[2] File Not Found: Request, when There's no file found in the same directory.
	[3] File Already Exist: Server only, when there's a file exist, cannot upload new. 
>argparse
	-a for port
	-l for local host
	-g get file: ReadRequest
	-p put file: WriteRequest
>download(RRQ) and Upload(WRQ) 
	features: files and multimedia compatible. 





