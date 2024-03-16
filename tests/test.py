# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

# from codecs import open
# import sys
import logging
import markdown
import unittest
from mdx_include.mdx_include import IncludeExtension

LOGGER_NAME = "mdx_include_test"
log = logging.getLogger(LOGGER_NAME)


def get_file_content(path):
    cont = ""
    try:
        with open(path, "r") as f:
            cont = f.read()
    except Exception as e:
        log.exception("E: could not read file: " + path)
    return cont


def assertEqual(self, html, output):
    if tuple(markdown.__version_info__ if hasattr(markdown, "__version_info__") else markdown.version_info) >= (3, 3):
        html = html.replace('ass="language-', 'ass="')
        html = html.replace("\n\n<p>", "<p>")
        html = html.replace("\n<p>", "<p>")
        output = output.replace("\n\n<p>", "<p>")
        output = output.replace("\n<p>", "<p>")
    self.assertEqual(html, output)


class TestMethods(unittest.TestCase):

    def test_default(self):
        text = r"""
This is a simple text

Including test1.md {! tests/test1.md !}

Including test2.md {! tests/test2.md | utf-8 !}

Including a gist:

```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

Writing the syntax literally: \{! file_path !} (you just escape it with a backslash \\\{! file_path !} -> this one will show the backslash before the syntax in HTML)

Recursive include: {! tests/testi.md !}

Forcing non-recursive include: {!- tests/testi.md !}

        """.strip()
        output = get_file_content("tests/t.html")
        md = markdown.Markdown(extensions=[IncludeExtension(), "markdown.extensions.extra"])
        html = md.convert(text)
        # print(html)
        assertEqual(self, html, output.strip())

    def test_non_existent(self):
        text = """
This is a test with non-extistent files

Include was here -> {! file_path !} <- This will strip off the include markdown, i.e it will be replaced with empty string because the path doesn't exist. It will log exception if you monitor the output.

Non-existent URL:

Include was here -> {! https://no.no/ !} <- Non existent URL also strips off the include markdown.

        """
        output = get_file_content("tests/tne.html")
        md = markdown.Markdown(extensions=[IncludeExtension(), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        self.assertEqual(html, output.strip())

    def test_config(self):
        text = r"""
This is a test with custom configuration

Including test1.md {! test1.md !} where base path is set to tests/

Including test2.md {! test2.md | utf-8 !} where base path is set to tests/

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
        output = get_file_content("tests/tc.html")
        configs = {
            "mdx_include": {
                "base_path": "tests/",
                "encoding": "utf-8",
                "allow_local": True,
                "allow_remote": True,
                "truncate_on_failure": False,
                "recurs_local": None,
                "recurs_remote": False,
                "syntax_left": r"\{!",
                "syntax_right": r"!\}",
                "syntax_delim": r"\|",
                "syntax_recurs_on": "+",
                "syntax_recurs_off": "-",
                "content_cache_local": True,
                "content_cache_remote": True,
                "content_cache_clean_local": False,
                "content_cache_clean_remote": False,
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        assertEqual(self, html, output.strip())

    def test_recurs(self):
        text = r"""


Forcing recursive include when recurs_local is set to None: {!+ tests/testi.md !}

        """.strip()
        output = get_file_content("tests/tr.html")
        configs = {
            "mdx_include": {
                "base_path": "",
                "encoding": "utf-8",
                "allow_local": True,
                "allow_remote": True,
                "truncate_on_failure": False,
                "recurs_local": None,
                "recurs_remote": False,
                "syntax_left": r"\{!",
                "syntax_right": r"!\}",
                "syntax_delim": r"\|",
                "syntax_recurs_on": "+",
                "syntax_recurs_off": "-",
                "content_cache_local": True,
                "content_cache_remote": True,
                "content_cache_clean_local": False,
                "content_cache_clean_remote": False,
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        self.assertEqual(html, output.strip())

    def test_manual_cache(self):
        text = r"""

{!test1.md!}

```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

    """
        configs = {
            "mdx_include": {
                "base_path": "tests/",
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        print(md.mdx_include_get_content_cache_local())
        prevr = md.mdx_include_get_content_cache_remote()
        html = md.convert("{!test2.md!}")
        print(md.mdx_include_get_content_cache_local())
        md.mdx_include_get_content_cache_local()["tests/test2.md"] = ["modified"]
        print(md.convert("{!test2.md!}"))
        self.assertEqual(md.mdx_include_get_content_cache_remote(), prevr)
        md.mdx_include_content_cache_clean_local()
        self.assertEqual(md.mdx_include_get_content_cache_local(), {})
        md.mdx_include_content_cache_clean_remote()
        self.assertEqual(md.mdx_include_get_content_cache_remote(), {})

    def test_cache(self):
        text = r"""

Including the same file should use the content from cache instead of reading them from files every time.

Including test1.md {! tests/test1.md !}

Including test1.md {! tests/test1.md !}

Including test1.md {! tests/test1.md !}

Including a gist:

```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

Including a gist:

```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

Including a gist:

```python
{! https://gist.github.com/drgarcia1986/3cce1d134c3c3eeb01bd/raw/73951574d6b62a18b4c342235006ff89d299f879/django_hello.py !}
```

    """.strip()
        output = get_file_content("tests/tcache.html")
        md = markdown.Markdown(extensions=[IncludeExtension(), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        assertEqual(self, html, output.strip())
        md.mdx_include_content_cache_clean_local()
        md.mdx_include_content_cache_clean_remote()

    def test_cyclic(self):
        text = r"""
This is a test with circular inclusion

{! testcya.md !}

        """.strip()
        output = get_file_content("tests/testcy.html")
        configs = {
            "mdx_include": {
                "base_path": "tests/",
                "allow_circular_inclusion": True,
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        self.assertEqual(html, output.strip())

    def test_file_slice(self):
        text = r"""
This is a test with file slice syntax

{! testfls.md [ln:4.6-4.3] !}

{! testfls.md [ln:.14-.14] !}

{! testfls.md [ln:1.2-2.13,6.4-2.3] !}

        """.strip()
        output = get_file_content("tests/tfls.html")
        configs = {
            "mdx_include": {
                "base_path": "tests/",
                "allow_circular_inclusion": True,
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        self.assertEqual(html, output.strip())

    def test_relative_include(self):
        text = r"""
This is a test with relative include

{! tests/c.md !}

{! tests/md/b.md !}

        """.strip()
        output = get_file_content("tests/trl.html")
        configs = {
            "mdx_include": {
                "allow_circular_inclusion": True,
                "recursive_relative_path": True,
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "markdown.extensions.extra"])
        html = md.convert(text)
        # ~ print(html)
        self.assertEqual(html, output.strip())

    def test_strip_indent(self):
        configs = {
            "mdx_include": {
                "base_path": "tests/",
            },
        }
        md = markdown.Markdown(extensions=[IncludeExtension(configs["mdx_include"]), "fenced_code"])

        # Test that indentation is removed from docstring snippet
        text = "{!< testindent.py [ln:6-8] !}"
        html = md.convert(text)
        # ~ print(html)
        output = "<p>Defines an Example object</p>\n<p>This docstring should be sliced from this file and the four leading spaces should be stripped from each line</p>"
        self.assertEqual(html, output)

        # Test that indentation is removed from a code snippet, so we can add our own and specify the language
        text = "```python\n{!< testindent.py [ln:13-14] !}\n```"
        html = md.convert(text)
        # ~ print(html)
        output = (
            '<pre><code class="language-python">def __init__(self, attr1):\n    self.attribute1 = attr1\n</code></pre>'
        )
        self.assertEqual(html, output)


if __name__ == "__main__":
    unittest.main()
