__firm__ = "Terminal Labs"
__author__ = "Michael Verhulst"
__copyright__ = "© 2014 Michael Verhulst"
__license__ = "MIT License"
__version__ = "0.0.1"


import os
import io
import hashlib
import platform
import configparser
import inspect
import logging

logger = logging.getLogger('messaging')
initial_scan_logger = logging.getLogger('initial_scan_logger')

def str_to_file_obj(original_function):
    def intermediate_function(arg, in_mem=False):
        if type(arg).__name__  == 'str':
            if in_mem:
                file_obj = open_in_mem(arg, 'rb')
            else:
                file_obj = open(arg, 'rb')
    
        elif (type(arg).__name__  == 'BufferedReader' or
              type(arg).__name__  == 'BytesIO'):
            file_obj = arg

        file_obj.seek(0)
        result = original_function(file_obj, in_mem=in_mem)
        
        return result
    return intermediate_function


def open_in_mem(file_path, read_mode):
    file_obj = open(file_path, read_mode)
    file_contents = file_obj.read()
    file_obj = io.BytesIO()
    file_obj.write(file_contents)
    file_obj.seek(0)
    return file_obj


def list_file_paths(target_dir):
    file_paths = []
    for root, dirnames, filenames in os.walk(target_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            initial_scan_logger.info(file_path)
            file_paths.append(file_path)
            if os.path.islink(file_path):
                print(file_path)
    return file_paths


def list_public_attrs(obj):
    return sorted(
        [
            attr for attr in dir(obj)
            if not attr.startswith('_') and not inspect.ismethod(
                getattr(obj, attr)
            )
        ]
    )


def list_private_attrs(obj):
    return sorted(
        [
            attr for attr in dir(obj)
            if attr.startswith('_') and not inspect.ismethod(
                getattr(obj, attr)
            )
        ]
    )


@str_to_file_obj
def get_file_size(file_obj, in_mem=False):
    """
        Get size of huge files, without loading them in ram.
        Does not rely on the file size info stored in the files metadata.
    """
    file_obj.seek(0,2) # move the cursor to the end of the file
    size = file_obj.tell()
    return size


def get_file_type(file_path):
    assert os.path.isfile(file_path) == True, "file does not exist"
    return file_path.split('.')[-1]
    

@str_to_file_obj
def line_count(file_obj, in_mem=False):
    number_of_lines = 0
    while True:
        buf = file_obj.read(64336)
        if not buf:
            break
        number_of_lines =+ str(buf).count('\\n')

    return number_of_lines    


@str_to_file_obj
def file_is_empty(file_obj, in_mem=False):
    file_size = get_file_size(file_obj)
    assert file_size > -1, "file size can't be nagative"
    if file_size == 0:
        return True
    else:
        return False


@str_to_file_obj
def file_md5sum(file_obj, in_mem=False):
    if in_mem:
        return _mem_based_file_md5sum(file_obj)
    else:
        return _disk_based_file_md5sum(file_obj)


def _disk_based_file_md5sum(file_obj):
    hash_obj = hashlib.md5()
    while True:
        buf = file_obj.read(32768)
        if not buf:
            break
        hash_obj.update(buf)
    return hash_obj.hexdigest()


def _mem_based_file_md5sum(file_obj):
    hash_obj = hashlib.md5()
    buf = file_obj.read()
    hash_obj.update(buf)
    return hash_obj.hexdigest()


@str_to_file_obj
def file_is_only_whitespace(file_obj, in_mem=False):
    file_size = get_file_size(file_obj)

    if file_size > 0:
        for line in file_obj.readlines():
            if not line.isspace():
                return False
        return True 
    else:
        return False
    

def os_type():
    try:
        from sys import getwindowsversion
        running_on_windows = True
    except:
        running_on_windows = False

    if running_on_windows == True:
        if(getwindowsversion()[0] == 5 ):
            return 'xp'
        if(getwindowsversion()[0] == 6 ):
            return 'vista7'
    elif running_on_windows == False:
        if platform.system() == 'Linux':
             if platform.dist()[0] == 'Ubuntu':
                 return 'linux'
             if platform.dist()[0] == 'LinuxMint':
                 return 'linux'
        else:
            return 'mac'
    return 'unknown'


def package_name():
    return __name__.split('.')[0]


def get_user_home():
    return os.path.expanduser("~")


def get_hidden_conf_dir_path():
    home_dir = get_user_home()
    hiddden_dir_path = get_user_home() + '/.' + package_name()
    return hiddden_dir_path


def create_hidden_conf_dir():
    os.makedirs(get_hidden_conf_dir_path())


def get_hidden_conf_file_path():
    return get_hidden_conf_dir_path() + '/config.ini' 


def hidden_conf_dir_exists():
    return os.path.isdir(get_hidden_conf_dir_path())


def hidden_conf_file_exists():
    return os.path.isfile(get_hidden_conf_file_path())


def create_hidden_conf_file(defaults_conf_dict):
    cfgfile = open(get_hidden_conf_file_path(), 'w')
    config = configparser.ConfigParser()
    section_name = 'defaults'
    config.add_section(section_name)
   
    for key in defaults_conf_dict._attr_data_defaults.keys():
        config.set(section_name, key, defaults_conf_dict._attr_data_defaults[key])

    config.write(cfgfile)
    cfgfile.close()


def get_conf_dic(defaults_conf_dict):
    if hidden_conf_file_exists():
        config = configparser.ConfigParser()
        config.read(get_hidden_conf_file_path())
        return config_section_map(config)
    else:
        create_hidden_conf_file(defaults_conf_dict)
        return defaults_conf_dict


def config_section_map(config):
    section_name = 'defaults'
    dic = {}
    for option in config.options(section_name):
        dic[option.split('.')[0]] = config.get(section_name, option)
    return dic


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return dict(items())
