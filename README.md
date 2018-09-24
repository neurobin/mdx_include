[![Build Status](https://travis-ci.org/neurobin/mdx_include.svg?branch=release)](https://travis-ci.org/neurobin/mdx_include)

Include extension for Python Markdown. It lets you include local or remote (downloadable) files into your markdown at arbitrary positions. 

This project is motivated by [markdown-include](https://github.com/cmacmackin/markdown-include) and provides the same functionalities with some extras.

Inclusion for local file is by default recursive and for remote file non-recursive. You can change this behavior through configuration.

File/Downloaded contents are cached, i.e if you include same file multiple times in multiple places, they won't be read/downloaded more than once. This behavior can also be changed with configuration.

Circular inclusion by default raises an exception. You can change this behavior to include the affected files in non-recursive mode through configuration.

**You should not use markdown-include along with this extension, choose either one, not both.**

# Syntax

1. **Simple:** `{! file_path_or_url !}`
2. **With explicit encoding:** `{! file_path_or_url | encoding !}`
3. **With recurs_state on:** `{!+ file_path_or_url !}` or `{!+ file_path_or_url | encoding !}`. This makes the included file to be able to include other files. This is meaningful only when recursion is set to `None`. If it is set to `False`, this explicit recurs_state defintion can not force recursion. This is a depth 1 recursion, so you can choose which one to recurs and which one to not.
4. **With recurs_state off:** `{!- file_path_or_url !}` or `{!- file_path_or_url | encoding !}`. This will force not to recurs even when recursion is set to `True`.
5. **Escaped syntax:** You can escape it to get the literal. For example, `\{! file_path_or_url !}` will give you literal `{! file_path_or_url !}` and `\\\{! file_path_or_url !}` will give you `\{! file_path_or_url !}`


**General syntax:** `{!recurs_state file_path_or_url | encoding !}`

> The spaces are not necessary. They are just to make it look nice :) . No spaces allowed between `{!` and recurs_state (`+-`)


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
some text {! test1.md !} some more text {! test2.md | utf-8 !}

Escaping will give you the exact literal \{! some_file !}

If you escape, then the backslash will be removed.

If you want the backslash too, then provide two more: \\\{! some_file !}
"""
md = markdown.Markdown(extensions=['mdx_include'])
html = md.convert(text)
print(html)
```

**Example output:**

(*when test1.md contains a single line `**This is test1.md**` and test2.md contains `**This is test2.md**`*)

```html
<p>some text <strong>This is test1.md</strong> some more text <strong>This is test2.md</strong></p>
<p>Escaping will give you the exact literal {! some_file !}</p>
<p>If you escape, then the backslash will be removed.</p>
<p>If you want the backslash too, then provide two more: \{! some_file !}</p>
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
`syntax_left` | `\{!` | The left boundary of the syntax. (Used in regex, thus escaped `{`).
`syntax_right` | `!\}` | The right boundary of the syntax. (Used in regex, thus escaped `}`).
`syntax_delim` | `\\|` | The delimiter that separates encoding from path_or_url. (Used in regex, thus escaped `\|`).
`syntax_recurs_on` | `+` | The character to specify recurs_state on. (Used in regex).
`syntax_recurs_off` | `-` | The character to specify recurs_state off. (Used in regex).
`content_cache_local` | `True` | Whether to cache content for local files.
`content_cache_remote` | `True` | Whether to cache content for remote files.
`content_cache_clean_local` | `False` | Whether to clean content cache for local files after processing all the includes
`content_cache_clean_remote` | `False` | Whether to clean content cache for remote files after processing all the includes
`allow_circular_inclusion` | `False` | Whether to allow circular inclusion. If allowed, the affected files will be included in non-recursive mode, otherwise it will raise an exception.

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

# Manual cache control

The configuration gives you enough cache control, but that's not where it ends :). You can do manual cache cleaning instead of letting the extension handle it for itself. First turn the auto cache cleaning off by setting `content_cache_clean_local` and/or `content_cache_clean_remote` to `False` (this is default), then call the cache cleaning function manually on the markdown object whenever you want:

```python
md.mdx_include_content_cache_clean_local()
md.mdx_include_content_cache_clean_remote()
```

You can also get the internal cache dictionary and make inplace modification (e.g cleaning a specific cache for a specific file/URL, or even modify the cached content):

```python
local_cache_dict = md.mdx_include_get_content_cache_local()
remote_cache_dict = md.mdx_include_get_content_cache_remote()
```

# How circular inclusion works

Let's say, there are three files, A, B and C. A includes B, B includes C and C inclues A and we are doing recursive include.

If circular inclusion is not allowed in the config i.e if `allow_circular_inclusion` is `False` (which is the default) then it will raise an exception.

If `allow_circular_inclusion` is set to `True`, then it will work like this:

1. A and B will be normally included
2. B includes C normally too
3. C includes A which is a circular inclusion (`C>A>B>C>A>B>C...`). Thus A will be included in non-recursive mode as `allow_circular_inclusion` is set to `True` i.e C will include A literally without parsing A anymore.

# An example of including a gist

The following markdown:


    Including a gist:
        
    ```python
    {! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
    ```


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
```
