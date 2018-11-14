#! /usr/bin/python


import os,sys,string,pickle,types
BIOPS = string.split('! ~ > < + == - * / != | || & && << >> >= <= ^ >>> <<<  inside **')


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

def dumpScanned(db):
    File = open('scanned.dump','w')
    for Item in db.Scanned:
        Kind = Item[0]
        Name = Item[1]
        if Kind=='module':
            Str = '%s %s lens = io=%d prm=%d stuff=%d'%(Kind,Name,len(Item[2]),len(Item[3]),len(Item[4]))
            File.write('%s\n'%Str)
            print Str
            for X in Item[2]:
                File.write('item2 : %s\n'%(str(X)))
            for X in Item[3]:
                File.write('item3 : %s\n'%(str(X)))
            for X in Item[4]:
                File.write('item4 : %s\n'%(str(X)))
        elif Kind=='package':
            Str = '%s %s lens = stuff=%d'%(Kind,Name,len(Item[2]))
            File.write('%s\n'%Str)
            print Str
            for X in Item[2]:
                File.write('item2 : %s\n'%(str(X)))
                
    File.close()


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
    db.Global = mcl.module_class('global_module')
    try:
        load_db1('%s/db0.pickle'%Rundir)
        Key = 'Main',1
        dumpDataBase(db.db)
        scan1(Key)
        dumpScanned(db)
    except:
        load_db1('db0.pickle')
        Key = 'Main',1
        scan1(Key)
        dumpScanned(db)
        logs.log_fatal('reading file probably failed on syntax')
    logs.log_info('total matches run %s'%matches.totalcount)
    matches.reportIt()
    return db


class dataBaseClass:
    def __init__(self):
        self.db = False
        self.Modules = {}
        self.Global = False
        self.Scanned = []

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

    if Key[0] in ['Parameter','Localparam','Function','Typedef']:
        logs.log_error('please treat key=%s list=%s'%(Key,List))
        return

    Vars = matches.matches(List,'define ?t ?t / ?t ?t',True)
    if Vars:
        return []
    Vars = matches.matches(List,'!Mains !MainItem')
    if Vars:
        scan1(Vars[0])
        scan1(Vars[1])
        return

    Vars = matches.matches(List,'module ?t !Hparams !Header !Module_stuffs endmodule')
    if Vars:
        L1 = get_list(db.db[Vars[1]])
        L2 = get_list(db.db[Vars[2]])
        L3 = get_list(db.db[Vars[3]])
        db.Scanned.append(('module',Vars[0],L1,L2,L3))
        return
    Vars = matches.matches(List,'package ?t ; !PackageStuff endpackage')
    if Vars:
        LL = get_list(db.db[Vars[1]])
        db.Scanned.append(('package',Vars[0],LL))
        return
    Vars = matches.matches(Item,'define ?t ?t / ?t ?t',True)
    if Vars:
        return []

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
    Vars = matches.matches(Item,'!Statements !Statement')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!LSH ?t !Expr ;')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        Expr = get_list(db.db[Vars[2]])
        return [(Vars[1],LSH[0],Expr[0])]

    Vars = matches.matches(Item,'!Expr ?t !Expr')
    if Vars:
        if Vars[1] in BIOPS:
            Exp0 = get_list(db.db[Vars[0]])
            Exp1 = get_list(db.db[Vars[2]])
            return [(Vars[1],Exp0[0],Exp1[0])]

    Vars = matches.matches(Item,'assign !LSH = !Expr ;')
    if Vars:
        LSH = get_list(Vars[0])
        Expr = get_list(Vars[1])
        return [('hard_assign',LSH[0],Expr[0])]

    Vars = matches.matches(Item,'begin !Statements end')
    if Vars:
        Stmts = get_list(db.db[Vars[0]])
        return Stmts

    Vars = matches.matches(Item,'!CurlyItems , !CurlyItem')
    if Vars:
        Items = get_list(Vars[0])
        Item = get_list(Vars[1])
        return Items+Item

    Vars = matches.matches(Item,'{  !CurlyItems }')
    if Vars:
        Items = get_list(Vars[0])
        return [('curly',Items)]

    Vars = matches.matches(Item,'!Cases !Case')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!Exprs2 : !Statement')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return [('caseitem',A[0],B[0])]

    Vars = matches.matches(Item,'if ( !Expr )  !Statement else !Statement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        No  = get_list(db.db[Vars[2]])
        return [('ifelse',Cond,Yes,No)]

    Vars = matches.matches(Item,'?t !Expr')
    if Vars:
        if Vars[0] in BIOPS:
            Cond = get_list(db.db[Vars[1]])
            return [(Vars[0],Cond[0])]

    Vars = matches.matches(Item,'if ( !Expr )  !Statement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        return [('if',Cond,Yes)]

    Vars = matches.matches(Item,'. ?t ( !Expr )')
    if Vars:
        Expr = get_list(db.db[Vars[1]])
        return [('conn',Vars[0],Expr[0])]

    Vars = matches.matches(Item,'[ !Expr : !Expr ]')
    if Vars:
        Expr0 = get_list(db.db[Vars[0]])
        Expr1 = get_list(db.db[Vars[1]])
        return [('range',Expr0[0],Expr1[0])]

    Vars = matches.matches(Item,'!Conns_list , !Connection')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'?t ?t')
    if Vars:
        return [('define',Vars[0],Vars[1])]

    Vars = matches.matches(Item,'!Expr  ?  !Expr : !Expr')
    if Vars:
        if (Vars[1][0]=='?'):
            Cond = get_list(db.db[Vars[0]])
            Yes = get_list(db.db[Vars[2]])
            No = get_list(db.db[Vars[3]])
            return [('question',Cond[0],Yes[0],No[0])]




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

    Vars = matches.matches(Item,'?t ( !Exprs )')
    if Vars:
        Exprs = get_list(Vars[1])
        return [('funccall',Vars[0],Exprs)]
    Vars = matches.matches(Item,'?t ( !Exprs ) ;')
    if Vars:
        Exprs = get_list(Vars[1])
        return [('taskcall',Vars[0],Exprs)]


    Vars = matches.matches(Item,'?t ?t ( !Conns_list ) ;')
    if Vars:
        Conns = get_list(db.db[Vars[2]])
        return [('instance',Vars[0],Vars[1],Conns)]

    Vars = matches.matches(Item,'?t !InstParams ?t ( !Conns_list ) ;')
    if Vars:
        Prms  = get_list(db.db[Vars[1]])
        Conns = get_list(db.db[Vars[3]])
        return [('instance',Vars[0],Vars[2],Prms[0],Conns)]

    Vars = matches.matches(Item,'functions !WidthInt ?t ;')
    if Vars:
        Wid = get_list(db.db(Vars[0]))
        return [('function',Wid[0],Vars[1])]
        

    Vars = matches.matches(Item,'!Funcheader !Mem_defs !Statements endfunction !Maybe')
    if Vars:
        Head = get_list(db.db[Vars[0]])
        Mems = get_list(db.db[Vars[1]])
        Stmts = get_list(db.db[Vars[2]])
        return [('funcdef',Head,Mems,Stmts)]

    Vars = matches.matches(Item,'# !Expr ;')
    if Vars:
        Expr = get_list(db.db[Vars[0]])
        return [('#',Expr[0])]

    Vars = matches.matches(Item,'# !Expr !Statement')
    if Vars:
        Expr = get_list(db.db[Vars[0]])
        Stmt = get_list(db.db[Vars[1]])
        return [('delay',Expr[0],Stmt[0])]
    Vars = matches.matches(Item,'# ( !Prms_list )')
    if Vars:
        Prms = get_list(Vars[0])
        return [('prms',Prms[0])]
    Vars = matches.matches(Item,'!Prms_list , !PrmAssign')
    if Vars:
        Prms = get_list(Vars[0])
        Prm = get_list(Vars[1])
        return [Prms+Prm]


    Vars = matches.matches(Item,'?t !BusBit !Width')
    if Vars:
        Ind = get_list(Vars[1])
        Wid = get_list(Vars[3])
        return [('subbus',Vars[0],Ind[0],Wid[0])]

    Vars = matches.matches(Item,'?t !BusBit . ?t !Width')
    if Vars:
        Ind = get_list(Vars[1])
        Wid = get_list(Vars[3])
        return [('record_slice',Vars[0],Ind[0],Vars[2],Wid[0])]

    Vars = matches.matches(Item,'?t !BusBit . ?t')
    if Vars:
        Ind = get_list(Vars[1])
        return [('record_slice',Vars[0],Ind,Vars[2])]
        

    Vars = matches.matches(Item,'?t !BusBit')
    if Vars:
        Ind = get_list(Vars[1])
        return [('subbit',Vars[0],Ind[0])]

    Vars = matches.matches(Item,'?t !BusBit !BusBit')
    if Vars:
        Bus0 = get_list(Vars[1])
        Bus1 = get_list(Vars[2])
        return [('subbit',Vars[0],Bus0[0],Bus1[0])]



    Vars = matches.matches(Item,'?t !Width')
    if Vars:
        Wid = get_list(Vars[1])
        return [('subbus',Vars[0],Wid[0])]

    Vars = matches.matches(Item,'. *')
    if Vars:
        return [('conn','*')]
    Vars = matches.matches(Item,'. ?t')
    if Vars:
        return [('conn',Vars[0],Vars[0])]
        
    Vars = matches.matches(Item,'[ !Expr ]')
    if Vars:
        Expr = get_list(db.db[Vars[0]])
        return [('square',Expr[0])]

    Vars = matches.matches(Item,'( !Expr )')
    if Vars:
        Expr = get_list(db.db[Vars[0]])
        return [('expr',Expr)]

    Vars = matches.matches(Item,'!Exprs , !Expr')
    if Vars:
        Expr0 = get_list(db.db[Vars[0]])
        Expr1 = get_list(db.db[Vars[1]])
        return Expr0+Expr1

    Vars = matches.matches(Item,'!Mem_defs !Mem_def')
    if Vars:
        Expr0 = get_list(db.db[Vars[0]])
        Expr1 = get_list(db.db[Vars[1]])
        return Expr0+Expr1

    Vars = matches.matches(Item,'. ?t ( )')
    if Vars:
        return [('conn',Vars[0],False)]


    Vars = matches.matches(Item,'? , !Tokens_list')
    if Vars:
        Sig = Vars[0][0]
        Sigs = get_list(db.db[Vars[1]])
        return [Sig]+Sigs

    Vars = matches.matches(Item,'!IntDir ?t ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        return [('define',Dir[0],Vars[1])]

    Vars = matches.matches(Item,'!IntDir !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Sigs = get_list(db.db[Vars[1]])
        return [('define',Dir[0],Sigs)]

    Vars = matches.matches(Item,'?t !Width !Tokens_list ;')
    if Vars:
        Dir = Vars[0]
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return [('define',Dir,Wid[0],Sigs)]

    Vars = matches.matches(Item,'logic !Width ?t = !Expr')
    if Vars:
        Dir = 'logic'
        Wid = get_list(db.db[Vars[0]])
        Sig = Vars[1]
        Expr = get_list(db.db[Vars[2]])
        return [('define',Dir,Wid[0],Sig),('soft_assign',Sig,Expr[0])]

    Vars = matches.matches(Item,'!IntDir !Tokens_list = !Expr ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Sigs = get_list(db.db[Vars[1]])
        Expr = get_list(db.db[Vars[2]])
        return [('define',Dir[0],Sigs),('hard_assign',Sigs[0],Expr[0])]

    Vars = matches.matches(Item,'integer ?t = !Expr ;')
    if Vars:
        Sig = Vars[0]
        Expr = get_list(db.db[Vars[2]])
        return [('define','integer',Sigs),('hard_assign',Sig,Expr[0])]

    Vars = matches.matches(Item,'integer ?t = !Expr')
    if Vars:
        Sig = Vars[0]
        Expr = get_list(db.db[Vars[1]])
        return [('define','integer',Sig),('hard_assign',Sig,Expr[0])]


    Vars = matches.matches(Item,'!IntDir !Width ?t !Width ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid1 = get_list(db.db[Vars[1]])
        Wid2 = get_list(db.db[Vars[3]])
        Net = Vars[2]
        return [('ram',Dir[0],Wid1[0],Net,Wid2[0])]


    Vars = matches.matches(Item,'!IntDir !Width ?t !BusBit ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid1 = get_list(db.db[Vars[1]])
        Wid2 = get_list(db.db[Vars[3]])
        Net = Vars[2]
        return [('ram',Dir[0],Wid1[0],Net,Wid2[0])]
    Vars = matches.matches(Item,'!IntDir !Width !Width !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid1 = get_list(db.db[Vars[1]])
        Wid2 = get_list(db.db[Vars[2]])
        Nets = get_list(db.db[Vars[3]])
        return [('packed',Dir[0],Wid1[0],Nets[0],Wid2[0])]


    Vars = matches.matches(Item,'!IntDir !Width !Tokens_list = !Expr ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        Expr = get_list(db.db[Vars[3]])
        return [('define',Dir[0],Wid[0],Sigs),('hard_assign',Sigs[0],Expr[0])]




    Vars = matches.matches(Item,'!IntDir !Width !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return [('intdir',Dir[0],Wid[0],Sigs)]

    Vars = matches.matches(Item,'!IntDir !Width ?t ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        return [('intdir',Dir[0],Wid[0],Vars[2])]

    Vars = matches.matches(Item,'!ExtDir ?t')
    if Vars:
        Sig = Vars[1]
        Dir = get_list(db.db[Vars[0]])
        return [('extdir',Dir[0],Sig)]

    Vars = matches.matches(Item,'!ExtDir ?t ;')
    if Vars:
        Sig = Vars[1]
        Dir = get_list(db.db[Vars[0]])
        return [('extdir',Dir[0],Sig)]

    Vars = matches.matches(Item,'!PureExt !IntKind')
    if Vars:
        Dir0 = get_list(db.db[Vars[0]])
        Dir1 = get_list(db.db[Vars[1]])
        return ['%s %s'%(Dir0[0],Dir1[0])]

    Vars = matches.matches(Item,'!PureExt !IntKind signed')
    if Vars:
        Dir0 = get_list(db.db[Vars[0]])
        Dir1 = get_list(db.db[Vars[1]])
        return ['%s %s %s'%(Dir0[0],Dir1[0],'signed')]

    Vars = matches.matches(Item,'!PureExt signed')
    if Vars:
        Dir0 = get_list(db.db[Vars[0]])
        return ['%s %s'%(Dir0[0],'signed')]



    Vars = matches.matches(Item,'!ExtDir !Width !Tokens_list')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return [('extdir',Dir[0],Wid[0],Sigs)]


    Vars = matches.matches(Item,'!ExtDir !Width !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sigs = get_list(db.db[Vars[2]])
        return [('extdir',Dir[0],Wid[0],Sigs)]

    Vars = matches.matches(Item,'!ExtDir !Tokens_list ;')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Sigs = get_list(db.db[Vars[1]])
        return [('extdir',Dir[0],Sigs)]



    Vars = matches.matches(Item,'!ExtDir ?t ?t')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        return [('extdir',Dir[0],Vars[1],Vars[2])]

    Vars = matches.matches(Item,'!ExtDir !Width ?t')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sig = Vars[2]
        return [('extdir',Dir[0],Wid[0],Sig)]

    Vars = matches.matches(Item,'!ExtDir ?t !Width ?t')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[2]])
        Sig = Vars[3]
        return [('extdir',Dir[0],Vars[1],Wid[0],Sig)]
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid = get_list(db.db[Vars[1]])
        Sig = Vars[2]
        return [('extdir',Dir[0],Wid[0],Sig)]
    Vars = matches.matches(Item,'!ExtDir !Width !Width ?t')
    if Vars:
        Dir = get_list(db.db[Vars[0]])
        Wid0 = get_list(db.db[Vars[1]])
        Wid1 = get_list(db.db[Vars[2]])
        Sig = Vars[3]
        return [('extdir',Dir[0],Wid0[0],Wid1[0],Sig)]


    Vars = matches.matches(Item,'initial  !Statement')
    if Vars:
        Stmt = get_list(db.db[Vars[0]])
        return [('initial',Stmt)]
    Vars = matches.matches(Item,'!AlwaysKind  !Statement')
    if Vars:
        Kind = get_list(db.db[Vars[0]])
        Stmt = get_list(db.db[Vars[1]])
        return [('always',Kind[0],[],Stmt)]


    Vars = matches.matches(Item,'!AlwaysKind  !When !Statement')
    if Vars:
        Kind = get_list(db.db[Vars[0]])
        When = get_list(db.db[Vars[1]])
        Stmt = get_list(db.db[Vars[2]])
        return [('always',Kind[0],When[0],Stmt)]

    Vars = matches.matches(Item,'@ ( * )')
    if Vars:
        return [('when','*')]

    Vars = matches.matches(Item,'@ ( !When_items )')
    if Vars:
        When = get_list(db.db[Vars[0]])
        return [('when',When[0])]

    Vars = matches.matches(Item,'!When_items !Or_coma !When_item')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[2]])
        LL = A+B
        return [('when_or',LL)]

    Vars = matches.matches(Item,'posedge !Expr')
    if Vars:
        A = get_list(db.db[Vars[0]])
        return [('posedge',A[0])]

    Vars = matches.matches(Item,'negedge !Expr')
    if Vars:
        A = get_list(db.db[Vars[0]])
        return [('negedge',A[0])]

    Vars = matches.matches(Item,'!InStmtType !Tokens_list ;')
    if Vars:
        Type = get_list(Vars[0])
        Sigs = get_list(Vars[1])
        return [('instmttype',Type[0],Sigs)]
    Vars = matches.matches(Item,'automatic logic !Width')
    if Vars:
        Wid = get_list(Vars[0])
        return [('logic',Wid[0])]
    Vars = matches.matches(Item,'automatic logic')
    if Vars:
        return ['logic']

    Vars = matches.matches(Item,'begin : ?t !GenStatements end')
    if Vars:
        Stmts = get_list(db.db[Vars[1]])
        return [('named_begin',Vars[0],Stmts)]
    Vars = matches.matches(Item,'begin !GenStatements end')
    if Vars:
        Stmts = get_list(db.db[Vars[0]])
        return [('begin',Stmts)]
        
    Vars = matches.matches(Item,'begin : ?t !Statements end')
    if Vars:
        Stmts = get_list(db.db[Vars[1]])
        return [('named_begin',Vars[0],Stmts)]
        


    Vars = matches.matches(Item,'if ( !Expr )  !GenStatement else !GenStatement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        No  = get_list(db.db[Vars[2]])
        return [('genifelse',Cond,Yes,No)]



    Vars = matches.matches(Item,'if ( !Expr )  !GenStatement')
    if Vars:
        Cond = get_list(db.db[Vars[0]])
        Yes = get_list(db.db[Vars[1]])
        return [('gen_if',Cond,Yes)]




    Vars = matches.matches(Item,'!LSH plusplus')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        return [('plusplus',LSH)]
    Vars = matches.matches(Item,'!LSH minusminus')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        return [('minusminus',LSH)]
        
    Vars = matches.matches(Item,'!LSH plusplus ;')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        return [('plusplus',LSH)]
    Vars = matches.matches(Item,'!LSH minusminus ;')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        return [('minusminus',LSH)]


    Vars = matches.matches(Item,'!LSH ?t !Expr')
    if Vars:
        LSH = get_list(db.db[Vars[0]])
        Expr = get_list(db.db[Vars[2]])
        return [(Vars[1],LSH,Expr)]

    Vars = matches.matches(Item,'# ( !head_params )')
    if Vars:
        LL = get_list(db.db[Vars[0]])
        return [('params',LL)]

    Vars = matches.matches(Item,'# ( !Exprs )')
    if Vars:
        LL = get_list(db.db[Vars[0]])
        return [('params',LL)]

    Vars = matches.matches(Item,'!head_params , !head_param')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'parameter logic !Width ?t  = !Expr')
    if Vars:
        Wid = get_list(db.db[Vars[0]])
        Prm = Vars[1]
        Val = get_list(db.db[Vars[2]])
        return [('parameter',Wid[0],Prm,Val[0])]

    Vars = matches.matches(Item,'parameter integer ?t  = !Expr')
    if Vars:
        Prm = Vars[0]
        Val = get_list(db.db[Vars[1]])
        return [('parameter',Prm,Val[0])]
    Vars = matches.matches(Item,'parameter  ?t  = !Expr')
    if Vars:
        Prm = Vars[0]
        Val = get_list(db.db[Vars[1]])
        return [('parameter',Prm,Val[0])]

    Vars = matches.matches(Item,'?t  = !Expr')
    if Vars:
        Prm = Vars[0]
        Val = get_list(db.db[Vars[1]])
        return [('assign',Prm,Val[0])]

    Vars = matches.matches(Item,'unique case')
    if Vars:
        return ['unique case']
    Vars = matches.matches(Item,'parameter  !Pairs ;')
    if Vars:
        Params = get_list(db.db[Vars[0]])
        return [('parameters',Params)]
    Vars = matches.matches(Item,'localparam  !Pairs ;')
    if Vars:
        Params = get_list(db.db[Vars[0]])
        return [('localparams',Params)]
    Vars = matches.matches(Item,'localparam  integer !Pairs ;')
    if Vars:
        Params = get_list(db.db[Vars[0]])
        return [('localparams',Params)]

    Vars = matches.matches(Item,'!CaseKind ( !Expr ) !Inside  !Cases !Default endcase')
    if Vars:
        Case = get_list(db.db[Vars[0]])
        Key = get_list(db.db[Vars[1]])
        Cases = get_list(db.db[Vars[3]])
        Default = get_list(db.db[Vars[4]])
        Res =  [('case',Case[0],Key[0],Cases,Default[0])]
        return Res

    Vars = matches.matches(Item,'!CaseKind ( !Expr ) !Inside  !Cases endcase')
    if Vars:
        Case = get_list(db.db[Vars[0]])
        Key = get_list(db.db[Vars[1]])
        Cases = get_list(db.db[Vars[3]])
        return [('case',Case[0],Key[0],Cases)]


    Vars = matches.matches(Item,'!Pairs , !Pair')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!Pairs2 , !Pair2')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!Exprs2 , !Expr2')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!Tail , !Tails')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'?t : !Expr')
    if Vars:
        B = get_list(db.db[Vars[1]])
        return [('pair',Vars[0],B)]

    Vars = matches.matches(Item,'default : !Statement')
    if Vars:
        Stmt = get_list(Vars[0])
        return [('default',Stmt)]

    Vars = matches.matches(Item,'!Exprs2 : ;')
    if Vars:
        A = get_list(db.db[Vars[0]])
        return [('caseitem',A,False)]


    Vars = matches.matches(Item,'generate !GenStatements endgenerate')
    if Vars:
        Stmts = get_list(Vars[0])
        return [('generate',Stmts)]

    Vars = matches.matches(Item,'!GenStatements !GenStatement')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return [('genstmts',A+B)]

    Vars = matches.matches(Item,'genvar ?t ;')
    if Vars:
        return [('genvar',Vars[0])]
        
    Vars = matches.matches(Item,'genvar ?t = !Expr')
    if Vars:
        Expr = get_list(db.db[Vars[1]])
        return [('genvar',Vars[0],Expr[0])]



    Vars = matches.matches(Item,'assign !AssignParams !LSH = !Expr ;')
    if Vars:
        LSH = get_list(Vars[1])
        Params = get_list(Vars[0])
        Expr = get_list(Vars[2])
        return [('hard_assign',Params,LSH,Expr)]


    Vars = matches.matches(Item,'!Expr  !CurlyList')
    if Vars:
        Expr = get_list(db.db[Vars[0]])
        Curly = get_list(db.db[Vars[1]])
        return [('repeat',Expr[0],Curly[0])]




    Vars = matches.matches(Item,'!PackageStuff !PackageItem')
    if Vars:
        Items = get_list(Vars[0])
        Item = get_list(Vars[1])
        return Items+Item
        
    Vars = matches.matches(Item,'!SimpleDefs !SimpleDef')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B

    Vars = matches.matches(Item,'!usedDefs , !usedDef')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        return A+B
    Vars = matches.matches(Item,'for ( !Soft_assigns ; !Expr ; !Soft_assigns )   !Statement')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        C = get_list(db.db[Vars[2]])
        D = get_list(db.db[Vars[3]])
        return [('for',A,B,C,D)]

    Vars = matches.matches(Item,'for ( !Soft_assigns ; !Expr ; !Soft_assigns )   !GenStatement')
    if Vars:
        A = get_list(db.db[Vars[0]])
        B = get_list(db.db[Vars[1]])
        C = get_list(db.db[Vars[2]])
        D = get_list(db.db[Vars[3]])
        return [('genfor',A,B,C,D)]


    Vars = matches.matches(Item,'struct !maybePacked { !SimpleDefs } !maybeWidth !Tails ;')
    if Vars:
        Packed = get_list(db.db[Vars[0]])
        Defs = get_list(db.db[Vars[1]])
        Wid =  get_list(db.db[Vars[2]])
        Sigs =  get_list(db.db[Vars[3]])
        return [('struct',Defs,Wid,Sigs)]

    Vars = matches.matches(Item,'typedef struct { !SimpleDefs } !Typename ;')
    if Vars:
        Defs = get_list(Vars[0])
        Name = get_list(Vars[1])
        return [('typedefstruct',Name,Defs)]


    Vars = matches.matches(Item,'enum !WireLogic !Width { !Tokens_list } !Tokens_list ;')
    if Vars:
        WL = get_list(Vars[0])
        Wid = get_list(Vars[1])
        Toks = get_list(Vars[2])
        Sigs = get_list(Vars[3])
        return [('enum',WL[0],Wid[0],Toks,Sigs)]

    Vars = matches.matches(Item,'enum !WireLogic { !Tokens_list } !Tokens_list ;')
    if Vars:
        WL = get_list(Vars[0])
        Toks = get_list(Vars[1])
        Sigs = get_list(Vars[2])
        return [('enum',WL[0],Toks,Sigs)]

    Vars = matches.matches(Item,'typedef enum logic !Width { !Pairs } !Typename ;')
    if Vars:
        Wid = get_list(Vars[0])
        Pairs = get_list(Vars[1])
        Name = get_list(Vars[2])
        return [('typedef','enum',Name[0],Wid[0],Pairs)]

    Vars = matches.matches(Item,'?t !usedDefs ;')
    if Vars:
        useDefs = get_list(Vars[1])
        return [('usedefs',Vars[0],useDefs)]
    Vars = matches.matches(Item,'crazy1 default : !Consts }')
    if Vars:
        Consts = get_list(Vars[0])
        return [('consts',Consts)]

    Vars = matches.matches(Item,'crazy1 default : ?t }')
    if Vars:
        return [('consts',Vars[0])]

    Vars = matches.matches(Item,'crazy1 !Pairs2 }')
    if Vars:
        Pairs = get_list(Vars[0])
        return [('crazy1',Pairs)]
    Vars = matches.matches(Item,'?t crazy2 !Expr )')
    if Vars:
        Expr = get_list(Vars[1])
        return [('crazy2',Vars[0],Expr[0])]

    Vars = matches.matches(Item,'?t crazy2 !Expr )')
    if Vars:
        Expr = get_list(Vars[1])
        return [('crazy2',Vars[0],Expr[0])]

    Vars = matches.matches(Item,'logic crazy2 !Expr )')
    if Vars:
        Expr = get_list(Vars[1])
        return [('logic_crazy',Vars[0],Expr[0])]

    Vars = matches.matches(Item,'logic crazy2 ?t )')
    if Vars:
        return [('logic_crazy',Vars[0])]

    Vars = matches.matches(Item,'?t ?t ;')
    if Vars:
        return [('define',Vars[0],Vars[1])]

    Vars = matches.matches(Item,'{ << { ?t } }')
    if Vars:
        return [('pack',Vars[0])]
    Vars = matches.matches(Item,'{ !Width }',True)
    if Vars:
        Wid = get_list(Vars[0])
        return [('inside_range',Wid[0])]
    Vars = matches.matches(Item,'{ !Width , !Width }')
    if Vars:
        Wid0 = get_list(Vars[0])
        Wid1 = get_list(Vars[1])
        return [('inside_range',Wid0[0],Wid1[0])]





    logs.log_err('get_list %s'%str(Item))
    logs.pStack()
    return []


def inDb(Item):
    return (type(Item)==types.TupleType)and(len(Item)==2)and(Item in db.db)



if __name__=='__main__':
    main()


