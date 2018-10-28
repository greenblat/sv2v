#! /usr/bin/python
'''
    help:   invocation: macro_verilog_pp.py [-h] [-y Dir] [-I Dir] [-o <filename>]  [-split [dir]]  File1 File2 ....

    this script massages verilog files. 
    it interprets ifdef/elsif/else/endif directives
    it includes include files
    it replaces all macro definitions
    it computes constants, in the form of "16-1"

    -y Dir     adds search directory to includes list
    -I Dir     identical to -y
    -o Filename  [file3.v default] the script creates one file with all substitutions
    -split     create directory "tmp" where all modules have their own file called "module".v  if -split has parameter, it will be the dir name.
    -h  print these instructions

verilog style params:
    +incdir+DIR+
    +libext+EXT+
    -v LIBFILE

'''


import os,sys,string
import re

from logs import parse_args

Lines2=[]
Lines3=[]
Defined={}
IncDirs=[]
LibExt = ['.v']
def main():
    Params = parse_args()
    run_main(Params)

def run_main(Params):
    global Lines2,Lines3
    Fnames = Params['fnames']
    if Fnames==[]:
        print __doc__
        print 'no files given'
        return
    if ('-h' in Params):
        print __doc__
        return
    if ('-d' in Params):
        Defs = Params['-d']
        for Def in Defs:
            print 'defined',Def
            Defined[Def]=1
    if ('-y' in Params):
        IncDirs.extend(Params['-y'])
    if ('-v' in Params):
        Fnames.extend(Params['-v'])
    if ('incdir' in Params):
        IncDirs.extend(Params['incdir'])
    if ('libext' in Params):
        LibExt.extend(Params['libext'])
    if ('-I' in Params):
        IncDirs.extend(Params['-I'])
    if ('-o' in Params):
        OutFileName = Params['-o'][0]
    else:
        OutFileName = 'file3.v'
    Synopsys = ('-synopsys' in Params)


    Lines = []
    for Fname in Fnames:
        File = open(Fname)
        Lines.extend(readfile(File))
        File.close()

    scan0(Lines)
    File2 = open('filex0.v','w')
    for line in Lines:
        File2.write(line)
    File2.close()

    scan1(Lines)
    File2 = open('filex1.v','w')
    for line in Lines2:
        File2.write(line)
    File2.close()

    if (Synopsys):
        print 'removing translates'
        Lines2= remove_synopsys_on_off(Lines2)
        Lines3= remove_synopsys_on_off(Lines3)

    File2 = open('file2.v','w')
    for line in Lines2:
        File2.write(line)
    File2.close()
    print 'preparing defines...'
    Def2=[]
    for Key in Defined:
        Def2.append((len(Key),Key,Defined[Key]))
    Def2.sort()
    Def2.reverse()
    print 'computing...'
    dones=0
    for i,line in enumerate(Lines3):
        line = use_defines(line,Def2)
#        linex = compute_constants(line)
        linex = line
        Lines3[i]=linex
#        print line,linex
        dones += 1
        if (dones % 10000)==0:
            print '%d lines'%dones
        
    print 'done computing...'
    File3 = open(OutFileName,'w')
    Lines4=[]
    for line in Lines3:
        File3.write(line)
        wrds = string.split(line)
        if len(wrds)!=0:
            Lines4.append(line)
    File3.close()
    print 'lines in the end %d'%len(Lines3)
    if ('-split' in Params):
        Dir = Params['-split'][0]
        if (Dir=='y'):
            Dir='tmp'
        do_the_split(Lines4,Dir)

    File4 = open('file4.v','w')
    state='idle'
    for line in Lines3:
        if len(line)==0:
            pass
        elif line[-1]=='\n':
            line=line[:-1]
        if '//' in line:
            line = line[:line.index('//')]
        if ('/*' in line)and('*/' in line):
            ok=True
            ind0 = line.index('/*')
            ind1 = line.index('*/')
            while ok:
                if ind0>ind1: ok=False
                if ind0<ind1:
                    part1 = line[:line.index('/*')]
                    part2 = line[line.index('*/')+2:]
                    line=part1+part2
                    ok = ('/*' in line)and('*/' in line)
                if ok:
                    ind0 = line.index('/*')
                    ind1 = line.index('*/')
        if state=='idle':
            if ('/*' in line):
                line=line[:line.index('/*')]
                state='work'
        elif state=='work':
            if ('*/' in line):
                line=line[line.index('*/')+2:]
                state='idle'
            else:
                line=''
        
        wrds = string.split(line)
        if len(wrds)>0:
            File4.write('%s\n'%line)
    File4.close()

Pat0 = re.compile('[{:\-+ \[][0-9]+ *[\*] *[0-9]+')
Pat1 = re.compile('[{:\-+ \[][0-9]+ *[+-] *[0-9]+')
Pat2 = re.compile('\( *[0-9]+ *\)')
Pat3 = re.compile(' 0[0-9]+')
Pat4 = re.compile('[-+*/]0[0-9]+')

def stupid1(Str):
    while (len(Str)>1)and(Str[0]=='0')and(Str[1] in '0123456789'):
        Str = Str[1:]
    Mtch = Pat3.search(Str)
    while (Mtch):
        (A,B) = Mtch.span()
        P1 = Str[A:B]
        Bef = Str[:A]
        Aft = Str[B:]
        Str = Bef+P1[2:]+Aft
        Mtch = Pat4.search(Str)

    
    Mtch = Pat4.search(Str)
    while (Mtch):
        (A,B) = Mtch.span()
        P1 = Str[A:B]
        Bef = Str[:A]
        Aft = Str[B:]
        Str = Bef+P1[2:]+Aft
        Mtch = Pat4.search(Str)

    return Str


def computex(Str,Pat,Where):
    Mtch = Pat.search(Str)
    while (Mtch):
        (A,B) = Mtch.span()
        if Where in [0,1]:
            Bef = Str[:A+1]
            Aft = Str[B:]
            P1 = Str[A+1:B]
        else:
            Bef = Str[:A]
            Aft = Str[B:]
            P1 = Str[A:B]
        P1=stupid1(P1)


        P1 = string.replace(P1,' ','')
        try:
            Eval = str(eval(P1))
            Str= Bef+Eval+Aft
            Mtch = Pat.search(Str)
        except:
            print 'error! failed %d eval on "%s" "%s" %s'%(Where,P1,Str[A:B],map(ord,list(Str[A:B])))
            Mtch = False
    return Str 

def compute_constants(line):
    done = False
    while (not done):
        done=True
        linex = computex(line,Pat0,0)
        linex = computex(linex,Pat1,1)
        if linex!=line:
            linex = computex(linex,Pat2,2)
        done = linex==line
        line = linex
    return line 

def use_defines(line,Def2):
    dones=True
    while ('`' in line)and(dones):
        dones =False
        i = 0
        while i<len(Def2):
            (Len,Key,Val)=Def2[i]
            if '`'+Key in line:
                line = string.replace(line,'`'+Key,Val)
                i=len(Def2)+5
                dones =True
            i +=1
    return line


def readfile(File):
    Lines = []
    num=0
    while 1:
        line = File.readline()
        num+=1
        if line=='':
            return Lines
        if line[-1]==13:
            line = line[:-1]+'\n'
        if (len(line)>1)and(ord(line[-2])==13):
            line = line[:-2]+'\n'

        if needs_work(line):
            more = work(line)
            Lines.extend(more)
        else:
            Lines.append(line)
    return Lines

def work(line):
    line = remove_comment1(line)
    line = clear_defs(line)
    if len(line)<2:
        return []
    wrds = string.split(line)
    if '`ifdef' in wrds:
        lines=rework(line,'`ifdef')
        return lines
    if '`ifndef' in wrds:
        lines=rework(line,'`ifndef')
        return lines
    if '`elsif' in wrds:
        lines=rework(line,'`elsif')
        return lines
    if '`else' in wrds:
        lines=rework(line,'`else',False)
        return lines
    if '`endif' in wrds:
        lines=rework(line,'`endif',False)
        return lines
    if '`include' in wrds:
        lines = include_file(wrds[1])
        return lines
    if line[-1]!='\n':
        line=line+'\n'
    return [line]

def include_file(Fname):
    if Fname[0]=='`': return ['`include "%s"\n'%Fname]
    Fname = string.replace(Fname,'"','')
    if os.path.exists(Fname):
        File = open(Fname)
        lines = readfile(File)
        return lines
    for Dir in IncDirs:
        Fname1 = '%s/%s'%(Dir,Fname)
        if os.path.exists(Fname1):
            return include_file(Fname1)
    print 'file "%s" cannot be included'%Fname
    return []
    


def rework(line,Ifdef,Two=True):
    wrds = string.split(line)
    Ind = wrds.index(Ifdef)
    Bef = wrds[:Ind]
    if Two:
        Aft = wrds[Ind+2:]
        This = '%s %s\n'%(wrds[Ind],wrds[Ind+1])
    else:
        Aft = wrds[Ind+1:]
        This = '%s\n'%(Ifdef)
    Line0= string.join(Bef,' ')+'\n'
    Line2= string.join(Aft,' ')+'\n'
    L0 = work(Line0)
    L2 = work(Line2)
    return L0+[This]+L2
        

def clear_defs(line):
    line = string.replace(line,'`elsif',' `elsif ')
    line = string.replace(line,'`ifdef',' `ifdef ')
    line = string.replace(line,'`ifndef',' `ifndef ')
    line = string.replace(line,'`else',' `else ')
    line = string.replace(line,'`endif',' `endif ')
    return line

def remove_comment1(line):
    if '//' in line:
        ind = line.index('//')
        return line[:ind]
    return line

    
def needs_work(line):
    return  ('`ifdef' in line)or('`else' in line)or('`endif' in line)or('`define' in line)or('`ifndef' in line)or('`elsif' in line)or('`include' in line)

def scan0(Lines):
    ind=0
    while ind<len(Lines):
        line = Lines[ind]
        if '//' in line:
            line = line[:line.index('//')]+'\n'
            Lines[ind]=line
        ind += 1

    ind=0
    while ind<len(Lines):
        line = Lines[ind]
        if (len(line)>1)and(line[-2]=='\\'):
            line = line[:-2]+Lines[ind+1]
            Lines[ind]=line
            Lines.pop(ind+1)
        else:
            ind += 1
    ind=0
    while ind<len(Lines):
        line = Lines[ind]
        if (" 'b" in line): line = string.replace(line," 'b","'b")
        if (" 'd" in line): line = string.replace(line," 'd","'d")
        if (" 'h" in line): line = string.replace(line," 'h","'h")
        if ("'b " in line): line = string.replace(line,"'b ","'b")
        if ("'d " in line): line = string.replace(line,"'d ","'d")
        if ("'h " in line): line = string.replace(line,"'h ","'h")
        Lines[ind]=line
        ind += 1
            
    state = 'idle'
    ind=0
    while ind<len(Lines):
        line = Lines[ind]
        if state=='idle':
            if '/*' in line:
                Bef = line[:line.index('/*')]
                Aft = line[line.index('/*')+2:]
                if '*/' in Aft:
                    Aft2 = Aft[Aft.index('*/')+2:]
                    line = Bef+Aft2
                    Lines[ind]=line
                else:
                    Lines[ind]=Bef
                    state = 'inside'
                    ind += 1
            else: 
                ind += 1
        elif state=='inside':
            if '*/' in line:
                line = line[line.index('*/')+2:]
                Lines[ind]=line
                state='idle'
            else:
                Lines[ind]=''
                ind += 1
    


def scan1(Lines):
    state='idle'    
    queue=[]
    indx=0
    while indx<len(Lines):
        line = Lines[indx]
        indx+=1
#        print '>>',indx,state,line,
        wrds = string.split(line)
        if state=='idle':
            if ('`define' in line):
                Defined[wrds[1]]=string.join(wrds[2:],' ')
                Lines2.append(line)
            elif ('`ifndef' in line):
                if wrds[1] in Defined:
                    state='ifdef_false'
                else:
                    state='ifdef_true'
            elif ('`ifdef' in line):
                if wrds[1] in Defined:
                    state='ifdef_true'
                else:
                    state='ifdef_false'
            elif ('`include' in line):
                Def2=[]
                for Key in Defined:
                    Def2.append((len(Key),Key,Defined[Key]))
                Def2.sort()
                Def2.reverse()
                wrds1 = use_defines(wrds[1],Def2)
                lines = include_file(wrds1)
                Lines = Lines[:indx-2]+lines+Lines[indx:] 
            elif needs_work(line):
                print 'error! kind=1',state,indx,line,
            else:
                Lines2.append(line)
                Lines3.append(line)
        elif state=='ifdef_true':
            if ('`define' in line):
                Defined[wrds[1]]=string.join(wrds[2:],' ')
                Lines2.append(line)
            elif ('`ifdef' in line):
                queue = [state]+queue
                if wrds[1] in Defined:
                    state='ifdef_true'
                else:
                    state='ifdef_false'
            elif ('`ifndef' in line):
                queue = [state]+queue
                if wrds[1] in Defined:
                    state='ifdef_false'
                else:
                    state='ifdef_true'
            elif ('`else' in line):
                state='wait_endif'
            elif ('`elsif' in line):
                state='wait_endif'
            elif ('`endif' in line):
                if queue==[]:
                    state='idle'
                else:
                    state=queue.pop(0)
            elif needs_work(line):
                print 'error! kind=2',state,line,
            else:
                Lines2.append(line)
                Lines3.append(line)
            
        elif state=='ifdef_false':
            if ('`else' in line):
                state='active_endif'
            elif ('`elsif' in line):
                if wrds[1] in Defined:
                    state='ifdef_true'
                else:
                    state='ifdef_false'
            elif ('`ifdef' in line):
                queue = [state]+queue
                state='wait_endif'
            elif ('`ifndef' in line):
                queue = [state]+queue
                state='wait_endif'
            elif ('`endif' in line):
                if queue==[]:
                    state='idle'
                else:
                    state=queue.pop(0)
            elif ('`define' in line):
                pass
            elif ('`include' in line):
                pass
            elif needs_work(line):
                print 'error! kind=3',state,line,
        elif state=='active_endif':
            if ('`define' in line):
                Defined[wrds[1]]=string.join(wrds[2:],' ')
                Lines2.append(line)
            elif ('`ifdef' in line):
                queue = [state]+queue
                if wrds[1] in Defined:
                    state='ifdef_true'
                else:
                    state='ifdef_false'
            elif ('`ifndef' in line):
                queue = [state]+queue
                if wrds[1] in Defined:
                    state='ifdef_false'
                else:
                    state='ifdef_true'
            elif ('`else' in line):
                state='wait_endif'
            elif ('`elsif' in line):
                state='wait_endif'
            elif ('`endif' in line):
                if queue==[]:
                    state='idle'
                else:
                    state=queue.pop(0)
            elif ('`include' in line):
                Def2=[]
                for Key in Defined:
                    Def2.append((len(Key),Key,Defined[Key]))
                Def2.sort()
                Def2.reverse()
                wrds1 = use_defines(wrds[1],Def2)
                lines = include_file(wrds1)
                Lines = Lines[:indx-2]+lines+Lines[indx:] 
            elif needs_work(line):
                print 'error! kind=4',state,line,
            else:
                Lines2.append(line)
                Lines3.append(line)
        elif state=='wait_endif':
            if ('`ifdef' in line):
                queue = [state]+queue
                state='wait_endif'
            elif ('`ifndef' in line):
                queue = [state]+queue
                state='wait_endif'
            elif ('`endif' in line):
                if queue==[]:
                    state='idle'
                else:
                    state=queue.pop(0)
            elif ('`else' in line):
                pass
            elif ('`elsif' in line):
                pass
            elif ('`define' in line):
                pass
            elif ('`include' in line):
                pass
            elif needs_work(line):
                print 'error! kind=5',state,line,


def do_the_split(wholelib,dir='tmp'):
    modules=[]
    state=0
    if not os.path.exists(dir):
        os.system('mkdir %s'%dir)
    for ind,line1 in enumerate(wholelib):
        line = fix_stupid_problems(line1)
        wrds =  string.split(line)
        if (state==0):
            if (len(wrds)>0)and(wrds[0] in ['module','primitive','interface','package']):
                line2 = string.replace(line,';',' ; ')
                line2 = string.replace(line2,'(',' ( ')
                wrds =  string.split(line2)
                if len(wrds)==1:
                    line2 = wholelib[ind+1]
                    line2 = string.replace(line2,';',' ; ')
                    line2 = string.replace(line2,'(',' ( ')
                    wrds =  string.split(line2)
                Module = wrds[0] 
                File=open(dir+'/'+Module+'.v','w')
                modules = [Module]+modules
                File.write(line)
                print 'opening ',Module
                state=1
        elif (state==1):
            if (len(wrds)>0)and(has_end(wrds[0])):
                File.write(line)
                File.close()
                state=0
            else:
                File.write(line)

def has_end(word):
    if word in ['endmodule','endprimitive','endinterface','endpackage']:
        return 1
    x =string.find(word,'//')    
    if (x>0):
        word = word[0:x]
        return has_end(word)
    x =string.find(word,'/*')    
    if (x>0):
        word = word[0:x]
        return has_end(word)
    return 0

def fix_stupid_problems(inline):
    for pattern in ["'b ","'h ","'d "]:
        ind  = 1
        while (ind>0):
            ind  = string.find(inline,pattern)
            if (ind>=0):
                inline = inline[0:ind+2]+inline[ind+3:]
    return inline

#  // synopsys translate_off
#  // synopsys translate_on

def remove_synopsys_on_off(Lines):
    Linesx = []
    state='on'
    for line in Lines:
        wrds = string.split(line)
        if 'synopsys' in wrds:
            ind = wrds.index('synopsys')
            if (state=='on'):
                if (len(wrds)>ind)and(wrds[ind+1]=='translate_off'):
                    state='off'
                else:
                    Linesx.append(line)

            elif (state=='off'):
                ind = wrds.index('synopsys')
                if (len(wrds)>ind)and(wrds[ind+1]=='translate_on'):
                    state='on'
        elif (state=='on'):
            Linesx.append(line)
    return Linesx

if __name__ == '__main__':
    main()





