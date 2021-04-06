# 📦 Making a Release

After installing the package in development mode and installing
`tox` with `pip install tox`, the commands for making a new release are contained within the `finish` environment
in `tox.ini`. Run the following from the shell:

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

