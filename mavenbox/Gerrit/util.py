
import subprocess
import pipes,os
import shutil
import urllib
from urlparse import urlparse


class GitAdaptor:
   
    
    def __init__(self,url,cache,branch = 'master'):

        self.REVIEW = None
        self.BRANCH = branch
        self.URL = url
        self.GERRIT_BASE = urlparse(url)[1].split(':')[0].split('@')[-1]
        
        r = url.split('/')[-1]
        if r.endswith('.git'):
            r = r[:-4]
        cache = os.path.abspath(cache)
        print(cache)
        self.CACHE = os.path.abspath(os.path.join(cache, r))
        
        self.make_dir(cache)
        self.pull(cache)
        self.get_hook()
        pass
    
    @staticmethod
    def dash(cmd, cwd = None):
        subprocess.call(cmd ,shell=True, cwd=cwd)

    def bash(self, cmd, cwd = None):
        if not cwd:
            subprocess.call(cmd ,shell=True,cwd=self.CACHE)
        else:
            subprocess.call(cmd ,shell=True,cwd=os.path.join(self.CACHE,cwd))
        pass
    
    def get_hook(self):
        hooks_loc = os.path.join(self.CACHE,'.git','hooks','commit-msg')
        urllib.urlretrieve('https://' + self.GERRIT_BASE + '/tools/hooks/commit-msg',  hooks_loc)
        pass


    def make_dir(self,DIR=None):
        try:
            os.mkdir(DIR)
        except:
            pass


    def pull(self,dir):  
        subprocess.call('git clone ' + self.URL ,shell=True,cwd=dir)
        pass

    
    def fcommit(self, title, f_path):
        self.bash('git add -A ')
        print(f_path)
        with open(f_path,'r+') as f:
            raw = f.readlines()
            c=[]
            for i in raw:
                c.append(i.rstrip())
            f.seek(0)
            f.write(title +'\n\n')
            f.write('\n'.join(c))
        self.bash('git commit -F %s' % (f_path) )
        pass


    def commit(self, title, msg = None ):
        self.bash('git add -A ')
        if msg:
            self.bash('git commit -m "%s" -m "%s"' % (title,msg) )
        else:
            self.bash('git commit -m "%s"' % (title) )
        pass


    def set_reviewers(self, mcsv=None):
        if mcsv.startswith('$'):
            return
    
        self.REVIEW = []        
        if mcsv:
            l = mcsv.split(',')
            for i in l:
                self.REVIEW.append(i.strip().lower())


    def push(self):
        self.bash('git push ' + self.URL+  ' HEAD:refs/for/' + self.BRANCH + self.enc_review())
        pass

    

###################################### EMBEDDED UTILITY ##########################################

def enc_review(self):
        if self.REVIEW:
            r_enc = []
            for i in self.REVIEW:
                r_enc.append('r='+i)
            r_enc = '%'+ (',').join(r_enc)
            return r_enc
        else: 
            return '' 

def rebase(self):
    self.bash('git rebase')
    pass

def commitmsg(self):
    msg_path = os.path.join(self.REPO_DIR,'.git','COMMIT_EDITMSG')
    with open(msg_path,'w+') as f:
        pass
    self.bash('git commit --amend')
    pass



##############################################################

GitAdaptor.enc_review = enc_review
GitAdaptor.commitmsg = commitmsg
GitAdaptor.rebase = rebase

##############################################################












def set_user(USER_EMAIL=None):
    if USER_EMAIL:
        GitAdaptor.dash("git config --global user.email " + USER_EMAIL)


def git_ignore(dirs):
    if('.git' in dirs):
        dirs.remove('.git')
    pass


def git_url_filter(url=None):

    url_string = url
    parts = url_string.split('/blob/')
    root = parts[0]
    branch = parts[1].split('/')[0]
    glob = url_string.split(branch).pop()[1:]

    return (root,branch,glob)


# a=GitAdaptor()
# a.push()
# a.commit()