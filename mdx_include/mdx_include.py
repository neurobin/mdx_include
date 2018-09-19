# -*- coding: utf-8 -*-
'''
Include Extension for Python-Markdown
===========================================

Includes local or remote files

See <https://github.com/neurobin/mdx_include> for documentation.

Copyright Md. Jahidul Hamid <jahidulhamid@yahoo.com>

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

'''
from __future__ import absolute_import
from __future__ import unicode_literals
import markdown
import re
import os
from codecs import open
import pkgutil
import encodings
import logging
try:
    # python 3
    from urllib.parse import urlparse
    from urllib.parse import urlunparse
    from urllib.request import build_opener
    from urllib.request import HTTPRedirectHandler
    from urllib.error import HTTPError
    from urllib.error import URLError
except ImportError:
    # python 2
    from urlparse import urlparse
    from urlparse import urlunparse
    from urllib2 import HTTPRedirectHandler
    from urllib2 import build_opener
    from urllib2 import HTTPError
    from urllib2 import URLError
from . import version

__version__ = version.__version__

INCLUDE_SYNTAX_RE = re.compile(r'\{!\s*(?P<path>.+?)\s*(\|\s*(?P<encoding>.+?)\s*)?!\}')

LOGGER_NAME = 'mdx_include' + __version__
log = logging.getLogger(LOGGER_NAME)

def encoding_exists(encoding):
    false_positives = set(["aliases"])
    found = set(name for imp, name, ispkg in pkgutil.iter_modules(encodings.__path__) if not ispkg)
    found.difference_update(false_positives)
    if encoding:
        if encoding in found:
            return True
        elif encoding.replace('-', '_') in found:
            return True
    return False

def get_remote_content(url, encoding='utf-8'):
    """Follow redirect and return the content"""
    try:
        log.info("Downloading url: "+ url)
        return build_opener(HTTPRedirectHandler).open(url).read().decode(encoding)
    except (URLError, HTTPError) as err:
        log.exception("E: Failed to download: " + url)
        return ''

class IncludeExtension(markdown.Extension):
    """Include Extension class for markdown"""

    def __init__(self,  *args, **kwargs):
        self.config = {
            'base_path': ['.', 'Base path from where relative paths are calculated'],
            'encoding': ['utf-8', 'Encoding of the files.'],
            }
        super(IncludeExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add( 'mdx_include', IncludePreprocessor(md, self.config),'_begin')


class IncludePreprocessor(markdown.preprocessors.Preprocessor):
    '''
    This provides an "include" function for Markdown. The syntax is {! file_path | encoding !} or
    simply {! file_path !} for default encoding from config params. 
    file_path can be a remote URL.
    This is done prior to any other Markdown processing. 
    All file names are relative to the location from which Markdown is being called.
    '''
    def __init__(self, md, config):
        super(IncludePreprocessor, self).__init__(md)
        self.base_path = config['base_path'][0]
        self.encoding = config['encoding'][0]


    def run(self, lines):
        i = -1
        for line in lines:
            i = i + 1
            ms = INCLUDE_SYNTAX_RE.finditer(line)
            for m in ms:
                if m:
                    text = ''
                    total_match = m.group(0)
                    d = m.groupdict()
                    filename = d.get('path')
                    filename = os.path.expanduser(filename)
                    encoding = d.get('encoding')
                    if not encoding_exists(encoding):
                        encoding = self.encoding
                        
                    urlo = urlparse(filename)
                    
                    remote = False
                    if urlo.netloc:
                        # remote url
                        remote = True
                        filename = urlunparse(urlo)
                        text = get_remote_content(filename, encoding)
                    else:
                        # local file
                        if not os.path.isabs(filename):
                            filename = os.path.normpath(os.path.join(self.base_path, filename))
                        try:
                            with open(filename, 'r', encoding=encoding) as f:
                                text = f.read()
                        except Exception as e:
                            log.exception('E: Could not find file {}'.format((filename,)))
                            # no modification will be made, not even stripping the syntax
                            continue

                    lines[i] = lines[i].replace(total_match, text)
        return lines

def makeExtension(*args, **kwargs):  # pragma: no cover
    return IncludeExtension(*args, **kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
