#! /usr/bin/python


import os,sys,string,types

DIR = 'ips/zero-riscy/'
DIR = 'zero_svrtl'
INCLUDES = DIR+'/include'

def main():
    if len(sys.argv)==1:
        Fnames = os.listdir(DIR)
        for Fname in Fnames:
            if endsWith(Fname,'.sv')and('latch' not in Fname):
                prep('%s/%s'%(DIR,Fname),Fname[:-3])
        return
    Fname = sys.argv[1]
    lll = string.split(Fname,'/')
    l0 = lll[-1]
    Cell = l0[:-3]
    prep(Fname,Cell)

def endsWith(Long,Short):
    if type(Long)!=types.StringType: return False
    if Short not in Long: return False
    return  Long.index(Short)==(len(Long)-len(Short))



def prep(Fname,Cell):
    os.system('llbin/macro_verilog_pp.py  -d VERILATOR -d SYNTHESIS -I %s  %s -split'%(INCLUDES,Fname))
    os.system('grep -v import file3.v > file33.v')
    os.system(' ../../llbin/sv2v.py  file33.v pulpino.types >& logs/%s.log'%Cell)
    os.system('/bin/mv %s.vx rtl_zero/'%Cell)
    os.system('/bin/mv %s.dump dumps/'%Cell)
    print Fname




main()

