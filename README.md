Welcome to my WhoIsHome scanner!
This tool scans your home network with the tool arp-scan (only dependecy).
***This tool requires ROOT priviliges because of ARP-SCAN***

****ABOUT THIS SCRIPT****
After completing a scan of the desired IP-Range (specified in the config file) it will tell you wether your targets (also specified in the cfg file) are at home or not.
A target is considered not at home if it misses more scans that the not_home_threshold (config file again). 
The reason I built it like this is because I discovered most Apple devices switch off Wi-Fi while not used for a while, and this way you prevent a lot of false not home triggers. 
In my experience setting this value between 15-20 scans (15-20 minutes) prevents most false positives.
At the moment the script is built this way so that when a target leaves- or comes home the specified email address in the config file will be sent an e-mail.
You could also replace this function (email-sender) with something else you desire, like switching on- or off lights. 
I built this as a project to expand my pyhton skills so any feedback is welcome. I will most likely improve on this project in the future.



**** INSTRUCTIONS ****
Install dependecy sudo apt install arp-scanner
Before running first time edit the CFG file.
  - file name reverse to the name of the 'database' storage file. (picke file) by default it will save to filename datastorage
  - Set internet adapter (ifconfig in command to get the correct name)
  - Set the ip-subrange (i.e. 192.168.2. (END WITH A DOT VERY IMPORTANT)
  - set the ip min and max (lets say you want to scan 192.168.2.1 until 192.168.2.100 you set ip min to 1 and ip max to 100)
  - The not-home threshold refers to how many scans (by default script scans every minute) a client can miss before it is set to 'not home'. This is due to most apple         devices switch off Wi-Fi when in idle mode for a while and only occasionally come online. (in my experience settings this to 15-20 works fine.
  - set the from and to email address and password
  - set targets in the target section. Should be in format: *name = macaddress(in AA:AA:AA:AA:AA:AA format)*
  - I run this program in the background with the following command: *sudo python3 main.py > /dev/null 2>&1 &*
  - The program should automatically e-mail you upon arrivals/depatures. But if you want to check the current database run the script: *database_checker.py* this script will give you a terminal print of the current database.
  
