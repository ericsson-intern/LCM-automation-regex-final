
from Pom.util import PomEditor
from Gerrit.util import *
from Logging import config


import click
import twiggy
from urlparse import urlparse
import csv
import os
import shutil
import json
import random


config.clear()
config.setup()

Log = twiggy.log

def empty(arg):
    pass


msg = {
        'a': "CAUTION : Should non-ref artifact get updated version?",
        'b': "Checking POM for modification in artifacts..",
        'c+': "\t[Yes]: requires file rewriting",
        'c-': "\t[No]: does not require file rewriting",
        'd': "[already updated]",
        'e': "Enter the upgraded versions for following artifacts (leave blank for no changes): \n",
        'com': "CAUTION : This artifact is also mentioned in global namespace of compile/pom.xml. confirm local-artifact upgrade: "
}   



cmd = {
        'info': Log.info,
        'prompt': click.prompt,
        'pause': raw_input,
        'warn' : Log.warning,
        'file': Log.name('file').notice,
        'repo': Log.name('repo').notice,
        'commit': Log.notice,
        'heads': empty,
        'confirm':click.confirm
}

# ////////////////////////////// UTILS /////////////////////////////


COMMIT_FILE = os.path.abspath('.COMMIT_MSG')
print(COMMIT_FILE)

# //////////////////////////////////////////// COMMITS //////////////////////////////////////////////

def prepare_commit(f_path, clog=True):
    COMMIT = []
    clog_file = config.LOG_FILES['commit']
    # clog_file = config.LOG_FILES['runtime']
    
    if clog:
        with open(clog_file,'r') as f:
            l = f.readlines()
            for i in l:
                line = ''
                msg = i.split('|')
                dtype = msg[0].split(':')[-1]
                if dtype == 'repo':
                    pass
                elif dtype == 'file':
                    line = msg[1]
                else:
                    line = '    '+msg[1]
                COMMIT.append('  '+line)

    track_id = 'SCM'
    track_tag = "\n\nTracking-Id: " + track_id
    COMMIT.append(track_tag)

    with open(f_path, 'w') as f:
        f.write(''.join(COMMIT))
        
        

    print('prepared commit....')
# //////////////////////////////////////////// COMMITS //////////////////////////////////////////////

import hashlib
import time

def get_cache_hash():
    hash = hashlib.sha1()
    hash.update(str(time.time()))
    hash.hexdigest()
    return hash.hexdigest()[:12]


def tsv_util(file):
    rows=[]
    with open(file) as f:
        r = csv.DictReader(f, dialect='excel-tab')
        for row in r:
            rows.append(row)
    return rows


def csv_util(filef):
    rows=[]
    with open(filef) as f:
        r = csv.reader(f)
        fields = r.next()
        headers = ['artifactId']
        for row in r:
            artifact = {}
            for i in headers:
                artifact[i] = row[fields.index(i)]
            rows.append(artifact)
    pass
    return rows
    # print("total count of artifacts: %s \ncsv_file: %s" % (str(len(rows)), str(file)) )
    

def url_build(protocol,port,base,path):
    return str(protocol +'://' + base + ':'+ str(port) +'/' + path)
    

class ppcli:
    def __init__(self):
        self.chars = ['=','~','/','*']
        self.trails = {}
        for c in self.chars:
            self.trails[c] = ''.join([c for i in xrange(128)])
    
    def tag(self, msg, c, offset = 36):
        off = str('%.'+str(offset)+'s')
        v = str(off + ' %s ' + off)
        return v % (self.trails[c],msg,self.trails[c])

pp = ppcli()

print(cmd['heads'](pp.tag('pulkit','=',32)))
            



# ///////////////////////////////////// MAVENBOX PUBLIC API /////////////////////////////////////

class MavenBox:
    def __init__(self):
        self._ARTIFACTS = {}
        self._ARTIFACTS_CSV = ''



def filter_artifacts(self, ARTIFACTS):
    print(msg['e'])
    filtered = {}
    for artifact in ARTIFACTS:

        name = artifact['artifactId']

        if name in self._ARTIFACTS:
            d = self._ARTIFACTS[name]
            v_new = cmd['prompt']('artifact: %s' % (name),default=d)
        else:
            v_new = cmd['prompt']('artifact: %s' % (name),default='$')

        if v_new == '$':
            continue
        filtered[name] = v_new
    print(filtered)
    return filtered





def set_csv_file(self, CSV):
    self._ARTIFACTS_CSV = CSV
    pass


def ask_artifacts(self):
    acol = csv_util(self._ARTIFACTS_CSV) 
    acol = self.filter_artifacts(acol)
    self._ARTIFACTS = acol
    return acol


def update_artifacts(self, CACHE=None, REPO_URL=None, BRANCH = None, COMMIT = None, ASK=None, CSV=None):    
    config.clear()
    print('\nPROJECT: ' + str(REPO_URL)+'\n')

    ## default Params Configuration
    if not CACHE:
        CACHE= os.path.abspath(os.path.join(os.path.dirname(__name__),'./.gerrit'))
    
    if ASK:
        ARTIFACTS = self.ask_artifacts()
    else:
        ARTIFACTS = self._ARTIFACTS 

    if not COMMIT:
        COMMIT = ''
    else:
        COMMIT = ': ' + COMMIT


    COMPILE_POM = {''}







    
    # cmd['heads'](pp.tag('GIT','='))\
    # CACHE = os.path.join(CACHE,get_cache_hash())
    try:
        os.makedirs(CACHE)
    except:
        pass
    adaptor = GitAdaptor(REPO_URL, CACHE)
    cmd['repo'](REPO_URL)
    REPO = adaptor.CACHE 

    for root, dirs, files in os.walk(REPO, topdown=True):
        git_ignore(dirs)
        for f in files:
            if f.endswith('pom.xml'):
                #-----------------------------------#
                f_loc = os.path.join(root,f)
                rel_loc = os.path.relpath(f_loc,REPO)
                print(rel_loc)
                abs_loc = os.path.abspath(f_loc)
                POM = PomEditor(abs_loc)
                print('------------')
                #-----------------------------------#


                #______________________________ Compile dependency logic _______________________________#

                if rel_loc.endswith(os.path.join('compile','pom.xml')):
                    for artifact in ARTIFACTS.keys():
                        name = artifact
                        new_v = ARTIFACTS[artifact]
                        f_flag =  POM.a_ref(name,new_v)

                        if f_flag: 
                            COMPILE_POM.add(name)
                    
                        POM.a_local(name,new_v)
                

                else:
                    for artifact in ARTIFACTS.keys():
                        name = artifact
                        new_v = ARTIFACTS[artifact]
                        POM.a_local(name, new_v)

                        if POM.a_ref(name):
                            if name not in COMPILE_POM:
                                POM.a_ref(name, new_v)
                            elif cmd['confirm'](msg['com']):
                                POM.a_ref(name , new_v)
                        pass

                #_________________________________________________________________________________________#

                if POM.STATUS:
                    cmd['file']('$%s' % str(rel_loc)) 

                POM.save()
    


    config.commit_file.close()
    prepare_commit(COMMIT_FILE,clog=False)

    adaptor.fcommit("Automated StepUp" + str(COMMIT),f_path = COMMIT_FILE)
    config.clear()
    config.commit_file._open()
    pass

    return adaptor
    




# export functions in API class
MavenBox.update_artifacts =update_artifacts
MavenBox.ask_artifacts = ask_artifacts
MavenBox.set_csv_file = set_csv_file
MavenBox.filter_artifacts = filter_artifacts

# ///////////////////////////////////// MAVENBOX PUBLIC API /////////////////////////////////////