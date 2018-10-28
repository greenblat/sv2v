
import string,types,logs
import module_class

def declareRegs(Mod,Struct):
    Regs = scanForRegs(Struct)
    for Net in Regs:
        if (type(Net)!=types.StringType)or(Net not in Mod.nets):
            if (Net not in Mod.parameters)and(Net not in Mod.localparams):
                logs.log_error('net not defined for declareRegs "%s"'%str(Net))
        else:
            Dir,Wid = Mod.nets[Net]
            if Dir=='wire':
                Mod.nets[Net] = ('reg',Wid)
            elif Dir=='output':
                Mod.nets[Net] = ('output reg',Wid)
            elif Dir=='reg':
                pass
            elif Dir=='integer':
                Mod.nets[Net] = ('reg',(31,0))
            else:
                logs.log_error('pacifierVerilog: net %s tried to be reg from "%s"'%(Net,Dir))

def scanForWires(Mod,Partial=False):
    Wires = []
    if not Partial:
        for Dst,_,_,_ in Mod.hard_assigns:
            Nets = module_class.support_set(Dst,False)
            for Net in Nets:
                if Net not in Wires: Wires.append(Net)
        
        for Gene  in Mod.generates:
            if Gene[0] in ['if','ifelse','for']:
                More = scanForWires(Mod,Gene)
                for Mo in More:
                    if Mo not in Wires: Wires.append(Mo)
            else:
                for Item in Gene:
                    More = scanForWires(Mod,Item)
                    for Mo in More:
                        if Mo not in Wires: Wires.append(Mo)

        return Wires

    if Partial[0] in ['if']:
        More = scanForWires(Mod,Partial[2])
        return More
    if Partial[0] in ['ifelse']:
        More = scanForWires(Mod,Partial[2])
        More1 = scanForWires(Mod,Partial[3])
        for M in More1: 
            if M not in More:
                More.append(M)
        return More
    if Partial[0] in ['for']:
        More = scanForWires(Mod,Partial[4])
        return More
    if Partial[0] in ['named_begin']:
        More = scanForWires(Mod,Partial[2])
        return More

    if Partial[0] in ['always']: return []
    if Partial[0] in ['list']:
        Wires = []
        for Item in Partial[1:]:
            More = scanForWires(Mod,Item)
            for Mo in More:
                 if Mo not in Wires: Wires.append(Mo)
        return Wires
    if Partial[0] in ['assigns']:
        return module_class.support_set(Partial[1][1],False)
    if Partial[0] in ['declare']:
        return []

    logs.log_error('partial %s not recognized'%(str(Partial[0])))
    return []


def scanForRegs(Struct):
    Regs=[]
    if (type(Struct) ==  types.ListType)and(len(Struct)==1):
        return scanForRegs(Struct[0])
    if Struct==[]: return []
    if complexType(Struct) and(Struct[0] in ['<=','=']):
        Nets = module_class.support_set(Struct[1],False)
        for Net in Nets:
            if Net not in Regs: Regs.append(Net)
        return Regs
    if (type(Struct) ==  types.ListType)and(Struct[0]=='list'):
        for Item in Struct:
            More = scanForRegs(Item)
            for Net in More:
                if Net not in Regs: Regs.append(Net)
        return Regs
    if complexType(Struct):
        if (Struct[0] in ['assigns','genvar','comment','declare','<','instance']):
            return []
        if (Struct[0]=='if'):
            return scanForRegs(Struct[2])
        if (Struct[0]=='always'):
            return scanForRegs(Struct[2])
        if (Struct[0]=='ifelse'):
            More = scanForRegs(Struct[2])+scanForRegs(Struct[3])
            for Net in More:
                if Net not in Regs: Regs.append(Net)
            return Regs
        if (Struct[0] in ['unique_case','case']):
            Struct[0] = 'case'
            LL = Struct[2]
            for Case in LL:
                PP = Case[1]
                More = scanForRegs(PP)
                for Net in More:
                    if Net not in Regs: Regs.append(Net)
            return Regs
        if (Struct[0]=='taskcall'): return []
        if (Struct[0]=='for'):
            Rs = module_class.support_set(Struct[1][1],False)
            More = scanForRegs(Struct[4])
            return Rs+More
        if (Struct[0]=='named_begin'):
            return scanForRegs(Struct[2])

        logs.log_error('scanForRegs encountered "%s"'%str(Struct))
        logs.pStack()
        
    if type(Struct) in [types.StringType,types.IntType]: return []

    logs.log_error('scanForRegs encountered "%s"'%str(Struct))
    return Regs

def complexType(Expr):
    return type(Expr) in [types.TupleType,types.ListType]


