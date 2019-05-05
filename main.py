
import mavenbox.util as util
import json
import sys
import os
import shutil

BASE = "egrgplk@gerrit.ericsson.se"
LINKS = [
    'a/bssf/com.ericsson.bss.top'
]

def update_interface(commit, aflag, csv, review ):

    MB = util.MavenBox()
    MB.set_csv_file(csv)
    MB.ask_artifacts()
    
    
    for link in LINKS:   
        url = util.url_build('https',443,BASE,link)
        adaptor = MB.update_artifacts(CACHE='.cache',REPO_URL=url, COMMIT=commit,ASK = aflag, CSV=csv)
        # adaptor.set_reviewers(review)
        # adaptor.push()
        raw_input("=> Done. \n\nPress Enter to continue...")
    pass





























# def update_interface(csv,reviewers):

#     with open('./repobox/git_links.json') as f:
#         links = json.loads(f.read())

#     for link in links[:3]:
#         url = url_build('ssh',29418,link['base'],link['repo'])

#         git = update_dependency(COLLECTION_ROOT=COLLECTION_ROOT, ARTIFACTS_CSV=csv,REPO_URL=url)
#         git.set_reviewers(reviewers)
#         git.push()
#         raw_input("Press Enter to continue...")



    