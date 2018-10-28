


import module_class
import logs
import string
import os
import matches
import types

import scanForRegs
if os.path.exists('packages_save.py'):
    import packages_save
else:
    packages_save = False

def info(Txt):
    logs.log_info('pacify: %s'%(Txt))


def run(Mod):
    for Net in Mod.nets:
        Dir,Wid = Mod.nets[Net]
        if 'logic' in Dir: 
            ww = string.split(Dir)
            dres = []
            for Wd in ww:
                if Wd!='logic':
                    dres.append(Wd) 
            if dres==[]:
                Dir = 'wire'
            else:
                Dir = string.join(dres,' ')

        Mod.nets[Net] = Dir,Wid
    Nets = Mod.nets.keys()
    for Net in Nets:
        Dir,_ = Mod.nets[Net]
        wrds = string.split(Dir)
        if wrds[-1] in packages_save.TYPEDEFS:
            Def =  packages_save.TYPEDEFS[wrds[-1]]
            Ndir,Nwid = getTypedefData(Mod,Def)
            if len(wrds)==1:
                Mod.nets[Net]=Ndir,Nwid
            else:
                Mod.nets[Net]=wrds[0],Nwid

    for Net in Nets:
        Dir,Wid = Mod.nets[Net]
#        if is_external_dir(Dir) and complexType(Wid) and (Wid[0]=='double'):
        if complexType(Wid) and (Wid[0]=='double'):
#            logs.log_warning('net %s is unpacked dir =%s wid=%s'%(Net,Dir,Wid))
            LL = list(Wid)
            LL[0]='packed'
            Mod.nets[Net]=Dir,LL
    
    for ind,Always  in enumerate(Mod.alwayses):
        if not Always[0]:
            scanForRegs.declareRegs(Mod,Always[1])
            Always = ['*',Always[1],Always[2]]
            Mod.alwayses[ind]=Always
        else:
            scanForRegs.declareRegs(Mod,Always[1])

    for ind,Gene  in enumerate(Mod.generates):
        if Gene[0] in ['if','ifelse','for']:
            scanForRegs.declareRegs(Mod,Gene)
        else:
            for Item in Gene:
                scanForRegs.declareRegs(Mod,Item)

    Wires = scanForRegs.scanForWires(Mod,False)
    for Reg in Mod.nets:
        Dir,_ = Mod.nets[Reg]
        if 'reg' in Dir:
            if Reg in Wires:
                logs.log_error('conflict reg/wire=%s'%(Reg))


    simplifyExpressions(Mod)
        
def getTypedefData(Mod,Def):
    Vars = matches.matches(Def[0],'enum logic ?')
    if Vars:
        for Item in Def[1]:
            Vars2 =  matches.matches(Item,'parameter ? ?')
            if Vars2:
                Mod.add_localparam(Vars2[0],Vars2[1])
            else:
                log.log_error('getTypedefData (parameter) failed on "%s"'%str(Item))
            
        return 'wire',Vars[0]
    logs.log_error('getTypedefData failed on "%s"'%str(Def))
    return 'wire',0
        

def simplifyExpressions(Mod):
    for ind,(Dst,Src,AA,BB) in enumerate(Mod.hard_assigns):
        Src0 = simplifyExpr(Src,Mod)
        Mod.hard_assigns[ind]=(Dst,Src0,AA,BB)
    for ind,Always in enumerate(Mod.alwayses):
        if Always[0]==[]: Always[0]='*'
        Body = simplifyExpr(Always[1],Mod)
        Mod.alwayses[ind]=[Always[0],Body,Always[2]]
    for ind,Gene in enumerate(Mod.generates):
        Body = []
        for Item in Gene:
            XX = simplifyExpr(Item,Mod)
            Body.append(Item)
        Mod.generates[ind]=Body


def simplifyExpr(Src,Mod):
    if type(Src)==types.StringType: 
        if packages_save and (Src in  packages_save.PARAMETERS):
            if Src not in Mod.localparams:
                Mod.localparams[Src]=packages_save.PARAMETERS[Src]

        return Src
    if type(Src)==types.IntType: return Src
    if Src==[]: return Src
    if Src[0] == 'question':
        Cond = simplifyExpr(Src[1],Mod)
        Yes = simplifyExpr(Src[2],Mod)
        No  = simplifyExpr(Src[3],Mod)
        return ['question',Cond,Yes,No]

    if (Src[0]=='functioncall')and(Src[1]=='$high'):
            Net = Src[2][0]
            Dir,Wid = Mod.nets[Net]
            return Wid[0]

    if Src[0]=='curly':
        Res = ['curly']
        for X in Src[1:]:
            Y = simplifyExpr(X,Mod)
            Res.append(Y)
        return Res
    if Src[0]=='subbit':
        return ['subbit',Src[1],simplifyExpr(Src[2],Mod)]
    if Src[0]=='subbus':
        return ['subbus',Src[1],[simplifyExpr(Src[2][0],Mod),simplifyExpr(Src[2][1],Mod)]]
    if Src[0] in ['taskcall','sub_slicebit','hex','dig','bin','functioncall','sub_slice','empty_begin_end','declare','instance']:
        return Src
    if (len(Src)==3)and(Src[0]=='==')and(complexType(Src[2]))and(Src[2][0]=='bin'):
        if str(Src[2][1])=='1':
            if str(Src[2][2])=='1':
                return Src[1]
            elif str(Src[2][2])=='0':
                return ['~',Src[1]]
                return Src[1]
    if (len(Src)==3)and(Src[0]=='==')and(not complexType(Src[2])):
        if str(Src[2]) == '1':
            return Src[1]
        if str(Src[2]) == '0':
            return ['~',Src[1]]

        
    if (len(Src)==2)and(Src[0] in ['|','&','^','-','!','~']):
        Y = simplifyExpr(Src[1],Mod)
        return [Src[0],Y]
        
    if (len(Src)>=3)and(Src[0] in ['**','>=','>','<','^','*','+','-','<<','<<<','>>','>>>','!=','==','&&','||','&','|']):
        res = [Src[0]]
        for X in Src[1:]:
            Y = simplifyExpr(X,Mod)
            res.append(Y)
        return res

    if Src[0]=='list':
        res = [Src[0]]
        for X in Src[1:]:
            Y = simplifyExpr(X,Mod)
            res.append(Y)
        return res
        
    if Src[0]=='named_begin':
        Src2 = simplifyExpr(Src[2],Mod)
        return ['named_begin',Src[1],Src2]
    if Src[0]=='=':
        Src2 = simplifyExpr(Src[2],Mod)
        return ['=',Src[1],Src2]
    if Src[0]=='<=':
        Src2 = simplifyExpr(Src[2],Mod)
        return ['<=',Src[1],Src2]
    if Src[0]=='if':
        Src1 = simplifyExpr(Src[1],Mod)
        Src2 = simplifyExpr(Src[2],Mod)
        return ['if',Src1,Src2]
    if Src[0]=='ifelse':
        Src1 = simplifyExpr(Src[1],Mod)
        Src2 = simplifyExpr(Src[2],Mod)
        Src3 = simplifyExpr(Src[3],Mod)
        return ['ifelse',Src1,Src2,Src3]
    if Src[0]=='unique_case':
        Src[0]='case'
        Srcx = simplifyExpr(Src,Mod)
        return Srcx
    if Src[0]=='case':
        res = []
        for Case in Src[2]:
            CondL,Stmnt = Case
            if complexType(CondL):
                Condl2=[]
                for Cond in CondL:
                    Condx = simplifyExpr(Cond,Mod)
                    Condl2.append(Condx)
            else:
                Condl2=CondL
            Stmnt = simplifyExpr(Stmnt,Mod)
            res.append([Condl2,Stmnt])
        return ['case',Src[1],res]
    if Src[0]=='assigns':
        Src[1] = simplifyExpr(Src[1],Mod)
        return Src
    if Src[0]=='for':
        Srcx = ['for',Src[1],simplifyExpr(Src[2],Mod),Src[3],simplifyExpr(Src[4],Mod)]
        return Srcx
    if Src[0]=='always':
        if Src[1]==[]: Src[1]='*'
        Src[2] =  simplifyExpr(Src[2],Mod)
        return Src
    if (len(Src)==1):
        return simplifyExpr(Src[0],Mod)
        
    if Src[0]=='genvar':
        return Src
    logs.log_error('simplify got src len=%d "%s"'%(len(Src),str(Src[0])))
    logs.pStack()
    return Src
def complexType(Expr):
    return type(Expr) in [types.TupleType,types.ListType]

def is_external_dir(Dir):
    for Cand in ['input','output','inout']:
        if Cand in Dir: return True
    return False


