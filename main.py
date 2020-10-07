import pickle
import os.path
from datetime import datetime
import os
import configparser
import smtplib
from time import sleep

config = configparser.ConfigParser()
config['DEFAULT'] = {'not_home_threshold': 15,
                     'internet_interface': 'eth0',
                     'arp_string': f'arp-scan --interface=',
                     'filename': 'datastorage'
                     }
config['EMAIL'] = {'sender_address': 'rpiblocker3000@gmail.com',
                   'your_password': 'Iha3000vuCH.!$',
                   'to_address': 'rikietje@gmail.com',
                   'subject': 'new arrival',
                   'message': 'body',
                   'smtp_domain': 'smtp.gmail.com',
                   'smtp_port': 465}

if os.path.isfile('whoishome.cfg'):  # if configfile exists: open, else create new
    config.read('whoishome.cfg')
    print('config found')
else:
    with open('whoishome.cfg', 'w') as configfile:
        config.write(configfile)
        print('config not found')

internet_interface = config['DEFAULT']['internet_interface']  # network interface to be used. (find by command ifconfig)
arp_string = config['DEFAULT']['arp_string']  # scan executed by arp scan (sudo apt install arp-scan)
not_home_threshold = int(
    config['DEFAULT']['not_home_threshold'])  # amount of scans the target can miss before considered not home
filename = config['DEFAULT']['filename']  # data file path


def import_database():
    if os.path.isfile(filename):  # functions that checks if data file alraedy exists else write to filepath filename
        print(f'Existing dataset found.\nOpening {filename} ...')
        with open(filename, 'rb') as data_json:
            data_dict = pickle.load(data_json)  # imports dict(data_dict) from filename
            print('File imported.')
    else:
        print('Dataset not found ...\nCreating new dataset.')
        data_dict = {}  # if no file was found data(data_dict) can't be loaded thus it is created here
    return data_dict


def init_dict(my_dict, my_targets):
    if not my_dict:
        for target in my_targets.keys():
            my_dict[target] = {}
            my_dict[target]['last_seen'] = 'Not scanned yet.'
            my_dict[target]['arrival_time'] = 'Not scanned yet.'
            my_dict[target]['scans_missed_counter'] = not_home_threshold + 1
            my_dict[target]['is_home'] = False
        print('New dictionary initialized...')
        return my_dict
    print('Existing dictionary scanned...')
    return my_dict


def add_to_dict(key, value, data_dict):  # functon writes to dictionary
    data_dict[key]['last_seen'] = value  # datetime when the target is last seen
    data_dict[key]['scans_missed_counter'] = 0
    return data_dict


def is_home_check(data_dict):  # functions checks if timestamp list is empty. If empty target is not home.
    for masterkey, value in data_dict.items():  # Not responding to a scan results in 1 timestamp deletion in
        if value['scans_missed_counter'] == 0:
            if value['is_home'] == False:
                value['arrival_time'] = value['last_seen']
                arrived_home(masterkey, data_dict)
            value['is_home'] = True
        elif value['scans_missed_counter'] > not_home_threshold and value['is_home'] is True:
            print(f'{masterkey} left home')
            value['is_home'] = False
            departed_home(masterkey, data_dict)
    return data_dict


def arrived_home(target, data_dict):
    arrival_time = data_dict[target].get('arrival_time')
    print('sending email')
    sender_address = config['EMAIL']['sender_address']
    receiver_address = config['EMAIL']['to_address']
    account_password = config['EMAIL']['your_password']
    smtp_domain = config['EMAIL']['smtp_domain']
    smtp_port = config['EMAIL']['smtp_port']
    subject = f'{target} just got home.'
    body = f"Dear Sysadmin,\n\nThis email is to notify you that {target} has arrived home at {arrival_time}!\nWith regards,\nYour Raspberry Pi"
    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    smtp_server.login(sender_address, account_password)
    message = f"Subject: {subject}\n\n{body}"
    smtp_server.sendmail(sender_address, receiver_address, message)
    smtp_server.close()
    print('email sent')


def departed_home(target, data_dict):
    arrival_time = data_dict[target].get('arrival_time')
    departure_time = data_dict[target].get('last_seen')
    print('sending email')
    sender_address = config['EMAIL']['sender_address']
    receiver_address = config['EMAIL']['to_address']
    account_password = config['EMAIL']['your_password']
    smtp_domain = config['EMAIL']['smtp_domain']
    smtp_port = config['EMAIL']['smtp_port']
    subject = f'{target} just left home.'
    body = f"Dear Sysadmin,\n\nThis email is to notify you that {target} has left home at {departure_time}.\n{target} was home since {arrival_time}!\nWith regards," \
           f"\nYour Raspberry Pi"
    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    smtp_server.login(sender_address, account_password)
    message = f"Subject: {subject}\n\n{body}"
    smtp_server.sendmail(sender_address, receiver_address, message)
    smtp_server.close()
    print('email sent')


def write_file(my_dict):  # writes datadict to pickle file
    print(f'Writing results to "{filename}"')
    with open(filename, 'wb') as data_write_pickle:
        pickle.dump(my_dict, data_write_pickle)
        print('Data write successful.')


def scan_network(target_dictionary, data_dict):  # main function. initiates scan
    amount_targets = len(target_dictionary)
    found = 0
    if amount_targets > 0:
        print('Scanning ' + str(amount_targets) + ' targets.')
        print('-------------------------------------')
        for name, ip in target_dictionary.items():
            result = os.popen(arp_string + internet_interface + ' ' + ip).read()[-12]
            if result == '1':
                print(f'{name} is at home and connected.')
                found += 1
                time_found = datetime.now()
                data_dict.update(add_to_dict(name, time_found, data_dict))
            else:
                print(f'{name} is not connected.')
                data_dict[name]['scans_missed_counter'] += 1
    else:
        print('Cannot run tool without targets. Enter in the form of dictionary: Target name : Ip address.')
        return
    print('-------------------------------------')
    print(f'Scan completed.\nFound {found} out of {amount_targets} targets.')
    return data_dict


def main():
    targets = {'Rik': '192.168.2.4', 'Riks Ipad': '192.168.2.153', 'Lisa': '192.168.2.5', 'Beau': '192.168.2.6',
               'Riks Bitcoin Node': '192.168.2.2', 'Riks PC': '192.168.2.1'}

    imported_database = import_database()
    database_dict = init_dict(imported_database, targets, )
    while True:
        database_dict = scan_network(targets, database_dict)
        is_home_check(database_dict)
        write_file(database_dict)
        sleep(60)


if __name__ == '__main__':
    main()
