import argparse
import json
import os

from procurvefront.ConfigParser import ConfigParser
from procurvefront.Connection import Connection


def main():
    parser = argparse.ArgumentParser(description='Creates a backup of the ProCurve 2510G via telnet')
    parser.add_argument('-c', '--config', default='config.json', help='Config file which should be used')
    args = parser.parse_args()

    config_path = args.config
    if not os.path.isfile(config_path):
        raise FileNotFoundError('Config file ' + config_path + ' not found')

    with open(config_path) as file:
        config = json.load(file)

    switch_config = config['switch']
    backup_config = config['backup']
    connection = Connection(switch_config['host'], switch_config.get('port', 21), switch_config.get('password'))
    connection.connect()

    config = connection.get_config(backup_config.get('runningConfig', False))
    with open(backup_config.get('destination', 'switchConfig.bin'), 'w') as file:
        file.write(config)

    port_config_file = backup_config.get('portConfig')
    if port_config_file:
        # Parse the config file and create a port configuration in a readable format
        parser = ConfigParser(config)
        port_config = parser.create_port_config()
        final_data = {
            'ports': port_config,
            'vlans': parser.get_vlans_dict()
        }
        with open(port_config_file, 'w') as file:
            json.dump(final_data, file)


if __name__ == '__main__':
    main()
