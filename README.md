Dependecy sudo apt install arp-scanner
run main.py as root (arp-scan requires root access for internet interface access)


Before running first time edit the CFG file.
  - file name reverse to the name of the 'database' storage file. (picke file) by default it will save to filename datastorage
  - Set internet adapter (ifconfig in command to get the correct name)
  - The not-home threshold refers to how many scans (by default script scans every minute) a client can miss before it is set to 'not home'. This is due to most apple         devices switch off Wi-Fi when in idle mode for a while and only occasionally come online. (in my experience settings this to 15-20 works fine.
  - set the from and to email address and password
  - set targets in the target section. Should be in format: name = (local_ip_address)
  
