# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

# ~ from codecs import open
import logging
import markdown
from mdx_include.mdx_include import IncludeExtension

LOGGER_NAME = 'mdx_include_test'
log = logging.getLogger(LOGGER_NAME)

def get_file_content(path):
    cont = ''
    try:
        with open(path, 'r') as f:
            cont = f.read();
    except Exception as e:
        log.exception("E: could not read file: " + f)
    return cont


def test_default():
    text = r""" 
This is a simple text 

Including test1.md {! mdx_include/test/test1.md !}

Including test2.md {! mdx_include/test/test2.md | utf-8 !}

Including a gist:
    
```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

Writing the syntax literally: \{! file_path !} (you just escape it with a backslash \\\{! file_path !} -> this one will show the backslash before the syntax in HTML)

Recursive include: {! mdx_include/test/testi.md !}

Forcing non-recursive include: {!- mdx_include/test/testi.md !}

    """.strip()
    output = get_file_content('mdx_include/test/t.html')
    md = markdown.Markdown(extensions=[IncludeExtension(),
                        'markdown.extensions.extra',
                        ]) 
    html = md.convert(text)
    # ~ print(html)
    assert(html == output.strip())

def test_non_existent():
    text = """
This is a test with non-extistent files

Include was here -> {! file_path !} <- This will strip off the include markdown, i.e it will be replaced with empty string because the path doesn't exist. It will log exception if you monitor the output.

Non-existent URL:

Include was here -> {! https://no.no/ !} <- Non existent URL also strips off the include markdown.

    """
    output = get_file_content('mdx_include/test/tne.html')
    md = markdown.Markdown(extensions=[IncludeExtension(), 'markdown.extensions.extra']) 
    html = md.convert(text)
    # ~ print(html)
    assert(html == output.strip())


def test_config():
    text = r"""
This is a test with custom configuration

Including test1.md {! test1.md !} where base path is set to mdx_include/test/

Including test2.md {! test2.md | utf-8 !} where base path is set to mdx_include/test/

Including a gist:
    
```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

Writing the syntax literally: \{! file_path !} (you just escape it with a backslash \\\{! file_path !} -> this one will show the backslash before the syntax in HTML)

Include is here -> {! file_path !} <- This will produce file not found warning but won't strip off the include markdown because truncate_on_failure is False in the config.

Non-existent URL:

Include is here -> {! https://no.no/ !} <- This will produce download failed warning but won't strip off the include markdown because truncate_on_failure is False in the config.

Forcing recursive include when recurs_local is set to None: {!+ testi.md !}

{! test2.md | Invalid !}

    """.strip()
    output = get_file_content('mdx_include/test/tc.html')
    configs = {
                'mdx_include': {
                    'base_path': 'mdx_include/test/',
                    'encoding': 'utf-8',
                    'allow_local': True,
                    'allow_remote': True,
                    'truncate_on_failure': False,
                    'recurs_local': None,
                    'recurs_remote': False,
                    'syntax_left': r'\{!',
                    'syntax_right': r'!\}',
                    'syntax_delim': r'\|',
                    'syntax_recurs_on': '+',
                    'syntax_recurs_off': '-',
                    
                },
            }
    md = markdown.Markdown(extensions=[IncludeExtension(configs['mdx_include']), 'markdown.extensions.extra']) 
    html = md.convert(text)
    # ~ print(html)
    assert(html == output.strip())

if __name__ == "__main__":
    test_default()
    test_non_existent()
    test_config()
