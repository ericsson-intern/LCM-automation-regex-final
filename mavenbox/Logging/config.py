from twiggy import *
import os



LOG_FILES = {
    'runtime'   :  "./logs/runtime.log",
    'commit'    :  "./logs/commit.log"
}

def clear():
    try:
        for i in LOG_FILES.keys():
            os.unlink(LOG_FILES[i])
    except:
        pass


runtime = outputs.FileOutput(LOG_FILES['runtime'], format=formats.line_format)
commit_file = outputs.FileOutput(LOG_FILES['commit'], format=formats.shell_format)



def setup():

    add_emitters(("runtime", levels.INFO, None, runtime),
        ("committer", levels.INFO, filters.names("commit","file"), commit_file),
        # ("_local", levels.INFO, filters.names("_local"), runtime),
        # ("except", levels.INFO, filters.names("except"), runtime)
        )