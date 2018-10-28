#! /usr/bin/python
import os,sys,string

import module_class
def main():
    Fname = sys.argv[1]
    File = open(Fname)
    read_verilog_file(Fname,'.',Env)



from vyaccer2 import run_yacc
import db0 
import pacifySV

class EnvironmentClass:
    def __init__(self):
        self.SearchDirs=[]
        self.Modules={}
        self.Current=None
        self.DontFlattens=[]
        self.systemverilog=False
        self.VerilogExtensions=['v','glv']

Env = EnvironmentClass()

def read_verilog_file(Fname,RunDir,Env):
    run_lexer(Fname,'%s/lex.out'%RunDir)
    print 'reading %s file'%Fname
    run_yacc('%s/lex.out'%RunDir,RunDir,Fname)
    Locals = db0.load_parsed(RunDir)
    print 'locals %s'%(Locals.keys())
    for Mod in Locals:
        Locals[Mod].cleanZeroNets()
    for Mod in Locals:
        if not Env.Current: Env.Current=Locals[Mod]
        Env.Modules[Mod]=Locals[Mod]
    for Module in Env.Modules:
        pacifySV.run(Env.Modules[Module])
    for Module in Env.Modules:
        Fout = open('%s.vx'%Module,'w')
        Env.Modules[Module].dump_verilog(Fout)
        Fout.close()
        Env.Modules[Module].dump()

import vlexer
import vyaccer2
def run_lexer(Fname,Foutname):
    File = open(Fname)
    if len(sys.argv)>2:
        HelpFile = open(sys.argv[2])
        vlexer.readHelpFile(HelpFile)

    vlexer.run(File,Foutname)
    File.close()
    

def run_yacc(Lexfile,RunDir,Fname):
    vyaccer2.run_yacc(False,'lex.out',RunDir,Fname) 


if __name__ == '__main__': main()
