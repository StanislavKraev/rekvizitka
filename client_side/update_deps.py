import codecs
from fnmatch import fnmatch
import os, os.path
import sys
import getopt
import json

CUR_FOLDER = os.path.dirname(__file__)

def usage():
    print("Rekvizitka js module dependency updater v1.0")

def parse_args():
    results = {"outdir" : CUR_FOLDER,
               "incdir" : CUR_FOLDER,
               "descr_name" : "descriptor.json"}

    try:
        opts, args = getopt.getopt(sys.argv[1:], "I:o:hd:", ["help", "output=", "input=", "descr_name="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            results['outdir'] = a
        elif o in ("-I", "--input"):
            results['incdir'] = a
        elif o in ("-d", "--descr_name"):
            results['descr_name'] = a
        else:
            assert False, "unhandled option"

    return results

def process_dep(dir, result):
    with codecs.open(dir, "r", "utf-8") as dep_file:
        dep_data = json.loads(dep_file.read())
        name = dep_data['name']
        requires = dep_data.get('requires')
        css = dep_data.get('css')
        ver = dep_data.get('ver')

        mod_name = name

        css_req = None
        if css and len(css):
            css_req = mod_name + "_css"

        base_name = mod_name
        if ver:
            mod_name += "/%s" % ver

        if mod_name not in result:
            result[mod_name] = {}
        data = result[mod_name]
        data["path"] = mod_name + "/" + name + '.js'

        if not requires and not css_req:
            if "requires" in data:
                del data['requires']
        else:
            data["requires"] = []
            if css_req:
                data["requires"].append(css_req)
            if requires:
                for req in requires:
                    if isinstance(req, basestring):
                        data["requires"].append(req)
                    else:
                        data["requires"].append("%s/%s" % (req["name"], req["ver"]))

        if css and len(css):
            css_req = base_name + "_css"
            if ver:
                css_req += "/%s" % ver
            result[css_req] = {'name' : css_req, 'path' : css_req + "/" + name + '.css', 'type' : 'css'}

        std_requires = dep_data.get('std_requires')
        if std_requires:
            for req in std_requires:
                if isinstance(req, dict):
                    if 'dynamic' in req and req['dynamic']:
                        result[req['name']] = {'name' : req['name'], 'path' : req['path'], 'dynamic' : req['dynamic']}
                        data["requires"].append(req['name'])

def print_fnmatches(pattern, dir, files):
    for filename in files:
        if fnmatch(filename, pattern[0]):
            process_dep(os.path.join(dir, filename), pattern[1])

def load_deps(result, folder):
    os.path.walk(folder, print_fnmatches, ('descriptor.json', result))

def process_app_entry(pattern, dir, files):
    for filename in files:
        if fnmatch(filename, pattern[0]):
            process_app(os.path.join(dir, filename), pattern[1], pattern[2])

def load_apps(result, folder, main_data):
    os.path.walk(folder, process_app_entry, ('descriptor.json', result, main_data))

def get_dep_from_versioned_data(mod_name, main_data):
    for dep in main_data:
        try:
            name, ver = dep.split('/')
        except Exception:
            continue
        if name == mod_name:
            res = {name : {'ver' : ver}}
            item = main_data[dep]
            if 'type' in item and item['type'] == 'css':
                continue
            if 'requires' in item:
                res[name]['requires'] = item['requires']
            return res
    return None


def collect_all_deps(main_data, dep_data):
    deps = set(['main_portal'])
    unchecked = set(['main_portal'])
    for dep in dep_data['requires']:
        unchecked.add(dep)
        deps.add(dep)

    while len(unchecked):
        next = unchecked.pop()
        dep_obj = get_dep_from_versioned_data(next, main_data)
        if dep_obj:
            for req in dep_obj.values():
                if 'requires' in req:
                    for sub_req in req['requires']:
                        try:
                            name, ver = sub_req.split('/')
                        except Exception:
                            continue
                        if name not in deps:
                            deps.add(name)
                            unchecked.add(name)
    return filter(lambda x:x is not None, [get_dep_from_versioned_data(dep, main_data) for dep in deps])


def get_module_sum_ver(main_data, dep_data):
    all_deps = collect_all_deps(main_data, dep_data)
    sum_min = 0
    sum_maj = 0
    sum_mid = 0
    for dep in all_deps:
        for item in dep.values():
            ver = item['ver']
            maj, mid, min = ver.split('.')
            sum_maj += int(maj)
            sum_mid += int(mid)
            sum_min += int(min)
    return "%d.%d.%d" % (sum_maj, sum_mid, sum_min)

def process_app(dir, result, main_data):
    with codecs.open(dir, "r", "utf-8") as dep_file:
        dep_data = json.loads(dep_file.read())
        name = dep_data['name']
        ver = dep_data.get('ver')
        module_sum_ver = get_module_sum_ver(main_data, dep_data)

        result[name] = name + '-' + ver + '_' + module_sum_ver

def get_max_ver(name, main_data):
    versions = []
    for mod in main_data:
        if mod.startswith('%s/' % name):
            ver = mod.split('/')[1]
            versions.append(ver)


    if len(versions):
        versions.sort()
        return versions[-1]

    return ""

def update_requirements_max_ver(main_data, old_name, new_name):
    for mod_name, mod_data in main_data.items():
        if 'requires' not in mod_data:
            continue
        for i in xrange(len(mod_data['requires'])):
            test_name = mod_data['requires'][i]
            if test_name == old_name:
                mod_data['requires'][i] = new_name

def remove_old_versions(main_data):
    new_data = {}
    for mod_name in main_data:
        if mod_name.find('/') == -1:
            new_data[mod_name] = main_data[mod_name]
            continue
        name, ver = mod_name.split('/')
        max_ver = get_max_ver(name, main_data)
        if ver >= max_ver:
            new_data[mod_name] = main_data[mod_name]

    return new_data

def main():
    args = parse_args()
    main_path = os.path.join(args['outdir'], "modules.json")
    main_data = {}
    if os.path.exists(main_path):
        with codecs.open(main_path, "r", "utf-8") as main_file:
            main_content = main_file.read()

        main_data = json.loads(main_content)

    load_deps(main_data, args['incdir'])

    for mod_name, mod_data in main_data.items():
        if 'requires' not in mod_data:
            continue
        for mod_req in mod_data['requires']:
            if mod_req.find('/') == -1:
                max_ver = get_max_ver(mod_req, main_data)
                if len(max_ver):
                    update_requirements_max_ver(main_data, mod_req, "%s/%s" % (mod_req, max_ver))

    main_data = remove_old_versions(main_data)
    result = json.dumps(main_data)
    with codecs.open(main_path, 'w', 'utf-8') as out_file:
        out_file.write(result)

    apps_data = {}
    load_apps(apps_data, os.path.normpath(os.path.join(args['incdir'], '../apps')), main_data)
    apps_path = os.path.join(args['outdir'], "apps.json")
    with codecs.open(apps_path, 'w', 'utf-8') as out_file:
        out_file.write(json.dumps(apps_data))

    print("Done")

if __name__ == "__main__":
    main()

