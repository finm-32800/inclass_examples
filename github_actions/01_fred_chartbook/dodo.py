"""Run or update the project. This file uses the `doit` Python package. It works
like a Makefile, but is Python-based

Run the whole pipeline with:
    doit
"""

#######################################
## Configuration and Helpers for PyDoit
#######################################
## Make sure the src folder is in the path
import sys

sys.path.insert(1, "./src/")

from os import environ, getcwd, path

from colorama import Fore, Style, init

## Custom reporter: Print PyDoit Text in Green
# This is helpful because some tasks write to sterr and pollute the output in
# the console. I don't want to mute this output, because this can sometimes
# cause issues when a command hangs on an error and requires presses on the
# keyboard before continuing. However, I want to be able to easily see the
# task lines printed by PyDoit. I want them to stand out from among all the
# other lines printed to the console.
from doit.reporter import ConsoleReporter
from settings import config

try:
    in_slurm = environ["SLURM_JOB_ID"] is not None
except:
    in_slurm = False


class GreenReporter(ConsoleReporter):
    def write(self, stuff, **kwargs):
        doit_mark = stuff.split(" ")[0].ljust(2)
        task = " ".join(stuff.split(" ")[1:]).strip() + "\n"
        output = (
            Fore.GREEN
            + doit_mark
            + f" {path.basename(getcwd())}: "
            + task
            + Style.RESET_ALL
        )
        self.outstream.write(output)


if not in_slurm:
    DOIT_CONFIG = {
        "reporter": GreenReporter,
        "backend": "sqlite3",
        "dep_file": "./.doit-db.sqlite",
    }
else:
    DOIT_CONFIG = {"backend": "sqlite3", "dep_file": "./.doit-db.sqlite"}
init(autoreset=True)

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")


##################################
## Begin rest of PyDoit tasks here
##################################


def task_config():
    """Create empty directories for data and output if they don't exist"""
    return {
        "actions": ["ipython ./src/settings.py"],
        "targets": [DATA_DIR, OUTPUT_DIR],
        "file_dep": ["./src/settings.py"],
        "clean": [],
    }


def task_pull_fred():
    """Pull GDP data from FRED"""
    return {
        "actions": ["ipython ./src/pull_fred.py"],
        "targets": [DATA_DIR / "fred.parquet"],
        "file_dep": ["./src/settings.py", "./src/pull_fred.py"],
        "task_dep": ["config"],
        "clean": [],
        # FRED publishes new data continuously, and END_DATE moves every day,
        # so this task should never be considered up-to-date.
        "uptodate": [False],
    }


def task_chart_gdp():
    """Create the interactive GDP chart"""
    return {
        "actions": ["ipython ./src/chart_gdp.py"],
        "targets": [OUTPUT_DIR / "gdp_chart.html"],
        "file_dep": ["./src/pull_fred.py", "./src/chart_gdp.py"],
        "task_dep": ["pull_fred"],
        "clean": True,
        "uptodate": [False],
    }


def task_build_site():
    """Build the chartbook HTML site into ./docs"""
    return {
        "actions": ["chartbook build -f"],
        "targets": ["./docs/index.html"],
        "file_dep": [
            "./chartbook.toml",
            "./README.md",
            "./docs_src/charts/gdp.md",
            "./docs_src/dataframes/fred.md",
        ],
        "task_dep": ["chart_gdp"],
        "clean": True,
        "uptodate": [False],
    }
