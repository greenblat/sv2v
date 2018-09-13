
%token module number token endmodule assign 
%token input  output  inout reg  wire  tri0 tri1 signed  unsigned event logic enum const
%token bin hex dig integer real wreal
%token ubin uhex udig
%token domino and_and or_or eq3 eq_eq not_eq gr_eq sm_eq
%token always begin end if else posedge negedge or wait emit
%token always_comb always_ff always_latch
%token string defparam parameter localparam case casez casex unique endcase default initial forever
%token function endfunction task endtask
%token for while backtick_define backtick_include backtick_timescale backtick_undef define
%token  strong1  strong0  pull1  pull0  weak1  weak0  highz1  highz0 
%token fork join
%token disable
%token pragma
%token plus_range minus_range
%token floating
%token generate endgenerate  genvar
%token force release
%token xnor nand nor repeat
%token supply0 supply1
%token newver plusplus starstar shift3 crazy1

%right '?' ':' 
%left and_and
%left '|' 
%left '^' xnor nand nor
%left '&' 
%left  shift3 shift_left shift_right SignedLeft arith_shift_right
%left  or_or  
%left '<' '>' sm_eq gr_eq
%left '+' '-' 
%left eq3 eq_eq not_eq noteqeq Veryequal 
%left '*' '/' '%'  
%left starstar
%left UNARY_PREC

%nonassoc else


%%
Main : Mains ;
Mains : Mains MainItem | MainItem  ;
MainItem : Module | Define ;
Module : module token Hparams Header Module_stuffs endmodule

Hparams : '#' '(' head_params ')' |  '#' '(' ')' | ;
Header : ';' | '(' Header_list ')' ';' | '(' ')' ';' ;
Header_list : Header_list ',' Header_item | Header_item ;

Header_item : 
      ExtDir token 
    | ExtDir Width token 
    | ExtDir integer token 
    | ExtDir Width token  Width 
    | ExtDir Width token  BusBit 
    | ExtDir Width Width token   
    | token ;


Module_stuffs : Mstuff Module_stuffs | ;

Mstuff :
     Definition
    | Assign
    | Instance
    | Always
    | Generate
    | Parameter
    | Localparam
    | Defparam
    | Initial
    | Function
    | Task
    | Define
    | pragma
    | newver
    | if '(' Expr ')' GenStatement 
    | if '(' Expr ')' GenStatement else GenStatement 
    ;

// Define : backtick_undef token | backtick_define token Expr | backtick_include Expr | backtick_timescale  number token '/' number token  ;
Define : define string | define token | define token Expr | define  number token '/' number token  ;
Initial : initial Statement ;
Definition : 
     ExtDir Tokens_list ';'
    | event Tokens_list ';'
    | IntDir Tokens_list ';'
    | IntDir Tokens_list '=' Expr ';'
    | ExtDir Width Tokens_list ';'
    | ExtDir Width Tokens_list Width ';'
    | ExtDir Width Tokens_list BusBit ';'
    | IntDir Width Tokens_list ';'
    | IntDir Width Tokens_list '=' Expr ';'
    | IntDir Width token Width ';'
    | IntDir Width token BusBit ';'
    | IntDir Width Width Tokens_list ';'
    | IntDir token Width ';'
    | IntDir InstParams Tokens_list ';'
    | enum WireLogic Width '{' Tokens_list '}' Tokens_list ';'  
    | token domino token token ';'
    | const logic Width Width token '=' '{' Exprs '}' ';'
    ;


WireLogic : wire | logic ;

Assign : 
      assign LSH '=' Expr ';' 
    | assign AssignParams LSH '=' Expr ';' 
    | assign StrengthDef AssignParams LSH '=' Expr ';' 
    | assign StrengthDef LSH '=' Expr ';' 
    ;

StrengthDef :  '(' Strength ',' Strength ')' ;
Strength : strong1 | strong0 | pull1 | pull0 | weak1 | weak0 | highz1 | highz0 ;
WidthInt : Width | integer ;
Function : 
      function  token ';' Mem_defs Statements  endfunction
    | function  token ';' Statements  endfunction
    | function  WidthInt token ';' Mem_defs Statement  endfunction
    | function  WidthInt token ';' Statement  endfunction
    | function  token '(' Header_list ')' ';' Statement  endfunction
    | function  token '(' Header_list ')' ';' Mem_defs Statement  endfunction
    | function  WidthInt token '(' Header_list ')' ';' Statement  endfunction
    | function  WidthInt token '(' Header_list ')' ';' Mem_defs Statement  endfunction
    ; 
Task : 
      task token ';' Mem_defs  Statement endtask  
    | task token ';' Statement endtask  
    | task token '(' Header_list ')' ';' Statement endtask  
    | task token '(' Header_list ')' ';' Mem_defs Statement endtask  
    ;

Mem_defs : Mem_defs Mem_def | Mem_def ;
Mem_def  :
      reg Tokens_list ';'
    | real Tokens_list ';'
    | wreal Tokens_list ';'
    | reg Width Tokens_list ';'
    | reg Width token Width ';'
    | input Tokens_list ';'
    | input Tokens_list Width ';'
    | input Width Tokens_list ';'
    | input integer Tokens_list ';'
    | integer Tokens_list ';'
    | integer Tokens_list Width ';'
    ;

Parameter : 
      parameter Pairs ';' 
    | parameter signed Pairs ';'
    | parameter Width Pairs ';'
    | parameter signed Width Pairs ';'
    ;
Localparam : localparam Pairs ';' | localparam Width Pairs ';' ;
Defparam : defparam token '=' Expr ';' ;
Pairs : Pairs ',' Pair | Pair ;
Pair : token '=' Expr ;

head_params : head_params ',' head_param | head_param ;
head_param : 
    parameter token '=' Expr 
    | token '=' Expr 
    ;

Instance : 
      token token '(' ')' ';' 
    | token InstParams token '(' ')' ';' 
    | token token ';' 
    | or '(' Exprs ')' ';' 
    | token token '(' Conns_list ')' ';' 
    | token token '(' Exprs ')' ';' 
    | token InstParams token '(' Conns_list ')' ';' 
    | token InstParams token Width '(' Conns_list ')' ';' 
    | token token Width '(' Conns_list ')' ';'
    ;

// | token '(' Exprs ')' ';' 


Crazy : crazy1 default ':' Consts '}' ;


Conns_list : Conns_list ',' Connection | Connection ;
Connection : '.' '*' | '.' token '(' Expr ')' | '.' token '(' ')' ;

AssignParams : '#' '(' Exprs ')' | '#' number | '#' token | '#' floating ;
Prms_list : Prms_list ',' PrmAssign | PrmAssign ;
PrmAssign :  '.' token '(' Expr ')' | '.' token ;
InstParams : '#' '(' Exprs ')' | '#' number | '#' token | '#' '(' Prms_list ')' | '#' '(' ')'  ;

AlwaysKind : always | always_comb | always_ff | always_latch ;

Always : AlwaysKind Statement | AlwaysKind When Statement ;


Generate : generate GenStatements  endgenerate ;

GenStatements : GenStatements GenStatement | GenStatement ;

GenStatement : 
     begin GenStatements end
    | begin ':' token GenStatements end
    | genvar token ';' 
    | Definition 
    | Assign 
    | Parameter 
    | Defparam 
    | Instance
    | GenFor_statement
    | Always
    | if '(' Expr ')' GenStatement 
    | if '(' Expr ')' GenStatement else GenStatement 
    | Initial
    ;



GenFor_statement : for '(' Soft_assigns ';' Expr ';' Soft_assigns ')' GenStatement ; 

CaseKind : unique case | case ;


When : '@' '*' | '@' '(' '*' ')' | '@' token | '@' '(' When_items ')'  ;
Or_coma : or | ',' ; 
When_items : When_items Or_coma When_item | When_item ;
When_item : posedge Expr | negedge Expr | Expr ;

// If_only : if '(' Expr ')' Statement ;
// If_else : If_only else Statement ;
Statement : 
     begin Statements end
    | begin end
    | forever Statement
    | begin ':' token Statements end
    | fork Statements join
    | LSH '=' Expr ';' 
    | LSH '=' AssignParams Expr ';' 
    | LSH sm_eq Expr ';' 
    | LSH sm_eq AssignParams Expr ';' 
    | if '(' Expr ')' Statement 
    | if '(' Expr ')' Statement else Statement 
    | wait Expr ';'
    | integer Tokens_list ';'
    | reg Tokens_list ';'
    | reg Width Tokens_list ';'
    | release Expr ';'
    | force Expr  '=' Expr ';'
    | When ';'
    | emit token ';'
    | disable token ';'
    | token '(' ')' ';'
    | token '(' Exprs ')' ';'
    | CaseKind '(' Expr ')' Cases endcase
    | CaseKind '(' Expr ')' Cases Default endcase
    | CaseKind '(' Expr ')' Default endcase
    | casez '(' Expr ')' Cases endcase
    | casez '(' Expr ')' Cases Default endcase
    | casex '(' Expr ')' Cases endcase
    | casex '(' Expr ')' Cases Default endcase
    | '#' Expr ';'
    | '#' Expr Statement 
    | token ';'
    | For_statement
    | Repeat_statement
    | While_statement
    | pragma
    | assign LSH '=' Expr ';'
    ;

For_statement : for '(' Soft_assigns ';' Expr ';' Soft_assigns ')' Statement ; 
Repeat_statement : repeat '(' Expr ')' Statement ; 
While_statement : while '(' Expr ')' Statement ; 
Soft_assigns : Soft_assigns ',' Soft_assign | Soft_assign ;
Soft_assign : LSH '=' Expr | LSH plusplus | integer token '=' Expr | genvar token '=' Expr ;
Cases : Cases Case | Case ;
Case : Exprs ':' Statement  | Exprs ':' ';' ;
Default : default ':'  Statement  | default ':' ';' ;

Exprs : Exprs ',' Expr | Expr ;
Statements : Statements Statement | Statement ;


LSH : token | token Width | token BusBit Width | token BusBit BusBit | token BusBit | CurlyList ;

Tokens_list : token ',' Tokens_list | token ;

Width : '[' Expr ':' Expr ']' | '[' Expr plus_range Expr ']' | '[' Expr minus_range Expr ']' ;
BusBit : '[' Expr ']' ;


PureExt : input | output | inout ;
IntKind  : reg | wire | logic | integer ;

ExtDir : PureExt | PureExt IntKind | PureExt signed | PureExt IntKind signed | PureExt unsigned | PureExt IntKind unsigned ;


IntDir : IntKind | signed | real | reg signed | wire signed | genvar | supply0 | supply1 | tri0 | tri1 ;

CurlyList : '{' CurlyItems '}' ;
CurlyItems : CurlyItems ',' CurlyItem | CurlyItem;
CurlyItem :   Expr CurlyList   | Expr ; 

Consts : bin | hex | dig | ubin | uhex | udig ;


Expr :
     token
    | number
    | floating
    | string
    | define
    | define '(' Expr ')' 
    | bin | hex | dig | ubin | uhex | udig
    | Crazy 
    | token Width
    | token BusBit Width
    | token BusBit BusBit
    | token BusBit
    | Expr '?' Expr ':' Expr
    | Expr '+' Expr
    | Expr '*' Expr
    | Expr '-' Expr
    | Expr '/' Expr
    | Expr '%' Expr
    | Expr '^' Expr
    | Expr '|' Expr
    | Expr '&' Expr
    | Expr '<' Expr
    | Expr '>' Expr
    | Expr starstar Expr
    | Expr and_and Expr
    | Expr or_or Expr
    | Expr xnor Expr
    | Expr nand Expr
    | Expr nor Expr
    | Expr eq_eq Expr
    | Expr eq3 Expr
    | Expr not_eq Expr
    | Expr noteqeq Expr
    | Expr gr_eq Expr
    | Expr sm_eq Expr
    | Expr shift3 Expr
    | Expr shift_left Expr
    | Expr shift_right Expr
    | Expr arith_shift_right Expr
    | token '(' Exprs ')'
    | '(' Expr ')'
    | CurlyList
    | '-' Expr %prec UNARY_PREC
    | '|' Expr %prec UNARY_PREC
    | '&' Expr %prec UNARY_PREC
    | '^' Expr %prec UNARY_PREC
    | xnor Expr %prec UNARY_PREC
    | nor Expr %prec UNARY_PREC
    | '!' Expr %prec UNARY_PREC
    | '~' Expr %prec UNARY_PREC
    ;


%%
