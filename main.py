import pickle
import os.path
from datetime import datetime
import os
import configparser
import smtplib
from time import sleep

config = configparser.ConfigParser()
config['GENERAL'] = {'not_home_threshold': 15,
                     'internet_interface': 'eth0',
                     'arp_string': f'arp-scan --interface=',
                     'filename': 'datastorage'
                     }
config['EMAIL-SETTINGS'] = {'sender_address': 'from_address@mail.com',
                            'your_password': '####',
                            'to_address': 'to_address@mail.com',
                            'smtp_domain': 'smtp.gmail.com',
                            'smtp_port': 465}
config['EMAIL-MESSAGE'] = {
    'departure_mail_subject': '{target} just left home.',
    'departure_mail_body': 'Dear Sysadmin,\n\nThis email is to notify you that {target} has left home at {departure_time}.\n{target} was home '
                           'since {arrival_time}!\nWith regards,\nYour Raspberry Pi',
    'arrival_mail_subject': '{target} just arrived home.',
    'arrival_mail_body': 'Dear Sysadmin,\n\nThis email is to notify you that {target} has arrived home at {arrival_time}.\n\nWith regards,'
                         '\nYour Raspberry Pi'}

config['TARGETS'] = {'Rik': '192.168.2.2',
                     'Beau': '192.168.2.6',
                     'Lisa': '192.168.2.5',
                     'Riks PC': '192.168.2.1'}

if os.path.isfile('whoishome.cfg'):  # if configfile exists: open, else create new
    config.read('whoishome.cfg')
else:
    with open('whoishome.cfg', 'w') as configfile:
        config.write(configfile)
        print('config not found, creating new one.')


def scanner_setup():  # loads scanner settings from config file to be used later on
    scannerdict = {'internet_interface': config['GENERAL']['internet_interface'], 'arp_string': config['GENERAL']['arp_string']}
    return scannerdict


def import_database(my_filename):  # imports the database if it exists. else creates new one
    if os.path.isfile(my_filename):
        with open(my_filename, 'rb') as data_json:
            data_dict = pickle.load(data_json)
    else:
        print('Dataset not found ...\nCreating new dataset.')
        data_dict = {}
    return data_dict


def import_targets(my_config_dict):  # imports targets from the config file. If not found it warns the users and exits the program
    if not my_config_dict:
        print('No targets entered.\nPlease specify targets in cfg file')
        raise SystemExit
    my_target_dict = {}
    for target, ip in my_config_dict.items():
        my_target_dict[target.title()] = ip
    return my_target_dict


def init_dict(my_dict, my_targets, my_not_home_threshold):  # initializes the dictionary in case of a
    for target in my_targets.keys():
        if target not in my_dict.keys():
            my_dict[target] = {}
            my_dict[target]['last_seen'] = 'Not scanned yet.'
            my_dict[target]['arrival_time'] = 'Not scanned yet.'
            my_dict[target]['scans_missed_counter'] = my_not_home_threshold + 1
            my_dict[target]['is_home'] = False
    return my_dict


def add_to_dict(key, value, data_dict):  # functon writes to dictionary
    data_dict[key]['last_seen'] = value  # datetime when the target is last seen
    data_dict[key]['scans_missed_counter'] = 0
    return data_dict


def is_home_check(data_dict, my_not_home_threshold):
    for masterkey, value in data_dict.items():
        if value['scans_missed_counter'] == 0 and value['is_home'] is False:
            value['arrival_time'] = value['last_seen']
            value['is_home'] = True
            email_sender(masterkey, data_dict, config['EMAIL-MESSAGE']['arrival_mail_subject'], config['EMAIL-MESSAGE']['arrival_mail_body'])
        elif value['scans_missed_counter'] > my_not_home_threshold and value['is_home'] is True:
            value['is_home'] = False
            email_sender(masterkey, data_dict, config['EMAIL-MESSAGE']['departure_mail_subject'], config['EMAIL-MESSAGE']['departure_mail_body'])
    return data_dict


def email_sender(target, data_dict, my_subject, my_message):
    arrival_time = data_dict[target].get('arrival_time').strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = data_dict[target].get('last_seen').strftime("%H:%M:%S on %d-%b-%Y ")
    sender_address = config['EMAIL-SETTINGS']['sender_address']
    receiver_address = config['EMAIL-SETTINGS']['to_address']
    account_password = config['EMAIL-SETTINGS']['your_password']
    smtp_domain = config['EMAIL-SETTINGS']['smtp_domain']
    smtp_port = config['EMAIL-SETTINGS']['smtp_port']

    if data_dict[target]['is_home'] is True:
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


def write_file(my_dict, my_filename):  # writes datadict to pickle file
    with open(my_filename, 'wb') as data_write_pickle:
        pickle.dump(my_dict, data_write_pickle)


def scan_network(target_dictionary, data_dict, scanner_settings_dict):
    amount_targets = len(target_dictionary)
    found = 0
    if amount_targets > 0 and target_dictionary is not None:
        print('Scanning ' + str(amount_targets) + ' targets.')
        print('-------------------------------------')
        for name, ip in target_dictionary.items():
            result = os.popen(scanner_settings_dict['arp_string'] + scanner_settings_dict['internet_interface'] + ' ' + ip).read()[-12]
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
        raise SystemExit
    print('-------------------------------------')
    print(f'Scan completed.\nFound {found} out of {amount_targets} targets.')
    return data_dict


def main():
    not_home_threshold = int(config['GENERAL']['not_home_threshold'])  # amount of scans the target can miss before considered not home
    filename = config['GENERAL']['filename']  # data file path
    targets = import_targets(config['TARGETS'])  # imports the targets specified in the cfg file as a dictionary.
    scanner_settings = scanner_setup()  # imports the scanner settings (internet interface etc) from the cfg file
    imported_database = import_database(filename)  # imports the database file
    database_dict = init_dict(imported_database, targets, not_home_threshold)
    while True:
        database_dict = scan_network(targets, database_dict, scanner_settings)
        is_home_check(database_dict, not_home_threshold)
        write_file(database_dict, filename)
        sleep(60)


if __name__ == '__main__':
    main()
