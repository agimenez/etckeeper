etckeeper is a collection of tools to let /etc be stored in a git,
mercurial, bazaar or darcs repository. It hooks into apt to automatically
commit changes made to /etc during package upgrades. It tracks file
metadata that git does not normally support, but that is important for
/etc, such as the permissions of `/etc/shadow`. It's quite modular and
configurable, while also being simple to use if you understand the basics
of working with version control.


## security warnings

First, a big warning: By checking /etc into version control, you are
creating a copy of files like /etc/shadow that must remain secret. Anytime
you have a copy of a secret file, it becomes more likely that the file
contents won't remain secret. etckeeper is careful about file permissions,
and will make sure that repositories it sets up don't allow anyone but root
to read their contents. However, you *also* must take care when cloning
or copying these repositories, not to allow anyone else to see the data.

Since git mushes all the files into packs under the .git directory, the
whole .git directory content needs to be kept secret. (Ditto for mercurial
and .hg as well as bazaar and .bzr)

Also, since version control systems don't keep track of the mode of files
like the shadow file, it will check out world readable, before etckeeper
fixes the permissions. The tutorial has some examples of safe ways to avoid
these problems when cloning an /etc repository.

Also note that `etckeeper init` runs code stored in the repository.
So don't use it on repositories from untrusted sources.


## what etckeeper does

etckeeper has special support to handle changes to /etc caused by
installing and upgrading packages. Before apt installs packages,
`etckeeper pre-install` will check that /etc contains no uncommitted changes.
After apt installs packages, `etckeeper post-install` will add any new
interesting files to the repository, and commit the changes.

You can also run `etckeeper commit` by hand to commit changes.

There is also a cron job, that will use etckeeper to automatically
commit any changes to /etc each day.


## VCS limitations

Version Control Systems are designed as a way to manage source code, not as
a way to manage arbitrary directories like /etc. This means there are a few
limitations that etckeeper has to work around. These include file metadata
storage, empty directories, and special files.

Most VCS, including git, mercurial and bazaar have only limited tracking of
file metadata, being able to track the executable bit, but not other
permissions or owner info. (darcs doesn't even track executable bits.) So
file metadata is stored separately. Among other chores, `etckeeper init`
sets up a `pre-commit` hook that stores metadata about file owners and
permissions into a `/etc/.etckeeper` file. This metadata is stored in
version control along with everything else, and can be applied if the repo
should need to be checked back out.

git and mercurial cannot track empty directories, but they can be
significant sometimes in /etc. So the `pre-commit` hook also stores
information that can be used to recreate the empty directories in the
`/etc/.etckeeper` file.

Most VCS don't support several special files that you _probably_ won't have
in /etc, such as unix sockets, named pipes, hardlinked files (but symlinks
are fine), and device files. The `pre-commit` hook will warn if your /etc
contains such special files.

Darcs doesn't support symlinks, so they are also stored in
`/etc/.etckeeper`.


## tutorial

A quick walkthrough of using etckeeper.

Note that the default VCS is git, and this tutorial assumes you're using
it. Using other VCSes should be broadly similar. 

The `etckeeper init` command initialises an /etc/.git/ repository. 
If you installed etckeeper from a package, this was probably automatically
performed during the package installation. If not, your first step is to
run it by hand:

	etckeeper init

The `etckeeper init` command is careful to never overwrite existing files
or directories in /etc. It will create a `.gitignore` if one doesn't
already exist (or update content inside a "managed by etckeeper" comment
block), sets up pre-commit hooks if they don't already exist, and so on. It
does *not* commit any files, but does `git add` all interesting files for
an initial commit later.

Now you might want to run `git status` to check that it includes all
the right files, and none of the wrong files. And you can edit the
`.gitignore` and so forth. Once you're ready, it's time to commit:

	cd /etc
	git status
	git commit -m "initial checkin"
	git gc # pack git repo to save a lot of space

After this first commit, you can use regular git commands to handle
further changes:

	passwd someuser
	git status
	git commit -a -m "changed a password"

Rinse, lather, repeat. You might find that some files are changed by
daemons and shouldn't be tracked by git. These can be removed from git:

	git rm --cached printcap # modified by CUPS
	echo printcap >> .gitignore
	git commit -a -m "don't track printcap" 

etckeeper hooks into apt (and similar systems) so changes to interesting
files in /etc caused by installing or upgrading packages will automatically
be committed. Here "interesting" means files that are not ignored by
`.gitignore`.

You can use any git commands you like, but do keep in mind that, if you
check out a different branch or an old version, git is operating directly
on your system's /etc. If you do decide to check out a branch or tag,
make sure you run "etckeeper init" again, to get any metadata changes:

	git checkout april_first_joke_etc
	etckeeper init

Often it's better to clone /etc to elsewhere and do potentially dangerous
stuff in a staging directory. You can clone the repository using git clone,
but be careful that the directory it's cloned into starts out mode 700, to
prevent anyone else from seeing files like `shadow`, before `etckeeper init`
fixes their permissions:

	mkdir /my/workdir
	cd /my/workdir
	chmod 700 .
	git clone /etc
	cd etc
	etckeeper init -d .
	chmod 755 ..

Another common reason to clone the repository is to make a backup to a
server. When using `git push` to create a new remote clone, make sure the
new remote clone is mode 700! (And, obviously, only push over a secure
transport like ssh, and only to a server you trust.)

	ssh server 'mkdir /etc-clone; cd /etc-clone; chmod 700 .; git init --bare'
	git remote add backup ssh://server/etc-clone
	git push backup --all

If you have several machine's using etckeeper, you can start with a
etckeeper repository on one machine, then add another machine's etckeeper
repository as a git remote. Then you can diff against it, examine its
history, merge with it, and so on. It would probably not, however, be wise
to "git checkout" the other machine's branch! (And if you do, make sure to
run "etckeeper init" to update file permissions.)
        
	root@kodama:/etc>git remote add dodo ssh://dodo/etc
	root@kodama:/etc>git fetch dodo
	root@kodama:/etc>git diff dodo/master group |head
	diff --git a/group b/group
	index 0242b84..b5e4384 100644
	--- a/group
	+++ b/group
	@@ -5,21 +5,21 @@ sys:x:3:
	adm:x:4:joey
	tty:x:5:
	disk:x:6:
	-lp:x:7:cupsys
	+lp:x:7:

Incidentially, this also means I have a backup of dodo's /etc on kodama.
So if kodama is compromised, that data could be used to attack dodo
too. On the other hand, if dodo's disk dies, I can restore it from this
handy hackup.

Of course, it's also possible to pull changes from a server onto client
machines, to deploy changes to /etc. Once /etc is under version control, the
sky's the limit..


## configuration

The main configuration file is `/etc/etckeeper/etckeeper.conf`

etckeeper runs the executable files in `/etc/etckeeper/$command.d/`. (It
ignores the same ones that run-parts(1) would ignore.) You can modify these
files, or add your own custom files. Each individual file is short, simple,
and does only one action.

For example, here's how to configure it to run `git gc` after each apt run,
which will save a lot of disk space:

	cd /etc/etckeeper/post-install.d
	(echo '#!/bin/sh' ; echo 'exec git gc') > 99git-gc
	chmod +x 99git-gc
	git add .
	git commit -m "run git gc after each apt run"

Here's how to disable the automatic commits after each apt run, while still
letting it git add new files:

	chmod -x /etc/etckeeper/commit.d/50vcs-commit

Here's how to make it automatically push commits to a clone of the
repository as a backup (see instructions above to set up the clone safely):

	cd /etc/etckeeper/commit.d
	(echo '#!/bin/sh' ; echo 'git push backup') > 99git-push
	chmod +x 99git-push
	git add .
	git commit -m "automatically push commits to backup repository"

## changing VCS

By default, etckeeper uses git. This choice has been carefully made;
git is the VCS best supported by etckeeper and the VCS users are most
likely to know.

[ It's possible that your distribution has chosen to modify etckeeper so
  its default VCS is not git -- if they have please complain to them,
  as they're making things unnecessarily difficult for you, and causing
  unnecessary divergence of etckeeper installations. 
  You should only be using etckeeper with a VCS other than git if you're
  in love with the other VCS. ]

If you would like to use some other VCS, and `etckeeper init` has already
been run to set up a git repository, you have a decision to make: Is the
history recorded in that repository something you need to preserve, or can
you afford to just blow it away and check the current /etc into the new
VCS?

In the latter case, you just need to follow three steps:

	etckeeper uninit # deletes /etc/.git!
	vim /etc/etckeeper/etckeeper.conf
	etckeeper init

In the former case, you will need to convert the git repository to the
other VCS using whatever tools are available to do that. Then you can
run `etckeeper uninit`, move files your new VCS will use into place,
edit `etckeeper.conf` to change the VCS setting, and finally
`etckeeper init`. This procedure is clearly only for the brave.


## inspiration

Two blog posts provided inspiration for techniques used by etckeeper:
* http://www.jukie.net/~bart/blog/20070312134706
* http://bryan-murdock.blogspot.com/2007/07/put-etc-under-revision-control-with-git.html

isisetup had some of the same aims as etckeeper, however, unlike it,
etckeeper does not aim to be a git porcelain with its own set of commands
for manipulating the /etc repository. Instead, etckeeper provides a simple
setup procedure and hooks for setting up an /etc repository, and then gets
out of your way; you manage the repository using regular VCS commands.


## license

etckeeper is licensed under version 2 or greater of the GNU GPL.


## author

Joey Hess <joey@kitenet.net>
