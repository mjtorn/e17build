===========
E17 BUILDER
===========

What?
=====

A quick hack to build the latest e17 release. Takes the packages off the web, no version
control support at the moment.

Comes with no warranties, it's just something I made for myself so it works for me.

Why?
====

Because *easy_e17.sh* doesn't work anymore. Building packages manually sucks, so coding
some help should return on investments in a couple of builds.

Also for fun ;)

How?
====

YMMV slightly, but::

  e17build.py --help

should be pretty helpful!

You may have to screw around with *PYTHONPATH* if it can't find the actual code.

Caveats
=======

It has two dependencies, viz *pyquery* and *docopt*::

  pip install -r requirements.txt

It deletes extracted sources, if found.

It also cleans up the destination dir.

So if the build fails, you don't have anything working for you. Backups are recommended.

Some of the variables may be confusing. Destination for downloaded source is called source elsewhere ;)

Help?
=====

By all means! Pull requests and such are more than welcome.

Oh you meant this help::
  
  (e17build)mjt@ishtar:~/src/git_checkouts/e17build$ bin/e17build.py  --help
  E17 builder

  Usage:
    e17build.py [--mirror=<url>] [--srcpath=<path>] [--instpath=<path>] [--thread-count=<n>]

  Options:
    -m <url>, --mirror=<url>      Where to download from [default: http://download.enlightenment.org/releases/]
    -s <path>, --srcpath=<path>   Where to download to [default: /home/mjt/src/e17]
    -i <path>, --instpath=<path>  Where to install to [default: /home/mjt/e17]
    -t <n>, --thread-count=<n>    How many threads to (try to) use in compiling [default: 9]

Note the defaults are dynamically generated and may differ for you.

