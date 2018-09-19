# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import markdown
from mdx_include.mdx_include import IncludeExtension

def build_url(urlo, base, end, url_whitespace):
    return "https://dummy"

def test_default():
    text = """ 
    This is a simple text 
    
    Including test1.md {! mdx_include/test1.md !}
    
    Including test2.md {! mdx_include/test2.md !}
    
    Including a gist:
    
```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```
    """.strip()
    output = """

    """.strip()
    md2 = markdown.Markdown(extensions=[IncludeExtension(), 'markdown.extensions.extra']) 
    html = md2.convert(text)
    print(html)
    # ~ assert(html == output)

if __name__ == "__main__":
    test_default()
