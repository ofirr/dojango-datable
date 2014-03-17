
WARNING: this file is wildly outdated

=dojango-datable=

==What is it?==

Dojango Data Tables allows you to define table layout and column types in
Python instead of JS or HTML. It also includes a few template tags to create
HTML required for the dojo.DataGrid in a configurable manner.

It can also be used to generate a XLS file or CSV file out of displayed information,
so you can either use it as a web UI widget or a XLS generator with Django and Dojango,
or both. First, show a nice, scrollable table to the user, then let him/her download
the data in preferred format.

dojango-datable requires [http://code.google.com/p/dojango/ dojango] and [http://www.python-excel.org/ xlwt].

==Installation==

{{{
$ pip install svn+http://dojango-datable.googlecode.com/svn/trunk/
}}}


== TODO ==

6) save state of all filters
7) save sort order of the table
8) optional on-off columns
9) minimal example for contrib.auth for the docs
