<!--
<p align="center">
  <img src="docs/source/logo.png" height="150">
</p>
-->

<h1 align="center">
  table-format
</h1>

<p align="center">
    <a href="https://github.com/spookylukey/table-format/actions?query=workflow%3ATests">
        <img alt="Tests" src="https://github.com/spookylukey/table-format/workflows/Tests/badge.svg" />
    </a>
    <a href="https://github.com/cthoyt/cookiecutter-python-package">
        <img alt="Cookiecutter template from @cthoyt" src="https://img.shields.io/badge/Cookiecutter-python--package-yellow" /> 
    </a>
    <a href="https://pypi.org/project/table-format">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/table-format" />
    </a>
    <a href="https://pypi.org/project/table-format">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/table-format" />
    </a>
    <a href="https://github.com/spookylukey/table-format/blob/master/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/table-format" />
    </a>
</p>

Format Python code (list of lists) as a fixed width table.

## Usage

You've got some tests or other code like this:
```python

def test_the_table():
    assert generate_the_table() == [
        ["Date", "Name", "Projects released"],
        ["2021-04-06", "spookylukey", 1],
    ]
```

Wouldn't it be nice if those columns lined up?

Copy the whole list of lists to the clipboard, then pipe to ``table-format
--guess-indent``. On Linux you could use `xsel` or `xclip` etc:

```shell
$ xsel | table-format --guess-indent
[
        ['Date',       'Name',        'Projects released'],
        ['2021-04-06', 'spookylukey', 1                  ],
    ]
```

The output should be ready to paste back into your editor.

### Options

Pass the `--help` flag to show all options:

```shell
$ table-format --help
```

## ⬇️ Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/table-format/) with:

```bash
$ pip install table-format
```

You can also use [pipx](https://pipxproject.github.io/pipx/) to install it more
conveniently in an isolated environment:

```bash
$ pipx install table-format
```


The most recent code and data can be installed directly from GitHub with:

```bash
$ pip install git+https://github.com/spookylukey/table-format.git
```

To install in development mode, use the following:

```bash
$ git clone git+https://github.com/spookylukey/table-format.git
$ cd table-format
$ pip install -e .
```

## Other tips

black: use `# fmt: off` and `# fmt: on` commands to stop black reformatting your
nicely aligned columns.


### Emacs
With default keybindings, doing `C-u` `M-|` `table-format --guess-indent` `ENTER` will
replace the current region with the formatted version from `table-format`.

You can wrap it up in a nice function like this:

```elisp
(defun align-python-table ()
  (interactive)
  (shell-command-on-region
   ;; beginning and end of region
   (region-beginning)
   (region-end)
   ;; command and parameters
   "table-format --guess-indent"
   ;; output buffer
   (current-buffer)
   ;; replace?
   t
   ;; name of the error buffer
   "*Table-Format Error Buffer*"
   ;; show error buffer?
   t))
```

## ⚖️ License

The code in this package is licensed under the MIT License.

## 🙏 Contributing
Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.rst](https://github.com/spookylukey/table-format/blob/master/CONTRIBUTING.rst) for more information on getting
involved.

## 🍪 Cookiecutter Acknowledgement

This package was created with
[@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using
[@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-python-package](https://github.com/cthoyt/cookiecutter-python-package)
template.

## 🛠️ Development

The final section of the README is for if you want to get involved by making a code contribution.

### ❓ Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
$ tox
```

Additionally, these tests are automatically re-run with each commit in a [GitHub Action](https://github.com/spookylukey/table-format/actions?query=workflow%3ATests).
