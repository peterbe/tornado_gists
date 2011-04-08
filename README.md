About tornado_gists
===================

This is a [Tornado](http://www.tornadoweb.org/) web app that integrates with
[Github Gists](https://gist.github.com/) so that people in the Tornado
community can share snippets of code with each other.

Anybody can log in (using their Github account) and start adding gists
and discuss them. **Not** only **their own** but anybody's gist.


About the code
--------------

All the code is of course Open Source and is licensed under the [Apache
Licence, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html)

It's by no means perfect and absolutely not the ideal way of writing a
Tornado app (because there is no such way).

To run the code you simply need a MongoDB (of a recentish version) and
install MongoKit which glues MongoDB to Tornado.


About running the tests
-----------------------

To run the tests simply run this command:

    ./bin/run_tests.sh

If you want to run tests just for one single app, `gists` run this:

    ./bin/run_tests.sh apps.gists.tests

And to run a specific test:

    ./bin/run_tests.sh  \
      apps.main.tests.test_handlers.HandlersTestCase.test_homepage

If you're doing development and want to run the same test(s) over and
over just add `--autoreload` like this:

    ./bin/run_tests.sh --autoreload apps.gists.tests

To run the coverage tests, make sure you have ``coverage`` installed
and run this script:

    ./bin/run_coverage_tests.sh

At the moment, this covers 87% of all the code on my computer.



About running database migrations
---------------------------------

MongoDB has no problem with some documents having different structure
even if they're in the same collection. However, the glue code we use
has. MongoKit expects every document in a collection to have the same
structure. At least, every document must have everything that is
entered in the class attribute `structure` in the document classes.

To add migration code you can do two things. For simple changes create
a file called `<myapp>/migrations/always_<whatever>.py` these files
are executed whenever you run the script that starts it:

    ./bin/run_migrations.py

If you have a specific change you want to make create a file that
starts with a number like this for example `003.gender_on_user.py` and
stick it in the `migrations` directory. Next time you run
`run_migrations` it will execute the file and create a file called
`003.gender_on_user.py.done` so that you don't accidentally run the
file again. All `*.done` files are supposed to be ignored by git and
not added to the repo.



About indexing the MongoDB
--------------------------

Indexing can be a precious operation and has therefore been removed
from the code as an automated task. Instead, has to be executed
manually. It's only really necessary to run once since MongoDB is
smart enough to maintain the indexes for new documents once everything
is set up. If you haven't already done so, to ensure all the indexes
run this:

    ./bin/run_migrations.py

Adding more indexing is basically the same as running migrations.