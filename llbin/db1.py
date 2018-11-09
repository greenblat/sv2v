#! /usr/bin/python


import os,sys,string,pickle,types
BIOPS = string.split('> < + == - * / !=')


import logs 
import traceback
import module_class as mcl
import matches
import pprint

class packagesClass:
    def __init__(self):
        self.TYPEDEFS  = {} 
        self.PARAMETERS  = {} 


if os.path.exists('packages_save.py'):
    sys.path.append('.')
    import packages_save
else:
    packages_save = packagesClass()



def main():
    load_parsed('.')
#    dump_all_verilog('all.v')
#    dump_all_all()
#    if PackFile: 
#        PackFile.write('endmodule\n')
#        PackFile.close()
#        Pack2File.close()

Modules = {} 

def dumpDataBase(db):
    Keys = db.keys()
    Keys.sort()
    Fout = open('database.dump','w')
    for Key in Keys:
        Fout.write('db %s %s\n'%(Key,db[Key]))

def dump_all_verilog(Fname):
    Fout = open(Fname,'w')
    for Mod in Modules:
        logs.log_info('dumping %s'%Mod)
        Modules[Mod].dump_verilog(Fout)
    Fout.close()

def dump_all_all():
    for Mod in Modules:
        logs.log_info('dumping %s'%Mod)
        Modules[Mod].dump()


def load_parsed(Rundir):
    db.Modules={}
    db.Global = mcl.module_class('global_module')
    try:
        load_db1('%s/db0.pickle'%Rundir)
        Key = 'Main',1
        dumpDataBase(db.db)
        scan1(Key)
        return Modules
    except:
        load_db1('db0.pickle')
        Key = 'Main',1
        scan1(Key)
        logs.log_fatal('reading file probably failed on syntax')
        return {}

class dataBaseClass:
    def __init__(self):
        self.db = False
        self.Modules = {}
        self.Global = False

db = dataBaseClass()

def load_db1(Fname):
    File = open(Fname)
    db.db = pickle.load(File)
    File.close()


def scan1(Key):
    if Key not in db.db: return
    List = db.db[Key]
    if List==[]: return

    if (len(List)==1)and(List[0] in db.db):
        scan1(List[0])
        return

    if Key[0] in ['Localparam','Function','Typedef']:
        logs.log_error('please treat key=%s list=%s'%(Key,List))
        return


    Vars = matches.matches(List,'module ? !Hparams !Header !Module_stuffs endmodule')
    if Vars:
        L1 = get_list(db.db[Vars[1]])
        L2 = get_list(db.db[Vars[2]])
        L3 = get_list(db.db[Vars[3]])
        print 'l1',L1,L2,L3
        return

    logs.log_error('scan1 failed on "%s" "%s"'%(Key,List))


def get_list(Item):
    return get_list__(Item)


def get_list__(Item):
    if (type(Item)==types.ListType)and(len(Item)==1):
        return get_list(Item[0])
    if (type(Item)==types.TupleType)and(len(Item)==4):
        return [Item[0]]
    if (type(Item)==types.ListType)and(len(Item)==0):
        return []

    if inDb(Item):
        List = db.db[Item]
        if List==[]: return []
        return get_list(List)
    Vars = matches.matches(Item,'( !Header_list ) ;')
    if Vars:
        return get_list(Vars[0])
    Vars = matches.matches(Item,'!Header_list , !Header_item')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'( !Hparams ) ;')
    if Vars:
        return get_list(Vars[0])

    Vars = matches.matches(Item,'!Module_stuffs')
    if Vars:
        return get_list(Vars[0])

    Vars = matches.matches(Item,'!Mstuff !Module_stuffs')
    if Vars:
        A =  get_list(db.db[Vars[0]])
        B =  get_list(db.db[Vars[1]])
        return A+B


    Vars = matches.matches(Item,'? ? ( !Conns_list ) ;')
    if Vars:
        Conns = get_list(db.db[Vars[2]])
        return [('instance',Vars[0][0],Vars[1][0],Conns)]
    Vars = matches.matches(Item,'!Conns_list , !Connection')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'. ? ( !Expr )')
    if Vars:
        Expr = get_list(db.db[Vars[1]])
        return [('conn',Vars[0][0],Expr)]

    Vars = matches.matches(Item,'[ !Expr : !Expr ]')
    if Vars:
        Expr0 = get_list(db.db[Vars[0]])
        Expr1 = get_list(db.db[Vars[1]])
        return [('range',Expr0,Expr1)]

    Vars = matches.matches(Item,'? , !Tokens_list')
    if Vars:
        Sig = Vars[0][0]
        Sigs = get_list(db.db[Vars[1]])
        return [Sig]+Sigs

    Vars = matches.matches(Item,'!IntDir !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Sigs = get_list(db.db[Vars[1]])
        return []

    Vars = matches.matches(Item,'!IntDir !Width !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return []

    Vars = matches.matches(Item,'!ExtDir ?')
    if Vars:
        Sig = Vars[1][0]
        Dir = get_list(db.db[Vars[0]])
        return [('extdir',Dir,Sig)]

    Vars = matches.matches(Item,'!PureExt !IntKind')
    if Vars:
        Dir0 = get_list(db.db[Vars[0]])
        Dir1 = get_list(db.db[Vars[1]])
        return [('dualdir',Dir0,Dir1)]


    Vars = matches.matches(Item,'!ExtDir !Width !Tokens_list')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return []

    Vars = matches.matches(Item,'!ExtDir !Width ?')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sig = Vars[2][0]
        return [('extdir',Dir,Wid,Sig)]

    Vars = matches.matches(Item,'!ExtDir !Width !Width ?')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid0 = get_list(db.db[Vars[1]])
        Wid1 = get_list(db.db[Vars[2]])
        Sig = Vars[3][0]
        return [('extdir',Dir,Wid0,Wid1,Sig)]



    Vars = matches.matches(Item,'assign !LSH = !Expr ;')
    if Vars:
        return []

    Vars = matches.matches(Item,'!AlwaysKind  !When !Statement')
    if Vars:
        Kind = get_list(db.db[Vars[0]])
        When = get_list(db.db[Vars[1]])
        Stmt = get_list(db.db[Vars[2]])
        return [('always',Kind,When,Stmt)]

    Vars = matches.matches(Item,'@ ( !When_items )')
    if Vars:
        When = get_list(db.db[Vars[0]])
        return [('when',When)]

    Vars = matches.matches(Item,'!When_items !Or_coma !When_item')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[2]])
        return [('when_or',A,B)]

    Vars = matches.matches(Item,'posedge !Expr')
    if Vars:
        A = get_list(db.db[Vars[0]])
        return [('posedge',A)]

    Vars = matches.matches(Item,'negedge !Expr')
    if Vars:
        A = get_list(db.db[Vars[0]])
        return [('negedge',A)]


    Vars = matches.matches(Item,'begin !Statements end')
    if Vars:
        Stmts = get_list(db.db[Vars[0]])
        return Stmts

    Vars = matches.matches(Item,'if ( !Expr )  !Statement else !Statement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        No  = get_list(db.db[Vars[2]])
        return [('ifelse',Cond,Yes,No)]

    Vars = matches.matches(Item,'if ( !Expr )  !Statement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        return [('if',Cond,Yes)]

    Vars = matches.matches(Item,'! !Expr')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        return [('!',Cond)]

    Vars = matches.matches(Item,'!Expr ? !Expr')
    if Vars:
        if Vars[1][0] in BIOPS:
            Exp0 = get_list(db.db[Vars[0]])
            Exp1 = get_list(db.db[Vars[2]])
            return [(Vars[1][0],Exp0,Exp1)]

    Vars = matches.matches(Item,'!LSH sm_eq !Expr ;')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        Expr = get_list(db.db[Vars[1]])
        return [('assignsm',LSH,Expr)]

    Vars = matches.matches(Item,'!Expr  ?  !Expr : !Expr')
    if Vars:
        if (Vars[1][0]=='?'):
            Cond = get_list(db.db[Vars[0]])
            Yes = get_list(db.db[Vars[2]])
            No = get_list(db.db[Vars[3]])
            return [('question',Cond,Yes,No)]

    Vars = matches.matches(Item,'# ( !head_params )')
    if Vars:
        LL = get_list(db.db[Vars[0]])
        return [('params',LL)]




    logs.log_err('get_list %s'%str(Item))
    logs.pStack()
    return []


def inDb(Item):
    return (type(Item)==types.TupleType)and(len(Item)==2)and(Item in db.db)



if __name__=='__main__':
    main()


