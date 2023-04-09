from typing import List, Union
from types import SimpleNamespace
from shutil import copyfile, copytree
from pathlib import Path
import json, sys, os, colorama, zipfile, re, math
false, true = False, True

def get_size(start_path = '.'):
    if os.path.isdir(start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    else:
        return os.path.getsize(start_path)

def get_world_path():
    return os.path.join(config.server_path, 'worlds\\' + os.listdir(os.path.join(config.server_path, 'worlds'))[config.world_idx])

def json2obj(data: any) -> object:
    return dict2obj(json.loads(data, strict=false))

def dict2obj(d):
    if isinstance(d, list): d = [dict2obj(x) for x in d]
    if not isinstance(d, dict): return d

    class C: pass
    
    obj = C()
    for k in d: obj.__dict__[k] = dict2obj(d[k])
    
    return obj

class world_json_item:
    def __init__(self, uuid, version):
        self.pack_id = uuid
        self.version = version

class Addon:
    def __init__(self, path: str):
        self.setPath(path)

    def setPath(self, path: str):
        self.path = path
        self._get_manifest()
        self._get_type()
        self._get_enabled()
        self._get_name()
        self._get_size()
        self._get_is_dev()
    
    def _get_manifest(self):
        try:
            if os.path.isdir(self.path):
                files = os.listdir(self.path)
                if not 'manifest.json' in files:
                    raise Exception(f"Manifest file doesn't exist in folder at path: {self.path}"); return
                
                with open(os.path.join(self.path, 'manifest.json')) as file:
                    self.manifest = json2obj(file.read())
            else:
                with zipfile.ZipFile(self.path) as zf:
                    file_path = list(filter(lambda x: 'manifest.json' in x and 'bridge' not in x, zf.namelist()))[0]

                    # file_path = list(filter(lambda x: 'bridge' not in x, file_paths))[0]
                    
                    with zf.open(file_path) as file:
                        data = file.read().decode('utf-8')
                        self.manifest = json2obj(re.sub(r'\/\*(\*(?!\/)|[^*])*\*\/|\/\/.*', '', data, flags=re.MULTILINE))
        except Exception as e:
            print('EXCEPTION OCCURED WHILE GETTING ADDON MANIFEST FROM ADDON!')
            print("EXCEPTION MESSAGE:", e)
            print('HAPPENED AT PATH:', self.path)
            exit()

    def _get_pack_id_object(self):
        return world_json_item(self.manifest.header.uuid, self.manifest.header.version)
        
    def _get_enabled(self):
        self.enabled = true if len(list(filter(lambda x: x.pack_id == self.manifest.header.uuid, get_active_addons()))) > 0 else false

    def _get_type(self):
        self.type = 'behavior' if self.manifest.modules[0].type == 'data' else 'resource'

    def _get_name(self):
        self.name = self.manifest.header.name if self.manifest.header.name != 'pack.name' else self.path.split('\\')[-1].split('.')[0]
        
        for i, x in enumerate(self.name):
            if x == 'Â' or x == '§': self.name = self.name.replace((x + self.name[i + 1]) if i + 1 < len(self.name) else x, '')
    
    def _get_size(self):
        self.size = math.floor(get_size(self.path)/1024)

    def _get_is_dev(self):
        if self.path.split('\\')[-2] in ['development_behavior_packs', 'development_resource_packs']:
            self.dev = true
        else:
            self.dev = false

def get_addons() -> List[Addon]:
    ## exclude default addons
    exclusion_list: List[str] = [
        'chemistry',
        'vanilla',
        'experimental_next_major_update',
        'experimental_sniffer',
    ]
    
    rs_packs = os.path.join(config.server_path, 'resource_packs')
    bh_packs = os.path.join(config.server_path, 'behavior_packs')
    rs_dev_packs = os.path.join(config.server_path, 'development_resource_packs')
    bh_dev_packs = os.path.join(config.server_path, 'development_behavior_packs')

    lens = []
    addons:List[str] = list(filter(lambda x: x not in exclusion_list and not 'test_vanilla_' in x and not 'vanilla_' in x, os.listdir(rs_packs)))
    lens.append(len(addons))

    addons.extend(list(filter(lambda x: x not in exclusion_list and not 'test_vanilla_' in x and not 'vanilla_' in x, os.listdir((bh_packs)))))
    lens.append(len(addons) - lens[0])

    addons.extend(list(os.listdir(rs_dev_packs)))
    lens.append(len(addons) - lens[0] - lens[1])
    
    addons.extend(os.listdir(bh_dev_packs))
    lens.append(len(addons) - lens[0] - lens[1] - lens[2])

    idx = 0
    for i, x in enumerate(addons):
        res_path:str  = ''
        if lens[idx] <= 0:
            idx += 1

        match idx:
            case 0: res_path = rs_packs
            case 1: res_path = bh_packs
            case 2: res_path = rs_dev_packs
            case 3: res_path = bh_dev_packs
        addons[i] = os.path.join(res_path, x)
        lens[idx] -= 1
    return map(Addon, addons)

def get_active_addons(_type: str=None) -> List[world_json_item]:
    if _type == None:
        bh_path = os.path.join(get_world_path(), 'world_behavior_packs.json')
        rs_path = os.path.join(get_world_path(), 'world_resource_packs.json')
        res = []
        with open(bh_path) as bh_file:
            data = bh_file.read()
            res.extend(json2obj(data if len(data) >= 2 else '[]'))
        with open(rs_path) as rs_file:
            data = rs_file.read()
            res.extend(json2obj(data if len(data) >= 2 else '[]'))
        return res
    
    path = os.path.join(get_world_path(), f'world_{_type}_packs.json')
    res = []
    with open(path) as file:
        data = file.read()
        res.extend(json2obj(data if len(data)  >= 2 else '[]'))
    return res

def set_active_addons(_type: str, data: str) -> None:
    path = os.path.join(get_world_path(), f'world_{_type}_packs.json')
    with open(path, 'w') as file:
        file.write(data)

def disable_all():
    set_active_addons('resource', json.dumps([]))
    set_active_addons('behavior', json.dumps([]))

def enable_addon(uuid: str):
    addon = list(filter(lambda x: x.manifest.header.uuid == uuid, get_addons()))[0]

    if type(addon) != Addon:
        print('This addon doesn\'t seem to exist!')
    
    if addon.enabled:
        print('this addon is already enabled!')
        exit()
    
    data = get_active_addons(addon.type)
    data.append(world_json_item(addon.manifest.header.uuid, addon.manifest.header.version))
    res = []

    for x in data:
        value = dict()
        value['pack_id'] = x.pack_id
        value['version'] = x.version
        res.append(value)

    set_active_addons(addon.type, json.dumps(res))

def enable_all():
    addons = get_addons()
    for x in addons: 
        if not x.enabled: enable_addon(x.manifest.header.uuid)

def disable_addon(uuid: str):
    addon = next(filter(lambda x: x.manifest.header.uuid == uuid, get_addons()))
    if type(addon) != Addon:
        print('This addon doesn\'t seem to exist!')
    
    if not addon.enabled:
        print('this addon is already disabled!')
        exit()
    
    data = get_active_addons(addon.type)
    data.remove(next(filter(lambda x: x.pack_id == addon.manifest.header.uuid, data)))
    res = []

    for x in data:
        value = dict()
        value['pack_id'] = x.pack_id
        value['version'] = x.version
        res.append(value)

    set_active_addons(addon.type, json.dumps(res))

def list_addons(sort_by=None):
    
    addons: List[Addon] = list(get_addons())

    ## sort addons
    if sort_by == None:
        addons.sort(key=lambda x: x.enabled, reverse=true)
    else:
        if sort_by == 'name':
            addons.sort(key=lambda x: x.manifest.header.name, reverse=false)
        elif sort_by == 'type':
            addons.sort(key=lambda x: x.type)
        elif sort_by == 'name-enabled':
            addons.sort(key=lambda x: x.manifest.header.name, reverse=false)
            addons.sort(key=lambda x: x.enabled, reverse=true)
        elif sort_by == 'size':
            addons.sort(key=lambda x: x.size, reverse=true)

    ## print addons
    print(colorama.Fore.BLUE + f"IDX{' ' * 7}NAME{' ' * 63}TYPE{' ' * 15}UUID{' ' * 44}ENABLED{' '* 10}SIZE" + colorama.Fore.RESET)
    for i, x in enumerate(addons):
        idx_to_path_spacing = ' ' * (7 - len(str(i+1)))
        path_to_type_spacing = ' ' * ((59 - len(x.name)) if 59 - len(x.name) > 0 else 9)
        type_string = (colorama.Fore.LIGHTYELLOW_EX + x.type + colorama.Fore.RESET) if x.type == 'behavior' else (colorama.Fore.LIGHTCYAN_EX + x.type + colorama.Fore.RESET)
        enabled_string = (colorama.Fore.LIGHTMAGENTA_EX + ' DEV ' + colorama.Fore.RESET) if x.dev else colorama.Fore.RED + str(x.enabled).lower() + colorama.Fore.RESET if not x.enabled else colorama.Fore.GREEN + str(x.enabled).lower() + colorama.Fore.RESET

        ## IDX
        output = f"{i+1}{idx_to_path_spacing} | "
        ## NAME
        output += f"{''.join((char if i < 47 else '.' if i >= 47 and i < 50 else ' ') for i, char in enumerate(list(x.name)))}"
        ## TYPE
        output += f"{path_to_type_spacing}  |     {type_string}"
        ## UUID
        output += f"    |      {x.manifest.header.uuid}"
        ## ENABLED
        output += f'      |      {enabled_string}'
        file_size_spacing = ' ' * (6 - len(str(x.size) + 'kb') + 5)
        output += f"{' ' * 5 if x.enabled else ' ' * 4}|{file_size_spacing}{x.size}" + colorama.Fore.LIGHTBLACK_EX + ' kb' + colorama.Fore.RESET
        print(output)

class config:
    # delete_after_copy:bool = false
    server_path:str = r'C:\Users\kingx\Downloads\bedrock-server-1.19.72.01'
    world_idx:int = 0

def setup_config():
    config.server_path = input('server path: ')
    config.world_idx = input('world index (nth folder in server_path/worlds/): ')

    with open(os.path.join(__file__, '../config.json'), 'w') as config_file:
        value = dict()
        value['server_path'] = config.server_path
        value['world_idx'] = str(config.world_idx)
        config_file.write(json.dumps(value))

def load_config() -> bool:
    if not os.path.exists(os.path.join(__file__, '../config.json')):
        setup_config()
    else:
        with open(os.path.join(__file__, '../config.json')) as config_file:
            content = config_file.read()
            if len(content) < 3:
                return false

            data = json.loads(content)
            config.server_path = data['server_path']
            config.world_idx = int(data['world_idx'])

            return true

def display_help():
    output = '\nCOMMANDS\n\n'
    output += 'How to use: py main.py <command>\n\n'
    output += 'setup - run the setup function to update your config.json file\n\n'
    output += 'list or list <type/name/name-enabled> - returns a list of all commands in the server, active or inactive, or a list sorted by the given key\n\n'
    output += 'help - displays help\n\n'
    output += 'enable <uuid/all> - enables the addon with the given uuid or all addons\n\n'
    output += 'disable <uuid/all> - disables the addon with the given uuid or all addons\n\n'
    print(output)

if __name__ == '__main__':
    colorama.init()
    args = sys.argv[1:]

    if not load_config():
        setup_config()

    if not len(args) > 0:
        print('no args inputted, closing...')
        exit()

    match args[0]:
        case 'setup':
            setup_config()

        case 'help':
            display_help()

        case 'list':
            list_addons(args[1] if len(args) > 1 and args[1] in ['type', 'name', 'name-enabled', 'size'] else None)
            exit()
        
        case 'enable':
            if len(args) < 2:
                print('please put the addon uuid you want to enable!')
                exit()
            if args[1] == 'all':
                enable_all()
            else:
                enable_addon(args[1])
            exit()
        
        case 'disable':
            if len(args) < 2:
                print('please put the addon uuid you want to disable!')
                exit()
            if args[1] == 'all':
                disable_all()
            else:
                disable_addon(args[1])
            exit()

        case _:
            print('Unknown command!')
            display_help()
            exit()