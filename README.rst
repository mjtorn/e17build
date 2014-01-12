==============================
E17 BUILDER (also E18 BUILDER)
==============================

What?
=====

A quick hack to build the latest enlightenment releases. Takes the packages off the web, no version
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

There is also the e18build.py command for building e18.

Caveats
=======

It has two dependencies, viz *pyquery* and *docopt*::

  pip install -r requirements.txt

It deletes extracted sources, if found.

It also cleans up the destination dir.

So if the build fails, you don't have anything working for you. Backups are recommended.

There are "experimental" options for --no-clean and --rebuild but they're not guaranteed
to work. Taking a backup and building Enlightenment is so fast that maybe they should be
deprecated, or the builder be taught how to take backups beforehand.

Caveats in the code
-------------------

Some of the variables may be confusing. Destination for downloaded source is called source elsewhere ;)

There are some hardcode-style hacks here and there that I couldn't be bothered with. They might get
attention later.

Help?
=====

By all means! Pull requests and such are more than welcome.

Oh you meant this help::

  (e17build)mjt@ishtar:~/src/git_checkouts/e17build (master *)$ bin/e18build.py --help
  E18 builder

  Usage:
    e18build.py [--mirror=<url>] [--srcpath=<path>] [--instpath=<path>] [--thread-count=<n>] [--no-clean] [--rebuild]

  Options:
    -m <url>, --mirror=<url>      Where to download from [default: http://download.enlightenment.org/]
    -s <path>, --srcpath=<path>   Where to download to [default: /home/mjt/src/e18]
    -i <path>, --instpath=<path>  Where to install to [default: /home/mjt/e18]
    -t <n>, --thread-count=<n>    How many threads to (try to) use in compiling [default: 9]
    --no-clean                    Do not clean up old files
    --rebuild                     Rebuild sources, implies --no-clean


Note the defaults are dynamically generated and may differ for you.

And for your .xsessionrc or whatever you prefer::

  export PATH=$HOME/e18/bin:$PATH
  export LD_LIBRARY_PATH=$HOME/e18/lib:$LD_LIBRARY_PATH
  export PYTHONPATH=$HOME/e18/python/lib/python2.7/site-packages:$PYTHONPATH

  exec $HOME/e18/bin/enlightenment_start

(The PATH setting does not work for me, I need it in .profile but it might be different for you)

