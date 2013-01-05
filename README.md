==================================
 Tizonia Static Website Generator
==================================

This tool generates the static website of the 
[Tizonia OpenMAX IL](http://tizonia.org "Tizonia OpenMAX IL") project.

Acknowledgements
================

This tool is based on TortoiseHg's website generation tool. The original
'thg-web' repository can be found on Bitbucket:
http://bitbucket.org/kuy/thg-web/


Requirements
============

To work on Tizonia website, you need to setup the environment.
The following requirements are mainly for maintainers, but if you
want to test translation before submitting, you also need.

- Python 2.6.4
- Django 1.1.1
- gettext utility


Structures
==========

templates
  Django template files.

static
  The static files to be copied to build directory.  'en' directory contains
  common files for all languages.  If you want to use language specific
  files instead of commons, you can create '<lang>' directory at the same
  hierarchy as 'en' directory.

locale
  Contains PO/MO files for developers/gettext.

build
  Will be created when you generate website using web.py tool.

README
  Yep, this file :)

web.py
  Tizonia website tool.  Run ``python web.py --help`` to see details.

Workflows
=========

For Translators
---------------

We are using Transifex as translation platform for Tizonia website:
https://www.transifex.net/projects/p/tizonia/c/web/

To translate the website, please follow this instructions.

Translate
^^^^^^^^^

1. Go to Tizonia project page on Transifex:
   https://www.transifex.net/projects/p/tizonia/c/web/
2. Select your language
3. Translate it
4. Submit translation

Here, you have two ways to translate messages:

A. Translate them on Transifex (recommended)
B. Download PO file from Transifex and translate it on local

If you choice A, you just click 'Submit translations' button at the bottom
of web-based editor on Transifex after translating.  Or you choice B, you
need to upload PO file to Transifex after translating.  In either way, 'Lock'
feature will be helpful to avoid translation conficts in case that more than
two translators contribute for one language.

Submitted translations will be pushed automatically to the correspinding
repository on GitHub by Transifex.  After that, maintainers re-generate
static website files for each language and upload them to hosting space.

Test Translation on Local
^^^^^^^^^^^^^^^^^^^^^^^^^

Probably, you want to test translated messages for the website before
submitting it to Transifex.  If so, please setup above environment first
and try this instructions:

1. Clone the 'tizonia-web-tool' repository to local from Bitbucket
2. Open command prompt and go to cloned repository root
3. Overwrite locale/<lang>/LC_MESSAGES/django.po file with your PO file
4. Run ``python web.py generate -l <lang>`` from command prompt
5. Open generated html files with the browser

Please DO NOT attempt to run ``python web.py update -l <lang>`` command.
This operation can instroduce new translatable strings and update your
PO file forcibly.  We recommend you to backup PO file before testing.


For Maintainers
---------------

First of all, you need to clone the 'tizonia-web-tool' repository from GitHub:
https://github.com/juanrubio/tizonia-web-tool


Update
^^^^^^

1. Update Django templates or static files in working copy
2. Run ``python web.py update --all``
3. Commit your changes with updated PO files
4. Push them to 'tizonia-web-tool' or send patches to maintainers

Next, you may need to generate website files and upload them to hosting
repository on GitHub.

1. Run ``python web.py generate --all`` to generate all websites
2. Confirm generated html files with the browser
3. Commit them to your local repository for hosting
4. Push a changeset to hosting repository on Bitbucket
