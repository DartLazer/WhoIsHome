import configparser
import os

config = configparser.ConfigParser()


config['GENERAL'] = {'not_home_threshold': 15,
                     'internet_interface': 'eth0',
                     'arp_string': f'arp-scan --interface=',
                     'ip_subnet' : '192.168.2',
                     'ip_range_start': '1',
                     'ip_range_end' : '200',
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

config['TARGETS'] = {'Joe\'s Phone': 'AA:AA:AA:AA:AA:AA',
                     'Carol\'s Phone': 'AA:AA:AA:AA:AA:AA',
                     'Lisa': 'AA:AA:AA:AA:AA:AA',
                     'John\'s PC': 'AA:AA:AA:AA:AA:AA'}


if os.path.isfile('whoishome.cfg'):  # if configfile exists: open, else create new
    config.read('whoishome.cfg')
else:
    with open('whoishome.cfg', 'w') as configfile:
        config.write(configfile)
        print('Config file not found!!!\nDont worry, I\'m creating a new one for you right now.\n If the program doesn\'t run make sure you have the config '
              'file setup properly! Especially the internet interface!')