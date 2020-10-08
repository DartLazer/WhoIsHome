import os


def strip_string_to_target_data(string):
    stripped_string = string.split('\n')[2].split('\t')  # [0] = ip, [1] = MAC, [2] = device network name
    if stripped_string[0] == '':
        return None
    return stripped_string


def intruder_detection(scanned_dictionary, approved_list):
    for ip, value in scanned_dictionary.items():
        if value['MAC'] not in approved_list:
            print('New MAC ADDRESS detected: ')
            print('IP: {ip} MAC: {MAC} and device name {device}'.format(ip=ip, MAC=value['MAC'], device=value['Device-Name']))
            approved_list.append(value['MAC'])
    return approved_list


def scan_network(ip_subnet, ip_min, ip_max):
    online_hosts = {}
    raw_scan_output = os.popen('arp-scan --interface=enp0s3 --retry 5 ' + ip_subnet + ip_min + '-' + ip_subnet + ip_max).read()
    split_output = raw_scan_output.split('\n')[2:-5]
    for host in split_output:
        stripped_host = host.split('\t')
        online_hosts[stripped_host[0]] = {'MAC': stripped_host[1], 'Device-Name': stripped_host[2]}
    return online_hosts


def main():
    approved_mac_address = ['b8:27:eb:59:1d:96', 'dc:a6:32:5e:68:96', '80:b0:3d:79:44:0d', '86:62:a3:f3:2c:e0']
    found_hosts = scan_network('192.168.2.', '1', '200')
    print(found_hosts)


if __name__ == '__main__':
    main()
