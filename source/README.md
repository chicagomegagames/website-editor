# chicagomegagames.com

This is the source for [chicagoemgagames.com](https://chicagomegagames.com).

It uses a home-built static site generator called "makeme".

To get started with makeme, you need to have Python3 and pip installed.

Then you can just `pip install -r requirements.txt` for the other requirements.

Running `./makeme.py generate` will create a copy of the site in `_site/`.


## Setup Instructions

If you know what you're doing, you can probably just figure it out without
reading on.

### Prerequisites

- Python 3
- virtualenv

Windows users will probably have a significantly harder time getting those setup
than their macOS, Linux, and BSD compatriots. But there should be sufficient
instructions out there on the internet

### Setting Up everything

1.  Create a virtual environment, it should be as simple as running

    ``` bash
    virtualenv -p python3 env
    ```

2.  Activate the virtualenv (windows users, I'm unsure of if this is how you
    actually do it)

    ``` bash
    . env/bin/activate
    ```

    Yes, you actually need that period in there.

3.  Install the requirements

    ```
    pip install -r requirements.txt
    ```

### General Tasks

Before making changes, make sure you understand git, the version control system
we use to track changes to the source. [try.github.io](https://try.github.io) is
a good way to start learning.

All content is generally defined in `pages/`. The index page is kind of special,
because it pulls content from inside `games/` and `calendar.yaml`.

If things ever get "super fucked up", you can always run `git reset --hard
origin/master`, and it will revert to the last good state of the source.

To turn your changes into a set of actual html pages, run `./makeme.py
generate`. It will, by default, output the generated html into `_site/`.

To view that in a browser, run `python -m http.server` inside the `_site`
directory, and open `localhost:8000` in your browser.

After making a set of changes you think are good to go live, commit your
changes, and push to master. Go through the try.github.io tutorial to learn how
to do that, or remind yourself how if you can't remember.

It's okay to consider all of these things magic invocations.
