import yaml


CONFIG_PATH = './server/config.yaml'


def load_config():
    '''
    Loads config from CONFIG_PATH constant

    Returns:
        dict(): Loaded yaml.
    '''
    with open(CONFIG_PATH) as config_file:
        config = yaml.load(config_file, yaml.FullLoader)

    return config
