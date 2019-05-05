import os   
import sys,re  
import argparse  

import twiggy
import click

log = twiggy.log

msg = {
        'a': "CAUTION : Should non-ref local-artifact get updated version?",
        'b': "Checking POM for modification in artifacts..",
        'c+': "\t[Yes]: requires file rewriting",
        'c-': "\t[No]: does not require file rewriting",
        'd': "[already updated]"

}   

def lpath(label):
    def aux(msg):
        log.name('commit').info(msg)
    return aux
    

    

cmd = {
        'info': log.info,
        'confirm':click.confirm,
        'pause':raw_input,
        'warn' : log.info,
        'debug' : log.info,
        'commit': log.name('commit').notice,
        'except': log.name('except').notice,
        'local': log.name('_local').notice
}

def aformat(a,old_v,new_v=None,i=None):

        a=a.strip()
        if a.startswith('com.ericsson'):
            a = a[13:]
            a = ' '.join(a.split('.'))
        

        sline = ''
        if i:
                sline = "%-5i:" % (i)
        if not new_v:
                return "%s %-52s %-8s" % (sline,a,old_v)
        else:
                return "%s %-52s %s ==> %s " % (sline,a,old_v,new_v)

# print(aformat('com.ericsson.bss.rm.charging.service.productstatusnotification.version', '1.2.4',i=123))

################################################################################################################################################


class PomEditor:

    def __init__(self,PomLocation):
        
        self.POM = {'attrs':[],'cache':[]}
        self.loc = PomLocation
        self.STATUS = False
        with open(self.loc,'r') as f:
                self.POM['cache']=list(f.readlines())

    def path(self):
        return self.loc
    
    def save(self):
        
        cmd['debug'](msg['b'])

        if self.STATUS:  
            cmd['debug'](msg['c+'])
            cmd['debug'](str( "Updating "+ self.loc +" with changes"))
            with open(self.loc,'w+') as f:
                a=''.join(list(self.POM['cache']))
                f.write(a)
        else:  
            cmd['debug'](msg['c-'])

        cmd['debug']("done.")
    

    def update_artifact(self, name, new_v):
        self.a_ref(name, new_v)
        self.a_local(name, new_v)
    



########################  EMBEDDED ARTIFACT UTILITY ######################################
########################                            ######################################


def extract(attr_raw):
        return (re.compile('<%s>' % attr_raw),re.compile('</%s>' % attr_raw))

def extracta(name):
    return re.compile('('+re.escape('<'+name+'>')+')(.*)(' + re.escape('</'+name+'>') +')')

dtag = 'dependency'
dattr = extract(dtag)

atag = 'groupId'     
attr = extracta(atag)

vtag = 'version'
vattr = extracta(vtag)
                        

def a_ref(self, name, new_v=None):

    a_found_flag = False
    cattr = extracta(str(name + '.version'))

    for i, line in enumerate(self.POM['cache']):
        
        if re.findall(cattr,line):
            a_found_flag = True
            old_v = re.sub(cattr,r'\2',line).strip()
            if not new_v:
                return a_found_flag
                
            if not old_v == new_v:
                tag0 = re.sub(cattr,r'\1',line)
                tag1 = re.sub(cattr,r'\3',line)
                
                replaced = tag0.rstrip() + new_v + tag1.lstrip()
                self.POM['cache'][i] = replaced
                self.STATUS = True
                

                cmd['commit'](aformat(name,old_v,new_v=new_v,i=(i+1)))
            else:
                cmd['except'](aformat(name,old_v,new_v=msg['d'],i=(i+1)))

    
    return a_found_flag




def _a_local(self):
    dependencies = []
    enum = enumerate(self.POM['cache'])
    for i, line in enum:
        if re.findall(dattr[0],line):
            begin = i
            while 1:
                l = next(enum)
                if re.findall(dattr[1],l[1]):
                    end = l[0]
                    dependencies.append((begin,end))
                    break
    pass
    return dependencies
    


def a_local(self, name, new_v):
    dependencies = self._a_local()

    for d in dependencies:
        # print(d)
        # print('--------')
        status = False
        span = range(d[0],d[1])

        #groupId 
        groupId = ''
        for i in span:
            if re.findall(attr, self.POM['cache'][i]):
                old_a = re.sub(attr,r'\2',self.POM['cache'][i]).strip()
                groupId = old_a
                pass
                if name == old_a:
                    status = True
                    break
        #version
        if status:
            for i in span:
                line = self.POM['cache'][i]
                if re.findall(vattr, line):
                    old_v = re.sub(vattr,r'\2',line).strip()
                    if old_v.startswith('$'):
                        cmd['local'](aformat(groupId,'$ref$',i=(i+1)))
                        pass
                    else:
                        cmd['local'](aformat(name ,old_v,i=(i+1)))
                        pass 
                        
                        if cmd['confirm'](msg['a'],default=False):
                            
                            if not old_v == new_v:
                                tag0 = re.sub(vattr,r'\1',line)
                                tag1 = re.sub(vattr,r'\3',line)
                                
                                replaced = tag0.rstrip() + new_v + tag1.lstrip()
                            
                                self.POM['cache'][i] = replaced
                                self.STATUS = True
                                cmd['commit'](aformat(name,old_v,new_v=new_v,i=(i+1)))
                            else:
                                cmd['except'](aformat(name,old_v,new_v=msg['d'],i=(i+1)))
                        pass
        pass
    





       
# ////////////////////////////////////////////////////////////////////////////////////////////////////////
PomEditor._a_local = _a_local
PomEditor.a_ref = a_ref
PomEditor.a_local = a_local

# ////////////////////////////////////////////////////////////////////////////////////////////////////////



   
 






############## TESTING ##############
if __name__ == '__main__':
    
    p=PomEditor('./test/pom.xml')
    print(p.path())
    p.update_artifact('com.ericsson.bss.rm.charging.rounding','4.2.9')
    print('done. Press any key to continue...')
    # p.save()

