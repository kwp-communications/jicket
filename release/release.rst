Release
=================
Information and steps required to release a new version. All of these changes must be performed in a release branch.



1. Bump version number and start release branch
------------------------------------------------
Jicket uses `semantic versioning <https://semver.org/>`_. Bump the version according to the rules of semantic versioning in ``VERSION``.

Afterwards you can begin the release branch: ``git flow release start "$(< VERSION)"``



2. Update documentation
-------------------------
Update all the documentation to reflect the contents of the new release if this hasn't happened yet.



3. Testing
-------------------------
Test that everything works and fix bugs if you find any. Additionally run tests.



4. Release
-------------------------
If, and only if, all tests succeed, finish the release branch.



5. pip
-------------------------
Make sure you are on the ``master`` branch. Build the sdist file

  ``python setup.py sdist``

and then upload it to the PyPI test repository using ``twine``

  ``twine upload --repository-url https://test.pypi.org/legacy/ dist/*``

Check that everything works as expected and the readme is formatted correctly.
If everything is fine, upload it to the real PyPI repository.

  **WARNING!** Once a version has been uploaded, it can't ever be reused, even if the PyPI repository is deleted.
  Make sure everything is perfect BEFORE uploading to the real repo! See 5.1 on how to do that.

  ``twine upload dist/*``

5.1 Checking PyPI package locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When you build the package with sdist, a ``jicket-x.x.x.tar.gz`` gets placed in ``dist/``.
Unpack it with ``tar xvf jicket-x.x.x.tar.gz``.
Create a virtualenv, activate it and then run ``python setup.py install`` inside the extracted folder.
Also take a look at all the files contained in the folder.



6. Docker
-------------------------
Build and tag the image with

  ``docker build release/docker --no-cache -t kwpcommunications/jicket:"$(< VERSION)"``

  ``docker build release/docker -t kwpcommunications/jicket:latest``


Then log in to docker with

  ``docker login``

and push the image

  ``docker push kwpcommunications/jicket:"$(< VERSION)"``

  ``docker push kwpcommunications/jicket:latest``
