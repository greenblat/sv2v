#! /usr/bin/python

import string,sys,os,types

def main():
    global Ofile
    Fname = sys.argv[1]
    try:
        File = open(Fname)
    except:
        print 'failed to open %s'%Fname
        return
    Ofile = open('lex.out','w')
    work(File)
#    print '>>>>',Queue
    work_out_queue(Queue,True)
    Ofile.close()

def work(File):
    LineNum=0
    while 1:
        line=File.readline()
        if len(line)==0:
            return
        LineNum+=1
        if len(line)>1:
            if ord(line[-2])==13:
                line=line[:-2]+chr(10)
            elif ord(line[-1])!=10:
                line = line+ chr(10)
#            print 'line',line,
            work_line(line,LineNum)

state='idle'
Token=''
def work_line(line,LineNum):
    global state,Token
    Len=len(line)
    for i in range(Len-1):
#        print 'try >>> %s %s %s %s'%(i,line[i],line[i+1],state)
        state,action,kind=stepit(i,line[i],line[i+1],state)
        if (action=='skipline'):
            state='idle'
            return
        if (action=='push'):
            Token=Token+line[i]
            push_token(Token,kind,LineNum,i)
            Token=''
        elif (action=='add'):
            Token=Token+line[i]
        elif (action!='none'):
            print state,action,kind,'error line=%d pos=%d chr="%s" line=||%s||'%(LineNum,i,line[i],line[:-1])
            sys.exit()
Queue=[]
def push_token(Token,kind,LineNum,LinePos):
#    print 'push_token    %s %s %s %s\n'%(Token,kind,LineNum,LinePos)
    if (kind=='token')and(Token in ReservedWords):
        kind=Token
    elif (kind=='define')and(Token in ReservedWords):
        kind='backtick_'+Token[1:]
    Queue.append((Token,kind,LineNum,LinePos))
    work_out_queue(Queue)

def work_out_queue(Queue,Flush=False):
    if (Flush):
        if Queue==[]:
            return
        Tup = Queue.pop(0)
        Tup = rework_tup(Tup)
        Ofile.write('%s %s %s %s\n'%Tup)
        work_out_queue(Queue,Flush)
    if (len(Queue)>=2)and(Queue[0][1]=='number')and(Queue[1][1] in ['uhex','ubin','udig']):
        Item = [Queue[0][0]+Queue[1][0],Queue[1][1][1:],Queue[0][2],Queue[0][3]]
        Queue[0]=tuple(Item)
        Queue.pop(1)

    if (len(Queue)>3):
        Tup = rework_tup(Queue.pop(0))
        Ofile.write('%s %s %s %s\n'%Tup)
        return
#    Ofile.write('%s %s %s %s\n'%(Token,kind,LineNum,LinePos))
            

def rework_tup(Tup):
    if Tup[1]=='single':
        List = list(Tup)
        List[1]=List[0]
        return tuple(List)
        
    if Tup[1]=='double':
        List = list(Tup)
        if (len(List[0])==1):
            List[1]=List[0]
            return tuple(List)
        List[1]=doublesName(List[0])
        return tuple(List)
    return Tup

DoubleNames = {}
DoubleNames['&&'] = 'and_and'
DoubleNames['=='] = 'eq_eq'
DoubleNames['!='] = 'not_eq'
DoubleNames['||'] = 'or_or'
DoubleNames['>='] = 'gr_eq'
DoubleNames['<='] = 'sm_eq'
DoubleNames['->'] = 'emit'
DoubleNames['!^'] = 'xnor'
DoubleNames['>>'] = 'shift_right'
DoubleNames['<<'] = 'shift_left'


def doublesName(Txt):
    if Txt in DoubleNames:
        return DoubleNames[Txt]
    else:
        print 'ilia! doubles names missing %s'%Txt
        return Txt


def stepit(Pos,Char,Char1,State):
    rule=0
    for (St,Ch0,Ch1,Next,Action,Kind) in Table:
        if (St==State):
#            print 'tryrule%d ch=%s ch1=%s in0=%d in1=%d st=%s ch0=%s ch1=%s next=%s act=%s kind=%s'%(rule,Char,Char1,(Char in Ch0),(Char1 in Ch1),State,Ch0,Ch1,Next,Action,Kind)
            rule +=1
            if (Ch0=='')or(Char in Ch0):
                if (Ch1=='')or(Char1 in Ch1):
                    return  Next,Action,Kind
    print 'no rule fits st=%s ch=%s ch1=%s'%(State,Char,Char1)
#    sys.exit()
    return 'idle','error',0
    
LowLetters = 'qwertyuiopasdfghjklzxcvbnm'
CapLetters = 'QWERTYUIOPASDFGHJKLZXCVBNM'
Letters = LowLetters+CapLetters
Digits='0123456789'
Alphas = Letters+Digits+'_'
HexDig = Digits+'abcdef'+'ABCDEF'+'_'+'xX'
BinDig = '01_xzXZ'
Singles = '?.,[]{}#@()~%^;:/+-*'
Doubles = '=!<>&|'
Doubles2 = '=<>&|'
Spaces = '\t '

LegalDoublesStr = '== != <= >= => =< && ||'
LegalDoubles = string.split(LegalDoublesStr)

Table = [
     ('idle',Spaces,'',             'idle','none',0)
    ,('idle','/','/',               'idle','skipline',0)
    ,('idle','/','*',               'comment','none',0)
    ,('comment','*','/',            'comment2','none',0)
    ,('comment2','/','',            'idle','none',0)
    ,('comment','','',              'comment','none',0)

    ,('idle','`',Letters,           'define','add',0)
    ,('define',Alphas,Alphas,       'define','add',0)
    ,('define',Alphas,'',           'idle','push','define')
    ,('idle',Letters+'$',Alphas,    'token','add',0)
    ,('token',Alphas,Alphas,        'token','add',0)
    ,('token',Alphas,'',            'idle','push','token')
    ,('idle',Letters,'',             'idle','push','token')

    ,('idle',Digits,Digits,         'number','add',0)
    ,('idle',Digits,'.',            'floating0','add',0)
    ,('idle',Digits,'',             'idle','push','number')
    ,('idle',"'",'b',               'ubin1','add',0)
    ,('idle',"'",'h',               'uhex1','add',0)
    ,('idle',"'",'d',               'udig1','add',0)
    ,('idle',"'",Digits,            'udig2','add',0)

    ,('number',Digits,Digits,       'number','add',0)
    ,('number',Digits,"'",          'sizednumber','add',0)
    ,('number',Digits,'.',          'floating0','add',0)
    ,('number',Digits,'',           'idle','push','number')
    ,('floating0','.',Digits,     'floating','add',0)
    ,('floating',Digits,Digits,     'floating','add',0)
    ,('floating',Digits,'',         'idle','push','floating')

    ,('sizednumber',"'",'b',          'bin1','add',0)
    ,('sizednumber',"'",'h',          'hex1','add',0)
    ,('sizednumber',"'",'d',          'dig1','add',0)

    ,('bin1','b',BinDig,         'bin2','add',0)
    ,('hex1','h',HexDig,         'hex2','add',0)
    ,('dig1','d',Digits,         'dig2','add',0)

    ,('dig2',Digits,Digits,         'dig2','add',0)
    ,('dig2',Digits,'',             'idle','push','dig')

    ,('hex2',HexDig,HexDig,         'hex2','add',0)
    ,('hex2',HexDig,'',              'idle','push','hex')

    ,('bin2',BinDig,BinDig,         'bin2','add',0)
    ,('bin2',BinDig,'',              'idle','push','bin')


    ,('ubin1','b',BinDig,         'ubin2','add',0)
    ,('uhex1','h',HexDig,         'uhex2','add',0)
    ,('udig1','d',Digits,         'udig2','add',0)

    ,('udig2',Digits,Digits,         'udig2','add',0)
    ,('udig2',Digits,'',             'idle','push','udig')

    ,('uhex2',HexDig,HexDig,         'uhex2','add',0)
    ,('uhex2',HexDig,'',              'idle','push','uhex')

    ,('ubin2',BinDig,BinDig,         'ubin2','add',0)
    ,('ubin2',BinDig,'',              'idle','push','ubin')



    ,('idle',Singles,'',             'idle','push','single')

    ,('idle','=','=',             'eqeq2','add',0)
    ,('eqeq2','=','=',             'eqeq3','add',0)
    ,('eqeq3','=','',             'idle','push','double')
    ,('eqeq2','=','',             'idle','push','double')

    ,('idle','!','=',             'neq2','add',0)
    ,('neq2','=','=',             'neq3','add',0)
    ,('neq3','=','',              'idle','push','double')
    ,('neq2','=','',              'idle','push','double')



    ,('idle',Doubles,Doubles2,        'double','add',0)
    ,('double',Doubles,'',           'idle','push','double')

    ,('idle',Doubles,'',       'idle','push','double')
    ,('idle','"','',                  'string','add',0)
    ,('string','"','',                'idle','push','string')
    ,('string','','',                'string','add',0)
]

ReservedWordsStr = '''
    `define `include `ifdef `ifndef `endif
    module endmodule primitive endprimitive function endfunction
    task endtask
    generate endgenerate genvar
    table endtable
    signed input output inout wire logic enum reg
    unique
    always begin end

assign deassign
force release

fork join join_any join_none
specify specparam defparam endspecify

vectored
repeat

tri tri0 tri1 wand trireg
supply0 supply1
wait
case
casex
casez
endcase
default
forever
always_ff
always_comb
always_latch
property
endproperty
sequence
endsequence
assert
_unique
_priority
or
if
else
parameter
for
while
initial
endprimitive
strong1 strong0 pull1 pull0 weak1 weak0 highz1 highz0
posedge negedge
integer real time
event
disable
localparam
    
class
rand
bit
endclass
constraint
enum
typedef
covergroup
endgroup
coverpoint
cross
bins
iff
new
with
semaphore
randomize
extends
mailbox
'''

ReservedWords = string.split(ReservedWordsStr)


main()

AFTERS = '''
        if (token==qqai("`define")) return Define;
        if (token==qqai("`undef")) return Define;
        if (token==qqai("`protect")) return Verilog_shtuiot;
        if (token==qqai("`endprotect")) return Verilog_shtuiot;
        if (token==qqai("`include")) return Include;
        if (token==qqai("`ifdef")) return Ifdef;
        if (token==qqai("`else")) return Back_Else;
        if (token==qqai("`endif")) return Endif;
        if (token==qqai("`timescale")) return Timescale;
        if (token==qqai("`resetall")) return Verilog_shtuiot;
        if (token==qqai("`celldefine")) return Verilog_shtuiot;
        if (token==qqai("`endcelldefine")) return Verilog_shtuiot;
        if (token==qqai("`suppress_faults")) return Verilog_shtuiot;
        if (token==qqai("`nosuppress_faults")) return Verilog_shtuiot;
        if (token==qqai("`enable_portfaults")) return Verilog_shtuiot;
        if (token==qqai("`disable_portfaults")) return Verilog_shtuiot;
        return Defined;

int specific_ver_double(long token) 
{

    if (token==qqai("Timeunit")) return Timeunit;
    if (token==qqai("&=")) return Andeq;
    if (token==qqai("|=")) return Oreq;
    if (token==qqai("+=")) return Pluseq;
    if (token==qqai("-=")) return Minuseq;
    if (token==qqai("||")) return Twoline;
    if (token==qqai("&&")) return Andand;
    if (token==qqai("<<")) return ShiftLeft;
    if (token==qqai(">>")) return ShiftRight;
    if (token==qqai("->")) return Emit;
    if (token==qqai("*>")) return StarMore;
    if (token==qqai("+:")) return PlusDots;
    if (token==qqai("-:")) return MinusDots;
    if (token==qqai("===")) return Veryequal;
    if (token==qqai("==")) return Equal;
    if (token==qqai("!=")) return Notequal;
    if (token==qqai("!==")) return Notequalequal;
    if (token==qqai("<=")) return Lessequal;
    if (token==qqai(">=")) return Moreequal;
    if (token==qqai("=<")) return Lessequal;
    if (token==qqai("=>")) return Moreequal;
    if (token==qqai("~^")) return Xnor;
    if (token==qqai("===")) return Andandand;
    if (token==qqai("++")) return PlusPlus;
    if (token==qqai("--")) return MinusMinus;
    if (token==qqai("**")) return StarStar;
    
}    

'''


