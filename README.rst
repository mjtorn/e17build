===========
E17 BUILDER
===========

What?
=====

A quick hack to build the latest e17 release.

Comes with no warranties, it's just something I made for myself so it works for me.

Why?
====

Because easy_e17.sh doesn't work anymore. Building packages manually sucks, so coding
some help should return on investments in a couple of builds.

Also for fun ;)

Caveats
=======

It deletes extracted sources, if found.

It also cleans up the destination dir.

So if the build fails, you don't have anything working for you. Backups are recommended.

It only knows how to install into the current user's home directory, as the user.

It doesn't prompt for anything.

Some of the variables may be confusing. Destination for downloaded source is called source elsewhere ;)

Help?
=====

By all means! Pull requests and such are more than welcome.

