
Include extension for Python Markdown. It lets you include local or remote (downloadable) files into your markdown at your desired places. 

This project is motivated by [markdown-include](https://github.com/cmacmackin/markdown-include) and provides the same functionalities with some extras.

**You should not use markdown-include along with this extension, choose either one, not both.**

# Syntax

1. With explicit encoding: `{! file_path_or_url | encoding !}`
2. Without explicit encoding: `{! file_path_or_url !}`

# Install

Install from Pypi:

```bash
pip install mdx_include
```

# Usage

```python
text = r"""
some text {! some_file !} some more text {! some_more_file | utf-8 !}

Escaping will give you the exact literal \{! some_file !}

If you escape, then the backslash will be removed.

If you want the backslash too, then provide two more: \\\{! some_file !}
"""
md = markdown.Markdown(extensions=['mdx_include'])
html = md.convert(text)
print(html)
```

# Configuration

Config param | Default | Details
------------ | ------- | -------
`base_path` | `.` | The base path from which relative paths are normalized.
`encoding` | `utf-8` | The file encoding.
`allow_local` | `True` | Whether to allow including local files.
`allow_remote` | `True` | Whether to allow including remote files.
`truncate_on_failure` | `True` | Whether to truncate the matched include syntax on failure. False value for both allow_local and allow_remote is treated as a failure.

## Example with configuration

```python
configs = {
            'mdx_include': {
                'base_path': 'mdx_include/test/',
                'encoding': 'utf-8',
                'allow_local': True,
                'allow_remote': True,
                'truncate_on_failure': False,
            },
        }

text = r"""
some text {! some_file !} some more text {! some_more_file | utf-8 !}

Escaping will give you the exact literal \{! some_file !}

If you escape, then the backslash will be removed.

If you want the backslash too, then provide two more: \\\{! some_file !}
"""
md = markdown.Markdown(extensions=['mdx_include'], extension_configs=configs)
html = md.convert(text)
print(html)
```

# Examples

The following markdown:


    Including a gist:
        
    ```python
    {! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
    ```

    Writing the syntax literally: \{! file_path !}
    
    You just escape it with a backslash.
    
    \\\{! file_path !} -> this one will show the backslash before the syntax in HTML


will produce (with fenced code block enabled):

```html
<p>Including a gist:</p>
<pre><code class="python"># -*- coding: utf-8 -*-

# Settings
from django.conf import settings


settings.configure(
    DEBUG=True,
    SECRET_KEY='secretfoobar',
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )
)


# Views
from django.http import HttpResponse
from django.conf.urls import url


def index(request):
    return HttpResponse('&lt;h1&gt;Hello Word&lt;/h1&gt;')

# Routes
urlpatterns = (
    url(r'^$', index),
)


# RunServer
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    import sys

    execute_from_command_line(sys.argv)

</code></pre>

<p>Writing the syntax literally: {! file_path !}</p>
<p>You just escape it with a backslash.</p>
<p>\{! file_path !} -&gt; this one will show the backslash before the syntax in HTML</p>
```
