
Include extension for Python Markdown. It lets you include local or remote (downloadable) files into your markdown at your desired places. 

This project is motivated by [markdown-include](https://github.com/cmacmackin/markdown-include) and provides the same functionalities with some extras.

Inclusion for local file is by default recursive and for remote file non-recursive. You can change this behavior through configuration. 

**You should not use markdown-include along with this extension, choose either one, not both.**

# Syntax

General syntax: `{!recurs_state file_path_or_url | encoding !}`

**The spaces are not necessary. They are just to make it look nice :) . No spaces allowd between `{!` and recurs_state**

**Examples:**

1. **Simple:** `{! file_path_or_url !}`
2. **With explicit encoding:** `{! file_path_or_url | encoding !}`
3. **With recurs_state on:** `{!+ file_path_or_url !}` or `{!+ file_path_or_url | encoding !}`. This makes the included file to be able to include other files. This is meaningful only when recursion is set to `None`. If it is set to `False`, this explicit recurs_state defintion can not force recursion. This is a depth 1 recursion, so you can choose which one to recurs and which one to not.
4. **With recurs_state off:** `{!- file_path_or_url !}` or `{!- file_path_or_url | encoding !}`. This will force not to recurs even when recursion is set to `True`.

**You can escape it to get the literal. For example, `\{! file_path_or_url !}` will give you literal `{! file_path_or_url !}` and `\\\{! file_path_or_url !}` will give you `\{! file_path_or_url !}`**

## You can change the syntax!!!

If you don't like the syntax you can change it through configuration.

There might be some complications with the syntax `{!file!}`, for example, conflict with `markdown.extensions.attr_list` which uses `{:?something}`. As the `:` is optional, a typical problem that occurs is this one:

```md
A paragraph
{!our syntax!}
```
would produce:

```html
<p syntax_="syntax!" _our="!our">A paragraph</p>
```

If you really want to avoid this type of collision, find some character sequence that is not being used by any extension that you are using and use those character sequences to make up the syntax.

[See the configuration section for details](#configuration)


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
`recurs_local` | `True` | Whether the inclusions are recursive on local files. Options are: `True`, `False` and `None`. `None` is a neutral value with negative default and overridable with recurs_state (e.g `{!+file!}`). `False` will permanently prevent recursion i.e you won't be able to override it with the recurs_state. `True` value is overridable with recurs_state (e.g `{!-file!}`).
`recurs_remote` | `False` | Whether the inclusions are recursive on remote files. Options are: `True`, `False` and `None`. `None` is a neutral value with negative default and overridable with recurs_state (e.g `{!+file!}`). `False` will permanently prevent recursion i.e you won't be able to override it with the recurs_state. `True` value is overridable with recurs_state (e.g `{!-file!}`).
`syntax_left` | `\{!` | The left boundary of the syntax. (Used in regex, thus escaped `{`)
`syntax_right` | `!\}` | The right boundary of the syntax. (Used in regex, thus escaped `}`)
`syntax_delim` | `\\|` | The delimiter that separates encoding from path_or_url. (Used in regex, thus escaped `\|`)
`syntax_recurs_on` | `+` | The character to specify recurs_state on. (Used in regex)
`syntax_recurs_off` | `-` | The character to specify recurs_state off. (Used in regex)

## Example with configuration

```python
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
