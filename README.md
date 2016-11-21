Welcome to the README for the Multistage Segmenter!

# Prerequisites:
You need OpenFST and OpenGRM installed on your system.  The commands for these must be on your path so that you can call them from any directory.
Note that there are no Windows versions of OpenFST or OpenGRM; you will need a Unix-like operating system to run this code.

# Virtual Environment:
We recommend you use virtualenv to keep your python installations nicely insulated from one another.  Mseg will work without it, but installing experimental code to your system's default python instance is not a very good idea.

# Mseg installation:
Download the contents of the <https://github.com/rjm49/multistage_segmenter> repository to a local folder on your system (you can either download a tar file or clone the repo).

In the repo top level, you will find a `requirements.txt`
Install the required python packages by running: `pip install -r requirements.txt`

You can then install mseg itself.  Do this by running: `pip install --no-index --find-links [path/to/repo/dir]`
(If you are in the root of the repo then you can replace the path with a single dot ".")

Run `pip --list` to ensure mseg has installed.

# Mseg configuration:
There are still a couple of things you need to do to run mseg.

## Workspace (or base_dir)
Create a workspace directory anywhere convenient on your system e.g. `~/mseg_workspace`

## Default train and test files
There are `default_train.csv` and `default_test.csv` files supplied with the source (in `default_files/` ).  It's recommended that you put these into your workspace while you're setting up.  The system will pick them up automatically when you run any of the primary scripts.

## Configuration file
We chose to go the `config file` route with mseg.  There is just one (JSON - see <http://json.org>) config file.  A default version called `mseg_config.cfg` is supplied with the source: You can rename it but mostly there's no need. In this file, set the `base_dir` entry so it points to your workspace directory.  This is important, since all scripts use it.  The config file is sought in the "current working directory" by default, but can be specified to the mseg scripts via the command line.

# Primary scripts
There are three primary scripts that run the segmenter, all in the `scripts/` directory.  These are:
* `train_pm.py` - this must be run first to ascertain the probabilities based on prosodic (it saves them to file)
* `create_models.py`- this is run next, this produces the numerous FSTs models for the main batch
* `main_run.py`- this is run last - it uses the files output by the first two scripts to compose, analyse and report on batches of models.

Each one of the primary scripts can take a --usage flag to get info on the parameters it can take.

The default configuration file already has a batch set up ("test_batch", the first entry in the `batches` list) and so it should be possible to run all three scripts in order and (if the base_dir is configured) get output that should appear in the `test_batch` directory.