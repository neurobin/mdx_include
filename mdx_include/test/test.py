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

    """.strip()
    output = get_file_content('mdx_include/test/t.html')
    md = markdown.Markdown(extensions=[IncludeExtension(), 'markdown.extensions.extra']) 
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

if __name__ == "__main__":
    # ~ test_default()
    # ~ test_non_existent()
