
def b(title):
    f_path = 'commit.log'
    with open(f_path,'r+') as f:
        raw = f.readlines()
        c=[]
        for i in raw:
            c.append('\t' + i.rstrip())
        f.seek(0)
        f.write(title +'\n\n')
        f.write('\n'.join(c))
    
b('Updated the new commit')