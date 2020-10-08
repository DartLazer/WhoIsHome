import pickle
import os.path
from datetime import datetime
import os
import smtplib
from time import sleep
from config_file_creator import config


def scanner_setup():  # loads scanner settings from config file to be used later on in function scan_network
    scannerdict = {'internet_interface': config['GENERAL']['internet_interface'], 'arp_string': config['GENERAL']['arp_string']}
    return scannerdict


def print_banner():
    banner = '''
  _      __ __          ____       __ __                
 | | /| / // /  ___    /  _/___   / // /___   __ _  ___ 
 | |/ |/ // _ \/ _ \  _/ / (_-<  / _  // _ \ /  ' \/ -_)
 |__/|__//_//_/\___/ /___//___/ /_//_/ \___//_/_/_/\__/                                                                                                                 
'''
    print(banner)
    print('-------------------------------------------------------')


def import_database(my_filename):  # imports the database if it exists. else creates new one
    if os.path.isfile(my_filename):
        with open(my_filename, 'rb') as data_json:
            print('Database found.')
            data_dict = pickle.load(data_json)
    else:
        print('Dataset not found ...\nCreating new dataset.')
        data_dict = {}
    return data_dict


def import_targets(my_config_dict):  # imports targets from the config file. Targets are identified by their mac. characters separated by :
    if not my_config_dict:
        print('No targets entered.\nPlease specify targets in cfg file')
        raise SystemExit
    my_target_dict = {}
    for target, mac in my_config_dict.items():
        my_target_dict[target.title()] = mac.casefold()
    return my_target_dict


def init_dict(my_dict, my_targets, my_not_home_threshold):  # Initializes a new dictionary on first time run or adds new targets to an existing one.
    for target in my_targets.keys():
        if target not in my_dict.keys():
            my_dict[target] = {}
            my_dict[target]['last_seen'] = 'Not scanned yet.'
            my_dict[target]['arrival_time'] = 'Not scanned yet.'
            my_dict[target]['scans_missed_counter'] = my_not_home_threshold + 1
            my_dict[target]['is_home'] = False
    return my_dict


def update_database(key, value, data_dict):  # updates the database with the processed results from the last scan.
    data_dict[key]['last_seen'] = value
    data_dict[key]['scans_missed_counter'] = 0
    return data_dict


def email_sender(target, data_dict, my_subject, my_message):  # sends arrival/departure emails
    arrival_time = data_dict[target].get('arrival_time').strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = data_dict[target].get('last_seen').strftime("%H:%M:%S on %d-%b-%Y ")
    sender_address = config['EMAIL-SETTINGS']['sender_address']
    receiver_address = config['EMAIL-SETTINGS']['to_address']
    account_password = config['EMAIL-SETTINGS']['your_password']
    smtp_domain = config['EMAIL-SETTINGS']['smtp_domain']
    smtp_port = config['EMAIL-SETTINGS']['smtp_port']

    if data_dict[target]['is_home'] is True:  # if target is home formats the string according to the arrival email. Else depearture email
        subject = my_subject.format(target=target, arrival_time=arrival_time)
        body = my_message.format(target=target, arrival_time=arrival_time)
    else:
        subject = my_subject.format(target=target, departure_time=departure_time)
        body = my_message.format(target=target, departure_time=departure_time, arrival_time=arrival_time)

    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    smtp_server.login(sender_address, account_password)
    message = f"Subject: {subject}\n\n{body}"
    smtp_server.sendmail(sender_address, receiver_address, message)
    smtp_server.close()


def scan_network(ip_subnet, ip_min, ip_max, scanner_settings_dict):  # scans the network using arp-scan module. Performs a scan in the specified ip range
    print('Scanning ....')
    online_hosts = {}
    raw_scan_output = os.popen(scanner_settings_dict['arp_string'] + scanner_settings_dict['internet_interface'] + ' --retry 5 ' + ip_subnet + ip_min + '-' +
                               ip_subnet + ip_max).read()
    split_output = raw_scan_output.split('\n')[2:-5]  # Split command output by \n, index [2:-5] contains target data.
    for host in split_output:
        stripped_host = host.split('\t')  # split the target data by tabs which will give us device ip, mac and device name.
        online_hosts[stripped_host[1]] = {'IP': stripped_host[0], 'Device-Name': stripped_host[2]}  # add the found data to dictionary with MAC as key.
    return online_hosts


def is_home_check(data_dict, my_not_home_threshold):  # checks and if necessary alters the 'is_home' state of the target
    for masterkey, value in data_dict.items():
        if value['scans_missed_counter'] == 0 and value['is_home'] is False:  # if the target was away and now checks in again: target got home and send email
            value['arrival_time'] = value['last_seen']
            value['is_home'] = True
            email_sender(masterkey, data_dict, config['EMAIL-MESSAGE']['arrival_mail_subject'], config['EMAIL-MESSAGE']['arrival_mail_body'])
        elif value['scans_missed_counter'] > my_not_home_threshold and value['is_home'] is True: # not home threshold is # scans target can miss to prevent
            # unnecessary emails. However the actual departure time(last scan) time is saved and sent in email. So only the email is delayed
            value['is_home'] = False
            email_sender(masterkey, data_dict, config['EMAIL-MESSAGE']['departure_mail_subject'], config['EMAIL-MESSAGE']['departure_mail_body'])
    return data_dict


def scan_processor(scanned_dictionary, my_data_dict, my_targets): # scans the raw scan out. Checks if targets are in the found mac addresses.
    print('-------------------------------------------------------\nTargets found: ')
    for name, mac in my_targets.items():
        if mac in scanned_dictionary.keys():
            print(name)
            time_found = datetime.now()
            my_data_dict.update(update_database(name, time_found, my_data_dict))
        else:
            my_data_dict[name]['scans_missed_counter'] += 1
    print('-------------------------------------------------------')
    return my_data_dict


def write_file(my_dict, my_filename):  # writes datadict to pickle file
    with open(my_filename, 'wb') as data_write_pickle:
        pickle.dump(my_dict, data_write_pickle)


def main():
    print_banner()
    not_home_threshold = int(config['GENERAL']['not_home_threshold'])  # amount of scans the target can miss before considered not home
    filename = config['GENERAL']['filename']  # data file path
    targets = import_targets(config['TARGETS'])  # imports the targets specified in the cfg file as a dictionary.
    scanner_settings = scanner_setup()  # imports the scanner settings (internet interface etc) from the cfg file
    imported_database = import_database(filename)  # imports the database file
    database_dict = init_dict(imported_database, targets, not_home_threshold)
    while True:
        found_hosts = scan_network(config['GENERAL']['ip_subnet'], config['GENERAL']['ip_range_start'], config['GENERAL']['ip_range_end'], scanner_settings)
        database_dict = scan_processor(found_hosts, database_dict, targets)
        is_home_check(database_dict, not_home_threshold)
        write_file(database_dict, filename)
        print('sleeping')
        sleep(60)


if __name__ == '__main__':
    main()
