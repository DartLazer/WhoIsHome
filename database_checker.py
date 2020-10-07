from datetime import datetime
from main import import_database, config


def show_last_seen(my_data_dict):  # prints last seen moments of targets
    print('-------------------------------------')
    for name, value in my_data_dict.items():
        if type(value['last_seen']) == datetime:
            last_seen_value = value['last_seen'].strftime("last seen at: %H:%M:%S on %d-%b-%Y ")
        else:
            last_seen_value = 'not scanned before.'
        print('{name} was {lastseen}'.format(name=name, lastseen=last_seen_value))
    print('-------------------------------------')
    return


def who_is_home(my_data_dict):
    print('Currently home:')
    for masterkey in my_data_dict.keys():
        if my_data_dict[masterkey].get('is_home'):
            print(f'{masterkey} is at home')
    print('-------------------------------------')


def main():
    filename = config['GENERAL']['filename']  # data file path
    database_dict = import_database(filename)
    show_last_seen(database_dict)
    who_is_home(database_dict)


if __name__ == '__main__':
    main()
