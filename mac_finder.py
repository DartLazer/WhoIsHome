import os
import re


def find_mac(string):
    match = re.findall('([0-9a-fA-F]:?){12}', string)
    if match:
        return match
    return 'Not found'

def main():
    scanned = os.popen('arp-scan --interface=enp0s3 192.168.2.4').read()
    print(find_mac(scanned))
    print(scanned)


if __name__ == '__main__':
    main()
