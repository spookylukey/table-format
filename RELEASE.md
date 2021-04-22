# 📦 Making a Release

First check everything is passing, using tox or [GitHub
Actions](https://github.com/spookylukey/table-format/actions?query=workflow%3ATests).

Update CHANGES.md with the current release date, and commit.

Install twine:

```shell
$ pip install twine
```

Bump the version number by running the following from the shell:

```shell
$ bumpversion release
```

Check the version number is to your liking. You can also do `bumpversion minor` etc.

Then
```shell
$ ./release.sh
```

This script does the following:

1. Packages the code in both a tar archive and a wheel
2. Uploads to PyPI using `twine`. Be sure to have a `.pypirc` file configured to
   avoid the need for manual input at this step
3. Pushes to GitHub.

Afterwards, you should do:
```shell
$ bumpversion patch
```

Add a new section to CHANGES.md, with `Version $NEXTVERSION (unreleased)`.
