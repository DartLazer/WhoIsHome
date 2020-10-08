import configparser

config = configparser.ConfigParser()
config['GENERAL'] = {'not_home_threshold': 15,
                     'internet_interface': 'enp0s3',
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

config['TARGETS'] = {'Rik': '192.168.2.4',
                     'Beau': '192.168.2.6',
                     'Lisa': '192.168.2.5',
                     'Riks PC': '192.168.2.1'}