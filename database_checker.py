
import os.path
import pickle
from datetime import datetime

filename = 'datastorage'
if os.path.isfile(filename):
    print(f'Existing dataset found.\nOpening {filename} ...')
    with open(filename, 'rb') as data_json:
        data_dict = pickle.load(data_json)
        print('File imported.')
else:
    print('Dataset not found ...')


def show_last_seen():  # prints last seen moments of targets
    print('-------------------------------------')
    for name, value in data_dict.items():
        if type(value['last_seen']) == datetime:
            last_seen_value = value['last_seen'].strftime("last seen at: %H:%M:%S on %d-%b-%Y ")
        else:
            last_seen_value = 'not scanned before.'
        print('{name} was {lastseen}'.format(name=name, lastseen=last_seen_value))
    print('-------------------------------------')
    return


def who_is_home():
    print('Currently home:')
    for masterkey in data_dict.keys():
        if data_dict[masterkey].get('is_home'):
            print(f'{masterkey} is at home')
    print('-------------------------------------')


show_last_seen()
who_is_home()