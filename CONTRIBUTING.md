# Contributing guidelines
When opening pull requests, please ensure that you have stated your changes in the description of the PR.

Before opening a pull request, please ensure pylint & pytest both say that your changes are clear.
To test locally, follow the below instructions:

```shell
$ pip install pytest pylint
$ pylint
$ pytest
```

If anything fails, please fix it. This will also be tested by github actions.


Basically, use common sense. Keep lines short (arout 130 characters, 150 at most), make code clear, leave comments etc etc.
