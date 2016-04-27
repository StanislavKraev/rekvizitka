import codecs
from copy import deepcopy
import os
import sys
import getopt
import json
from django.utils import simplejson

CUR_FOLDER = os.path.dirname(__file__)

def usage():
    print("Rekvizitka js application builder 1.0")

def parse_args():
    results = {"outdir" : CUR_FOLDER,
               "incdir" : CUR_FOLDER,
               "descr_name" : "descriptor.json",
               "locale" : "ru"}

    try:
        opts, args = getopt.getopt(sys.argv[1:], "I:o:hd:l:m:", ["help", "output=", "input=", "descr_name=", "locale=", "modules="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output_dir"):
            results['outdir'] = a
        elif o in ("-I", "--include_dir"):
            results['incdir'] = a
        elif o in ("-d", "--descr_name"):
            results['descr_name'] = a
        elif o in ("-l", "--locale"):
            results['locale'] = a
        elif o in ("-m", "--modules"):
            results['modules'] = a
        else:
            assert False, "unhandled option"

    if "modules" not in results:
        print("Missed requires parameter '--modules'")
        usage()
        sys.exit(2)

    return results

def check_descriptor(descriptor):
    required = ('name',)
    for item in required:
        if item not in descriptor:
            print("Invalid js application descriptor: missed required parameter %s" % item)
            return False
    return True

def plain_mod_list(requires, all_mods):
    result = {}
    for req in requires:
        if req in result:
            continue
        module_info = all_mods[req]
        item = {}
        result[req] = item
        if 'requires' in module_info:
            result.update(plain_mod_list(module_info['requires'], all_mods))
        item['path'] = module_info['path']
        if module_info.get('type') == 'css':
            item['type'] = 'css'

    return result

def build_dep_tree(modules):
    tree = {}

    for mod, descr in modules.items():
        item = {'name' : mod}
        tree[mod] = item
        if 'requires' in descr:
            item['requires'] = plain_mod_list(descr['requires'], modules)
        item['path'] = descr['path']
        if 'type' in descr:
            item['type'] = descr['type']
        if descr.get('dynamic'):
            item['dynamic'] = descr['dynamic']
    return tree

def get_latest_version(name, tree):
    versions = []
    for item in tree:
        if item.startswith(name + '/'):
            versions.append(item.split('/')[1])
    if len(versions):
        versions.sort()
        return name + '/' + versions[-1]
    return name

def build_app_deps(tree, descr_data):
    app_deps = {}
    css_deps = {}

    all_requires = descr_data['requires'] + ['main_portal']

    for req in all_requires:
        if req in app_deps or req in css_deps:
            continue

        latest_req = get_latest_version(req, tree)
        tree_item = tree[latest_req]
        item = {'path' : tree_item['path']}
        if tree_item.get('dynamic'):
            item['dynamic'] = tree_item['dynamic']

        if tree_item.get('type') == 'css':
            css_deps[latest_req] = item
        else:
            app_deps[latest_req] = item
            if 'requires' in tree_item:
                for sub_req in tree_item['requires']:
                    if sub_req in app_deps or sub_req in css_deps:
                        continue
                    tree_sub_item = tree[sub_req]

                    new_item = {'path' : tree_sub_item['path']}
                    if tree_sub_item.get('dynamic'):
                        new_item['dynamic'] = tree_sub_item['dynamic']

                    if tree_sub_item.get('type') == 'css':
                        css_deps[sub_req] = new_item
                    else:
                        app_deps[sub_req] = new_item

    return app_deps, css_deps

def concat_js(app_deps, mod_dir, locale):
    result = []
    for mod, descr in app_deps.items():
        if descr.get('dynamic'):
            continue
        mod_path = os.path.join(mod_dir, locale)
        mod_path = os.path.join(mod_path, descr['path'])
        with codecs.open(mod_path, 'r', 'utf-8') as mod_file:
            result.append(mod_file.read())
    return ''.join(result)

def concat_css(mod_dir, locale, css_deps):
    result = []
    for css_dep in css_deps.values():
        mod_path = os.path.join(mod_dir, locale)
        css_path = os.path.join(mod_path, css_dep['path'])

        with codecs.open(css_path, 'r', 'utf-8') as css_file:
            result.append(css_file.read())
    return ''.join(result)

def make_app(content, use_modules):
    result = ""
    return result

def get_std_requirements(descr_data):
    std_reqs = []
    if 'std_requires' in descr_data:
        for std_req in descr_data['std_requires']:
            std_reqs.append(std_req)
    return std_reqs


def save_file(path, content):
    with codecs.open(path, 'w', 'utf-8') as file:
        file.write(content)

def read_file(path):
    with codecs.open(path, 'r', 'utf-8') as file:
        return file.read()

def make_config(mod_json, dynamic_mod_json, ignore_modules):
    config = {
                'combine': True,
                'base' : "",
                'root' : "",
                'groups' : {
                    'rek' : {
                        'combine': True,
                        'comboBase': '/combo/?',
                        'root': '',
                        'modules': deepcopy(mod_json)
                    },
                    'dynamic' : {
                        'base' : "",
                        'root' : "",
                        'combine': False,
                        'comboBase': '',
                        'modules' : deepcopy(dynamic_mod_json)
                    }
                },
                'ignore' : ignore_modules
             }
    config_str = json.dumps(config)
    return """if (typeof(YUI_config) === "undefined") {
    var YUI_config = {};
}
$.extend(YUI_config, %(config)s);
""" % {'config' : config_str}

def read_json(path):
    content = read_file(path)
    return json.loads(content)

def get_jslint_assumes():
    return """/*global clearInterval: false, clearTimeout: false, document: false, event: false,
    frames: false, history: false, Image: false, location: false, name: false, navigator: false,
    Option: false, parent: false, screen: false, setInterval: false, setTimeout: false, alert : false,
    window: false, XMLHttpRequest: false, _: false, $: false, YUI: false, YUI_config:true, console:false, Backbone: false, jQuery: false, qq: false, Audio:false */
    """

def load_app_templates(templates_list, path, app_name):
    templates_content = ""
    res_templates_list = []
    req_mod_name = ""
    template_dir = os.path.join(path, 'templates')
    if templates_list and len(templates_list):
        for template in templates_list:
            template_path = os.path.join(template_dir, template + '.html')
            template_content = read_file(template_path)

            tmp = {'a' : template_content}
            tmp_str = simplejson.dumps(tmp)
            template_content = tmp_str[tmp_str.find(': "') + 3:-2]

            template_src = """    Y.TemplateStore.store("%(app_name)s_%(template_name)s",
    _.template("%(template_content)s"));
""" % {"app_name" : app_name,
       "template_name" : template,
       "template_content" : template_content}
            res_templates_list.append(template_src)

        req_mod_name = 'templates/%(app_name)s' % {'app_name' : app_name}
        templates_content = """
    YUI.add('%(req_mod_name)s', function (Y) {
    "use strict";
    %(content)s
    }, '0.0.1', {requires:['template-store']});
""" % {'content' : u"\n".join(res_templates_list),
       'req_mod_name' : req_mod_name}

    return templates_content, req_mod_name

def split_modules(all_modules):
    generals = {}
    dynamics = {}

    for module_name in all_modules:
        if 'dynamic' in all_modules[module_name]:
            dynamics[module_name] = all_modules[module_name]
        else:
            generals[module_name] = all_modules[module_name]

    return generals, dynamics

def main():
    args = parse_args()
    locale = args['locale']
    descr_path = os.path.join(args['incdir'], args["descr_name"])
    with codecs.open(descr_path, "r", "utf-8") as descr_file:
        descr_content = descr_file.read()

    descr_data = json.loads(descr_content)
    if not check_descriptor(descr_data):
        exit(-1)

    std_reqs = get_std_requirements(descr_data)

    source_file_name = (descr_data['src'] if 'src' in descr_data else descr_data['name']) + '.js'
    main_file_path = os.path.join(args['incdir'], source_file_name)

    main_css_content = ""
    if 'css' in descr_data:
        for css_item in descr_data['css']:
            css_dir_path = os.path.join(args['incdir'], 'css')
            css_file_path = os.path.join(css_dir_path, css_item + '.css')
            with codecs.open(css_file_path, 'r', 'utf-8') as css_file:
                main_css_content += css_file.read()

    mod_dir = args['modules']
    all_modules = read_json(os.path.join(mod_dir, "modules.json"))
    modules_json, dynamic_modules_json = split_modules(all_modules)

    tree = build_dep_tree(all_modules)
    app_deps, css_deps = build_app_deps(tree, descr_data)
    use_list = []
    if 'requires' in descr_data:
        for item in descr_data['requires']:
            if isinstance(item, basestring):
                use_list.append(item)
            else:
                use_list.append(item['name'])

    config = make_config(modules_json, dynamic_modules_json, css_deps.keys())

    locale_file = ""
    locale_req = ""
    if 'locales' in descr_data and locale in descr_data['locales']:
        locale_path = os.path.join(args['incdir'], 'locales')
        locale_path = os.path.join(locale_path, locale + '.json')
        locale_req = "locales/%(app_name)s_%(locale)s" % {'app_name' : descr_data['name'],
                                                          'locale' : locale}
        locale_file = """
YUI.add("%(locale_req)s", function(Y) {
    "use strict";
    if (!Y.Locales) {
        Y.Locales = {};
    }
    Y.Locales["%(app_name)s"] = %(locale_content)s;
});
""" % {'locale_content' : read_file(locale_path),
         'app_name' : descr_data['name'],
         'locale_req' : locale_req}

    app_js_content = read_file(main_file_path)
    reqs = std_reqs + use_list
    if locale_req:
        reqs.append(locale_req)

    template_content, template_req = load_app_templates(descr_data.get('templates'), args['incdir'], descr_data['name'])
    if template_req:
        reqs.append(template_req)

    main_content = make_app(app_js_content, reqs)

    concated_js = get_jslint_assumes() + config + template_content + locale_file + concat_js(app_deps, mod_dir, locale) + main_content
    concated_css = concat_css(mod_dir, locale, css_deps) + main_css_content

    app_path = os.path.join(args['outdir'], "%(app_name)s-%(version)s_%(locale)s.js" % {'app_name' : descr_data['name'],
                                                                                        'version' : descr_data['ver'],
                                                                                        'locale' : locale})

    app_css_path = os.path.join(args['outdir'], "%(app_name)s-%(version)s_%(locale)s.css" % {'app_name' : descr_data['name'],
                                                                                             'version' : descr_data['ver'],
                                                                                             'locale' : locale})
    save_file(app_path, concated_js)
    save_file(app_css_path, concated_css)

    print("%s - done" % descr_data['name'])
if __name__ == "__main__":
    main()
