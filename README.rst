****************************
Mopidy-BTSource
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-BTSource.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-BTSource/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-BTSource.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-BTSource/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/ismailof/mopidy-btsource/master.svg?style=flat
    :target: https://travis-ci.org/ismailof/mopidy-btsource
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/ismailof/mopidy-btsource/master.svg?style=flat
   :target: https://coveralls.io/r/ismailof/mopidy-btsource
   :alt: Test coverage

Mopidy extension to control music received via bluetooth from another device. 

Current features include:
  - Remote Playback Control (play/pause/stop)
  - Remote Playback Monitor: Display Artist/Track/Album Info  

Current feautures do not include:
  - scanning or pairing with the BT device
  - actual reproduction of the audio (it is delivered via PulseAudio)

Currently is on very alpha state, more of a proof of concept. No unit test or alike have been run.
Tested with Mopidy 1.1.1

Installation
============

Install by running:

    git clone git@github.com:ismailof/mopidy-btsource
    sudo python setup.py install
    

Configuration
=============

No current configuration needed

Project resources
=================

- `Source code <https://github.com/ismailof/mopidy-btsource>`_
- `Issue tracker <https://github.com/ismailof/mopidy-btsource/issues>`_


Changelog
=========

v0.2.5 (UNRELEASED)
----------------------------------------

- Initial release on Git.
- First more or less usable version
