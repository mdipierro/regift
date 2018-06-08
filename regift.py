import argparse
import time
import datetime
import os
import sys
import yaml
import json
import logging
import re
import os
import base64
from pyquery import PyQuery as pq
from jsmin import jsmin
from rcssmin import cssmin

### UTILITY FUNCTIONS

def which(program):
    """ locates the program on a Unix file syste """
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

JAVA = which('java')
KEYTOOL = which('keytool')

def decompile(apk):    
    return os.system('%s -Xmx512M -Dfile.encoding=utf-8 -Djava.awt.headless=true -jar "tools/jar/apktool.jar" d %s -f' % (JAVA, apk)) == 0

def compile(name, apk):
    return os.system('%s -Xmx512M -Dfile.encoding=utf-8 -Djava.awt.headless=true -jar "tools/jar/apktool.jar" b %s -o %s' % (JAVA, name, apk)) == 0

def make_keystore(name):
    return os.system('%s -genkey -v -keystore %s.keystore -alias %s -keyalg RSA -keysize 2048 -validity 10000' % (KEYTOOL, name, name)) == 0

def sign(apk, name):
    return os.system('jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore %s.keystore %s %s' % (name, apk, name)) == 0

def align(apk, apk2):
    #~/Library/Android/sdk/build-tools/24.0.3/zipalign
    return os.system('tools/osx/zipalign -v 4 %s %s' % (apk, apk2)) == 0

def get_config(config_filename):
    config = {}    
    if config_filename:
        if not os.path.exists(config_filename):
            logging.error('%s file does not exist' % config_filename)
            sys.exit(1)
        if config_filename.endswith('.json'):
            config = json.load(open(config_filename))
        elif config_filename.endswith('.yaml'):
            config = yaml.load(open(config_filename))
        else:
            logging.error('%s file type not supported' % config_filename)
            sys.exit(1)
    KEYS = ['app_name','description','author','email','url','package_url']
    for key in KEYS:
        if not key in config:
            config[key] = raw_input(key+':')
    return config


#############################################
# main build function
#############################################

def build(appname, config_filename):
    base = appname
    if base.endswith('.apk'):
        base = base[:-4]

    # decomple the default apk
    os.system('cp tools/apps/default.apk ./%s.apk' % base)
    assert decompile(base+'.apk')
    
    # gather user parameters
    config = get_config(config_filename)
    if not config.get('version'):
        now = datetime.datetime.now()    
        config['version'] = '%i.%.2i%.2i.%.2i%.2i' % (now.year, now.month, now.day, now.hour, now.minute)
    if not config.get('name'):
        config['name'] = config['app_name'].lower().replace(' ','')
    
    # modify it
    filenames = [base+'/AndroidManifest.xml', base+'/res/xml/config.xml', base+'/res/values/strings.xml']    
    for filename in filenames:
        data = open(filename,'rb').read()
        data = data.replace('HelloCordova', config['app_name'])
        data = data.replace('version="1.0.0"', 'version="%s"' % config['version'])
        data = data.replace('A sample Apache Cordova application that responds to the deviceready event.', config['description'])
        data = data.replace('dev@cordova.apache.org', config['email'])
        data = data.replace('http://cordova.io', config['url'])
        data = data.replace('Apache Cordova Team', config['author'])
        data = data.replace('http://127.0.0.1:8080/static/examples/package.json', config['package_url'])
        open(filename,'wb').write(data)

    a, b = 'io.cordova.hellocordova', 'io.cordova.'+config['name']
    c, d = 'Lio/cordova/hellocordova', 'Lio/cordova/'+config['name']
    for dirpath, dnames, fnames in os.walk(base):
        for f in fnames:
            filename = os.path.join(dirpath, f)
            data = open(filename,'rb').read()
            data1 = data.replace(a,b)
            data1 = data1.replace(c,d)
            if data1 != data:
                logging.info('modified: %s' % filename)
            open(filename, 'wb').write(data1)

    if os.path.exists(base+'/smali/io/cordova/hellocordova'):
        os.rename(base+'/smali/io/cordova/hellocordova', base+'/smali/io/cordova/'+config['name'])

    # recompile it
    target = base+'-signed.apk'
    assert compile(base, target)

    # sign it and generate keystore if necessary (prompts for passwd)
    if not os.path.exists('%s.keystore' % base):
        assert make_keystore(base)
    assert sign(target, base)

    # maybe re-align it
    tmp = target[:4]+'-aligned.apk'
    if align(target, tmp):
        os.rename(tmp, target)
    logging.info('done')

# logic for packaging

def encode_image(filename):
    extension = filename.split('.')[-1].lower()
    data = open(filename).read()
    if extension=='ttf':
        return 'data:font/ttf;base64,' + data
    if extension=='svg':
        return 'data:image/svg+xml;utf8,'+ data    
    else:
        return 'data:image/%s;base64,%s' % (extension, base64.b64encode(data))

def process_js(doc, assets):
    script = ''
    for item in doc('script'):        
        filename = item.get('src')
        if filename and '://' in filename:
            script += '/**** %s ****/\n' % filename
            code = '$("html").append(\'<script src="%s"></scrpt>\')' % filename
            script += code + '\n'
        elif filename:
            script += '/**** %s ****/\n' % filename
            code = open(filename).read()
            if code.count('\n')>1:
                code = jsmin(code)
            script += code + '\n'
        else:
            script += '/**** %s ****/\n' % 'inline'
            code = jsmin(item.text)
            script += code+'\n'
    return script

def process_css(doc, assets):
    regex = re.compile('url\([\'"]?(?P<url>.*?)[\'"]?\)')
    css = ''
    for item in doc('link[rel="stylesheet"]'):        
        filename = item.get('href')
        style = open(filename).read()
        css += '/**** %s ****/\n' % filename
        style = regex.sub(lambda g: "url('%s')" % encode_image(os.path.join(os.path.dirname(filename), g.group('url'))), style)
        code = cssmin(style)        
        css += code+'\n'
    return css

def process_html(doc, assets):
    images = doc('img[src]')
    for image in images:
        image.attrib['src'] = encode_image(image.get('src'))
    return doc('body').html()

#############################################
# main package function
#############################################

def package(filename):
    with open(filename) as myfile:
        doc = pq(myfile.read())
    assets = {}
    html = process_html(doc, assets)
    script = process_js(doc, assets)
    css = process_css(doc, assets)
    version = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
    package = {
        'version': version,
        'body': html,
        'script': script,
        'head': '<style>%s</style' % css,
        'assets': assets
        }
    with open('package.json','w') as myfile:
        json.dump(package, myfile)

#############################################
# main test web server
#############################################

def serve(folder):
    from bottle import Bottle, request, response, static_file, redirect
    bottle = Bottle()
    @bottle.route('/static/<path:path>')
    def static(path):
        """ exposes static pages """
        return static_file(path, folder)
    bottle.run(host='127.0.0.1', port=8080)

#############################################
# main 
#############################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', default=None, help='command to be executed')
    parser.add_argument('filename', default=None, help='file to process')
    parser.add_argument('-c', '--config_filename', help='input configuration (yaml/json)')
    args = parser.parse_args()
    if args.command == 'package':
        package(args.filename)
    elif args.command == 'build':
        build(args.filename, args.config_filename)
    elif args.command == 'serve':
        serve(args.filename)
    else:
        logging.error('command %s not supported. allowed command are "build" and "package"' % args.command)
        sys.exit(1)

if __name__ == '__main__':
    main()
