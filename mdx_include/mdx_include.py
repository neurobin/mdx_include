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
except ImportError:
    # python 2
    from urlparse import urlparse
    from urlparse import urlunparse
    from urllib2 import HTTPRedirectHandler
    from urllib2 import build_opener
from . import version

__version__ = version.__version__


logging.basicConfig()
LOGGER_NAME = 'mdx_include-' + __version__
log = logging.getLogger(LOGGER_NAME)

def encoding_exists(encoding):
    """Check if an encoding is available in Python"""
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
        return build_opener(HTTPRedirectHandler).open(url).read().decode(encoding), True
    except Exception as err:
        # catching all exception, this will effectively return empty string
        log.exception("E: Failed to download: " + url)
        return '', False

class IncludeExtension(markdown.Extension):
    """Include Extension class for markdown"""

    def __init__(self, configs={}):
        self.config = {
            'base_path': [ '.', 'Base path from where relative paths are calculated',],
            'encoding': [ 'utf-8', 'Encoding of the files.', ],
            'allow_local': [ True, 'Allow including local files.', ],
            'allow_remote': [ True, 'Allow including remote files.', ],
            'truncate_on_failure': [True, 'Truncate the include markdown if failed to get the content.'],
            'recurs_local': [True, 'Whether the inclusion is recursive for local files.'],
            'recurs_remote': [False, 'Whether the inclusion is recursive for remote files.'],
            'syntax_left': [r'\{!', 'The left mandatory part of the syntax'],
            'syntax_right': [r'!\}', 'The right mandatory part of the syntax'],
            'syntax_delim': [r'\|', 'Delemiter used to separate path from encoding'],
            'syntax_recurs_on': ['+', 'Character to specify recurs on'],
            'syntax_recurs_off': ['-', 'Character to specify recurs off'],
            'content_cache_local': [True, 'Whether to cache content for local files'],
            'content_cache_remote': [True, 'Whether to cache content for remote files'],
            'content_cache_clean_local': [False, 'Whether to clean content cache for local files after processing all the includes.'],
            'content_cache_clean_remote': [False, 'Whether to clean content cache for remote files after processing all the includes.'],
            }
        # ~ super(IncludeExtension, self).__init__(*args, **kwargs)
        # default setConfig does not preserve None when the default config value is a bool (a bug may be or design decision)
        for k, v in configs.items():
            self.setConfig(k, v)
        
        self.compiled_re = re.compile( ''.join([r'(?P<escape>\\)?', self.config['syntax_left'][0], r'(?P<recursive>[', self.config['syntax_recurs_on'][0], self.config['syntax_recurs_off'][0], r'])?\s*(?P<path>.+?)\s*(', self.config['syntax_delim'][0], r'\s*(?P<encoding>.+?)\s*)?', self.config['syntax_right'][0], ]))
    
    def setConfig(self, key, value):
        if value is None or isinstance(value, bool):
            if self.config[key][0] is None or isinstance(self.config[key][0], bool):
                pass
            else:
                raise TypeError("E: The type of the value (%s) for the key %s is not correct." % (value, key,))
        else:
            if isinstance(value, type(self.config[key][0])):
                pass
            else:
                raise TypeError("E: The type ({}) of the value ({}) does not match with the required type ({}) for the key {}.".format(type(value), value, type(self.config[key][0]), key))
        self.config[key][0] = value

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add( 'mdx_include', IncludePreprocessor(md, self.config, self.compiled_re),'_begin')


class IncludePreprocessor(markdown.preprocessors.Preprocessor):
    '''
    This provides an "include" function for Markdown. The syntax is {! file_path | encoding !} or
    simply {! file_path !} for default encoding from config params. 
    file_path can be a remote URL.
    This is done prior to any other Markdown processing. 
    All file names are relative to the location from which Markdown is being called.
    '''
    def __init__(self, md, config, compiled_regex):
        super(IncludePreprocessor, self).__init__(md)
        self.compiled_re = compiled_regex
        self.base_path = config['base_path'][0]
        self.encoding = config['encoding'][0]
        self.allow_local = config['allow_local'][0]
        self.allow_remote = config['allow_remote'][0]
        self.truncate_on_failure = config['truncate_on_failure'][0]
        self.recursive_local = config['recurs_local'][0]
        self.recursive_remote = config['recurs_remote'][0]
        self.syntax_recurs_on = config['syntax_recurs_on'][0]
        self.syntax_recurs_off = config['syntax_recurs_off'][0]
        self.mdx_include_content_cache_local = {} # key = file_path_or_url, value = content
        self.mdx_include_content_cache_remote = {} # key = file_path_or_url, value = content
        self.markdown.mdx_include_content_cache_clean_local = self.mdx_include_content_cache_clean_local
        self.markdown.mdx_include_content_cache_clean_remote = self.mdx_include_content_cache_clean_remote
        self.markdown.mdx_include_get_content_cache_local = self.mdx_include_get_content_cache_local
        self.markdown.mdx_include_get_content_cache_remote = self.mdx_include_get_content_cache_remote
        self.content_cache_local = config['content_cache_local'][0]
        self.content_cache_remote = config['content_cache_remote'][0]
        self.content_cache_clean_local = config['content_cache_clean_local'][0]
        self.content_cache_clean_remote = config['content_cache_clean_remote'][0]
        
    
    def mdx_include_content_cache_clean_local(self):
        self.mdx_include_content_cache_local = {}
        
    def mdx_include_content_cache_clean_remote(self):
        self.mdx_include_content_cache_remote = {}
    
    def mdx_include_get_content_cache_local(self):
        return self.mdx_include_content_cache_local

    def mdx_include_get_content_cache_remote(self):
        return self.mdx_include_content_cache_remote

    def mdx_include_get_processed_line(self, line):
        resl = ''
        c = 0
        ms = self.compiled_re.finditer(line)
        for m in ms:
            text = ''
            stat = True
            total_match = m.group(0)
            d = m.groupdict()
            escape = d.get('escape')
            if not escape:
                filename = d.get('path')
                filename = os.path.expanduser(filename)
                encoding = d.get('encoding')
                recurse_state = d.get('recursive')
                if not encoding_exists(encoding):
                    if encoding:
                        log.warning("W: Encoding (%s) not recognized . Falling back to: %s" % (encoding, self.encoding,))
                    encoding = self.encoding
                    
                urlo = urlparse(filename)
                
                if urlo.netloc:
                    # remote url
                    if self.allow_remote:
                        filename = urlunparse(urlo).rstrip('/')
                        if self.content_cache_remote and filename in self.mdx_include_content_cache_remote:
                            text = self.mdx_include_content_cache_remote[filename]
                            stat = True
                        else:
                            text, stat = get_remote_content(filename, encoding)
                            if stat and self.content_cache_remote:
                                self.mdx_include_content_cache_remote[filename] = text
                        if stat and text:
                            if self.recursive_remote:
                                if recurse_state != self.syntax_recurs_off:
                                    text = self.mdx_include_get_processed_line(text)
                            elif self.recursive_remote is None:
                                # it's in a neutral position, check recursive state
                                if recurse_state == self.syntax_recurs_on:
                                    text = self.mdx_include_get_processed_line(text)
                    else:
                        # If allow_remote and allow_local both is false, then status is false
                        # so that user still have the option to truncate or not, text is empty now.
                        stat = False
                elif self.allow_local:
                    # local file
                    if not os.path.isabs(filename):
                        filename = os.path.normpath(os.path.join(self.base_path, filename))
                    if self.content_cache_local and filename in self.mdx_include_content_cache_local:
                        text = self.mdx_include_content_cache_local[filename]
                        stat = True
                    else:
                        try:
                            with open(filename, 'r', encoding=encoding) as f:
                                text = f.read()
                                stat = True
                                if self.content_cache_local:
                                    self.mdx_include_content_cache_local[filename] = text
                        except Exception as e:
                            log.exception('E: Could not find file: {}'.format(filename,))
                            # Do not break or continue, think of current offset, it must be
                            # set to end offset after replacing the matched part
                            stat = False
                    if stat and text:
                        if self.recursive_local:
                            if recurse_state != self.syntax_recurs_off:
                                text = self.mdx_include_get_processed_line(text)
                        elif self.recursive_local is None:
                            # it's in a neutral position, check recursive state
                            if recurse_state == self.syntax_recurs_on:
                                text = self.mdx_include_get_processed_line(text)
                else:
                    # If allow_remote and allow_local both is false, then status is false
                    # so that user still have the option to truncate or not, text is empty now.
                    stat = False
            else:
                # this one is escaped, gobble up the escape backslash
                text = total_match[1:]
            
            if not stat and not self.truncate_on_failure:
                # get content failed and user wants to retain the include markdown
                text = total_match
            s, e = m.span()
            resl = ''.join([resl, line[c:s], text ])
            # set the current offset to the end offset of this match
            c = e
        # All replacements are done, copy the rest of the string
        resl = ''.join([resl, line[c:]])
        return resl
        

    def run(self, lines):
        new_lines = []
        for line in lines:
            line = self.mdx_include_get_processed_line(line)
            if line:
                new_lines.extend(line.splitlines())
            else:
                new_lines.append(line)
        if self.content_cache_clean_local:
            self.mdx_include_content_cache_clean_local()
        if self.content_cache_clean_remote:
            self.mdx_include_content_cache_clean_remote()
        return new_lines

def makeExtension(*args, **kwargs):  # pragma: no cover
    return IncludeExtension(*args, **kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
