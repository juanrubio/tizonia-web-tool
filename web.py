# encoding: utf-8
# Tizonia Website Tool

import os
import sys
import shutil
import urllib2
from optparse import OptionParser, OptionValueError
from datetime import date

# constants
LANGLIST = (('en', 'English'),
            )
LANGS = [L[0] for L in LANGLIST]
DOCLANGS = 'en'.split()
COMMANDS = ('generate', 'update', 'compile')
CURVER = 'http://tortoisehg.bitbucket.org/curversion.txt'
DESC = '''%prog COMMAND [OPTIONS]

Commands:
  generate: Generate Tizonia website after compiling PO files
  update:   Update PO files from Django templates (xgettext and msgmerge)
  compile:  Compile PO files and generate MO files (msgfmt)'''
FILES = ('index.html',
         'about.html',
         'docs.html',
         'download/index.html',
         'download/install_content.html',
         'download/install.html',
         'download/linux_content.html',
         'download/linux.html',
         )

# command-line parser
parser = OptionParser(usage=DESC)
parser.add_option('-l', '--lang', dest='lang', default='en',
                  help='generate website for LANG', metavar='LANG')
parser.add_option('-c', '--curver', dest='curver', default=CURVER,
                  help='curversion.txt file path')
parser.add_option('--all', dest='all', action='store_true', default=False,
                  help='generate website for all languages')

# check command-line options
opts, args = parser.parse_args(sys.argv)
if len(args) < 2:
    print >> sys.stderr, 'COMMAND is required to run'
    sys.exit(1)

subcmd = args[1]
if subcmd not in COMMANDS:
    print >> sys.stderr, 'Unknown command: %s' % subcmd
    sys.exit(1)

if opts.lang not in LANGS:
    print >> sys.stderr, 'Unsupported language: %s' % opts.lang
    sys.exit(1)

def parse_curver(curver):
    # fetch curversion.txt
    if curver.startswith('http://'):
        try:
            f = urllib2.urlopen(curver, timeout=3)
            lines = f.readlines()
            f.close()
        except urllib2.URLError:
            print >> sys.stderr, 'Failed to fetch curversion.txt, use -c option'
            return None
    else:
        f = open(curver, 'r')
        lines = f.readlines()
        f.close()

    # parse curversion.txt
    dl = {}
    obj = dict(version=lines[0].rstrip('\n'), dl=dl)
    lines = lines[1:]
    for line in lines:
        if line.startswith('dl/'):
            line = line[3:]
        parts = line.rstrip('\n').split(':', 1)
        if len(parts) == 1:
            continue
        dl[parts[0]] = parts[1]

    return obj

verobj = parse_curver(opts.curver)
if verobj is None:
    sys.exit(1)

# determine target languages
langs = opts.all and LANGS or (opts.lang,)

# Django settings
from django.conf import settings
root = os.path.dirname(os.path.realpath(__file__))
root_u = root.replace('\\', '/')
tmpl_u = os.path.join(root, 'templates').replace('\\', '/')
locale_u = os.path.join(root, 'locale').replace('\\', '/')
mids = ('django.middleware.common.CommonMiddleware',)
settings.configure(TEMPLATE_DEBUG=True, MIDDLEWARE_CLASSES=mids,
                   TEMPLATE_DIRS=(tmpl_u,), LOCALE_PATHS=(locale_u,))

def cmd_genenate():
    from django.template.loader import render_to_string
    from django.utils import translation

    # create output root dir
    output_root = os.path.join(root, 'build')
    if not os.path.exists(output_root):
        os.mkdir(output_root)

    def make_docver(ver, lang):
        nums = ver.split('.')
        if len(nums) == 2:
            nums = list(nums) + [0]
        if lang == 'en':
            return '.'.join(nums[0:2])
        else:
            return '%s-%s' % ('.'.join(nums[0:2]), lang)

    def prepare_dir(path):
        dir = os.path.dirname(path)
        if os.path.exists(dir):
            return
        prepare_dir(os.path.dirname(dir))
        os.mkdir(dir)

    # prepare global values for rendering context
    docdict = {}
    for lang in DOCLANGS:
        docdict[lang] = make_docver(verobj['version'], lang)

    # generate website
    for lang in langs:
        # activate target language
        translation.activate(lang)

        # create per-language dir
        output_dir = os.path.join(output_root, lang)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # copy static files
        static_root = os.path.join(root, 'static')
        static_en = os.path.join(static_root, 'en')
        shutil.copytree(static_en, output_dir)
        for rootdir, dirs, files in os.walk(os.path.join(static_root, lang)):
            if not files:
                continue
            for file in files:
                fullsrc = os.path.join(rootdir, file)
                relsrc = os.path.relpath(fullsrc, static_en)
                fulldst = os.path.join(output_dir, relsrc)
                shutil.copyfile(fullsrc, fulldst)

        # prepare common values for rendering context
        docdict['ver'] = docdict.has_key(lang) and docdict[lang] \
                                               or docdict['en']
        home = 'http://tizonia.org/' + (lang != 'en' and lang + '/' or '')
        langlist = [l for l in LANGLIST if l[0] != lang]
        langlabel = [l[1] for l in LANGLIST if l[0] == lang][0]
        langdict = dict(code=lang, list=langlist, label=langlabel)

        # generate files from templates
        for file in FILES:
            if file.endswith('.js'):
                file += '.tmpl'

            # render static content
            offset = '../' * (len(file.split('/')) - 1)
            ctx = dict(year=str(date.today().year), doc=docdict,
                       home=home, dir_offset=offset, lang=langdict,
                       dl=verobj['dl'], version=verobj['version'])
            rendered = render_to_string(file, ctx)

            # write out to file
            path = os.path.abspath(os.path.join(output_dir, file))
            prepare_dir(path)
            f = open(path, 'w')
            f.write(rendered.encode('utf-8'))
            f.close()

            orig, ext = os.path.splitext(path)
            if ext == '.tmpl':
                os.rename(path, orig)

def cmd_gettext(cmd):
    from django.core import management
    cmdline = ['django-admin.py', cmd]
    if cmd == 'makemessages':
        cmdline += ['-e', 'html,tmpl']
    cmdline.append('-l')
    for lang in [lang for lang in langs if lang != 'en']:
        management.execute_from_command_line(argv=cmdline + [lang])

# dispatch command
if subcmd == 'generate':
    cmd_gettext('compilemessages')
    cmd_genenate()
elif subcmd == 'update':
    cmd_gettext('makemessages')
elif subcmd == 'compile':
    cmd_gettext('compilemessages')
