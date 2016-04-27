import codecs
import os
import sys
import getopt
import json
from django.utils import simplejson

CUR_FOLDER = os.path.dirname(__file__)

def usage():
    print("Rekvizitka js module builder 1.0")

def read_file(path):
    with codecs.open(path, 'r', 'utf-8') as file:
        return file.read()

def read_json(path):
    content = read_file(path)
    return json.loads(content)

def parse_args():
    results = {"outdir" : CUR_FOLDER,
               "incdir" : CUR_FOLDER,
               "descr_name" : "descriptor.json",
               "locale" : "ru"}

    try:
        opts, args = getopt.getopt(sys.argv[1:], "I:o:hd:l:m:",
            ["help", "output=", "input=", "descr_name=", "locale=", "modules="])
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
            print("Invalid module descriptor: missed required parameter %s" % item)
            return False
    return True

def load_locale(args, locale, module_name, base_name):
    locale_dir = os.path.join(args['incdir'], 'locales')
    locale_path = os.path.join(locale_dir, locale + '.json')
    with codecs.open(locale_path, "r", "utf-8") as locale_file:
        return """
YUI.add("locales/%(module_name)s_%(locale)s",
    function(Y) {
    "use strict";
        if (!Y.Locales) {
            Y.Locales = {};
        }
        Y.Locales["%(base_name)s"] = %(locale_content)s;
    }
);""" % {'locale_content' : locale_file.read(),
          'locale' : locale,
          'module_name' : module_name,
          'base_name' : base_name}

def load_templates(args, templates, module_name, all_modules):
    if not len(templates):
        return ""
    template_dir = os.path.join(args['incdir'], 'templates')
    templates_list = []
    for template in templates:
        template_path = os.path.join(template_dir, template + '.html')
        with codecs.open(template_path, "r", "utf-8") as template_file:
            content = template_file.read()
            tmp = {'a' : content}
            tmp_str = simplejson.dumps(tmp)
            content = tmp_str[tmp_str.find(': "') + 3:-2]
            template_content = """    Y.TemplateStore.store("%(module_name)s_%(template_name)s",
    _.template("%(template_content)s"));
""" % {"module_name" : module_name,
       "template_name" : template,
       "template_content" : content}
            templates_list.append(template_content)
    return """
YUI.add('templates/%(module_name)s', function (Y) {
    "use strict";
%(content)s
}, '0.0.1', {requires:['template-store/%(ts_last_ver)s']});
""" % {'content' : u"\n".join(templates_list),
       'module_name' : module_name,
       'ts_last_ver' : get_latest_module_ver("template-store", all_modules)}

def build_css(args, css_files):
    css_list = []
    css_dir = os.path.join(args['incdir'], 'css')
    for css_file in css_files:
        file_path = os.path.join(css_dir, css_file + '.css')
        with codecs.open(file_path, "r", "utf-8") as file:
            content = file.read()
            css_list.append(content)

    return "\n".join(css_list)

def get_latest_module_ver(name, all_modules):
    versions = []
    for mod in all_modules.keys():
        if mod.startswith(name + '/'):
            versions.append(mod.split('/')[1])

    if len(versions):
        versions.sort()
        return versions[-1]
    return ""

def get_requirements(descr_data, all_modules):
    requirements = []
    if 'requires' in descr_data:
        for item in descr_data['requires']:
            if isinstance(item, basestring):
                name = item
                ver = get_latest_module_ver(name, all_modules)
                if ver:
                    requirements.append("%s/%s" % (name, ver))
                else:
                    requirements.append(item)
            else:
                name = item['name']
                ver = item['ver']
                requirements.append("%s/%s" % (name, ver))
    return requirements

def get_std_requirements(descr_data):
    requirements = []
    if 'std_requires' in descr_data:
        for item in descr_data['std_requires']:
            if isinstance(item, basestring):
                requirements.append(item)
            elif isinstance(item, dict):
                requirements.append(item['name'])
    return requirements

def make_dirs(outdir, module_name, locale, ver):
    dest_dir = os.path.join(outdir, locale)
    dest_dir = os.path.join(dest_dir, module_name + "%s")
    #dest_dirs = [(dest_dir, module_name)]
    dest_dirs = []
    if ver:
        dest_dir = os.path.join(dest_dir, ver)
        dest_dirs.append((dest_dir, module_name))
    return dest_dirs

def main():
    args = parse_args()

    mod_dir = args['modules']
    all_modules = read_json(os.path.join(mod_dir, "modules.json"))

    descr_path = os.path.join(args['incdir'], args["descr_name"])
    with codecs.open(descr_path, "r", "utf-8") as descr_file:
        descr_content = descr_file.read()

    descr_data = json.loads(descr_content)
    if not check_descriptor(descr_data):
        exit(-1)

    src_name = descr_data['name'] if 'src' not in descr_data else descr_data['src']
    src_name += ".js"

    src_path = os.path.join(args['incdir'], src_name)
    with codecs.open(src_path, "r", "utf-8") as src_file:
        src_content = src_file.read()

    locale = args['locale']
    has_locale = 'locales' in descr_data and len(descr_data['locales'])
    if has_locale:
        locales = descr_data['locales']

        if locale in locales:
            pass
        elif 'en' in locales:
            locale = 'en'
        elif len(locales):
            locale = locales[0]
        else:
            print("Can't find locale for module %s" % descr_data['name'])
            exit(-1)

    module_templates = ""
    if 'templates' in descr_data:
        module_templates = load_templates(args, descr_data['templates'], descr_data['name'], all_modules)
    has_templates = 'templates' in descr_data and len(descr_data['templates'])

    requirements = get_requirements(descr_data, all_modules)
    std_requirements = get_std_requirements(descr_data)
    module_version = ", '0.0.0'" if 'ver' not in descr_data else ", '%s'" % descr_data['ver']

    css = None
    if 'css' in descr_data:
        css = build_css(args, descr_data['css'])

    dest_dirs = make_dirs(args['outdir'], descr_data['name'], locale, descr_data.get('ver'))

    for dest_dir, mod_name in dest_dirs:

        req_modules = list(requirements)
        if has_locale:
            req_modules.append("locales/%(module_name)s_%(locale)s" % {'module_name' : mod_name, 'locale' : locale})
        if has_templates:
            req_modules.append("templates/%s" % mod_name)

        css_requirements = []
        if css:
            css_requirements.append(mod_name + "_css")

        if not os.path.exists(dest_dir % ""):
            os.makedirs(dest_dir % "")

        module_requires = ""
        if len(req_modules) + len(std_requirements) + len(css_requirements):
            module_requires = ", {requires : [%s]}" % ", ".join(["'%s'" % item for item in req_modules + std_requirements + css_requirements])

        module_full_name = mod_name
        if 'ver' in descr_data:
            module_full_name += "/" + descr_data['ver']

        module_src = "YUI.add('%(module_name)s', %(src_content)s%(module_version)s%(module_requires)s);" % {
            'module_name' : module_full_name,
            'src_content' : src_content,
            'module_version' : module_version,
            'module_requires' : module_requires
        }

        module_src = module_templates + module_src

        module_locale = load_locale(args, locale, mod_name, descr_data['name']) if has_locale else ""
        module_src = module_locale + module_src

        if css:
            css_dir = dest_dir % "_css"
            if not os.path.exists(css_dir):
                os.makedirs(css_dir)
            css_path = os.path.join(css_dir, mod_name + '.css')
            with codecs.open(css_path, 'w', 'utf-8') as css_outfile:
                css_outfile.write(css)

        js_path = os.path.join(dest_dir % "", mod_name + '.js')
        with codecs.open(js_path, 'w', 'utf-8') as js_outfile:
            js_outfile.write(module_src)

    # todo: add "header section" for js files (which may contain copyright info, etc
    print("%s - done" % descr_data['name'])

if __name__ == "__main__":
    main()
