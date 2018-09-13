
import string,types
import logs
KNOWNFUNCTIONS = string.split('ext sxt resize conv_std_logic_vector conv_integer unsigned')
def matches(List,Seq,Verbose=False):
    if Verbose:
        logs.log_info('try list=%s pattern=%s'%(List,Seq))
    if type(Seq)==types.ListType:
        return listMatches(List,Seq,Verbose)
    if type(Seq)==types.TupleType:
        return listMatches(List,Seq,Verbose)
    Lseq = string.split(Seq)
    if len(List)!=len(Lseq): 
        if Verbose: logs.log_info('matches stopped at length %d<>%d iseq=%s who=%s '%(len(Lseq),len(List),Lseq,List))
        return False
    Vars=[]
    for ind,Iseq in enumerate(Lseq):
        Lind = List[ind]
        if type(Lind) in [types.TupleType,types.ListType]:
            Litem = Lind[1]
        else:
            Litem = Lind

        if Iseq == '?': 
            Vars.append(List[ind])
        elif Iseq[0] == '!': 
            if (Iseq[1:]!=List[ind][0]): 
                if Verbose: logs.log_info('matches stopped at iseq=%s who=%s '%(Iseq,List[ind]))
                return False
            Vars.append(List[ind])
        elif Iseq == '$': 
            Who = List[ind]
            if Who in KNOWNFUNCTIONS:
                Vars.append(List[ind])
            else:
                if Verbose: logs.log_info('matches stopped at iseq=%s who=%s '%(Iseq,Who))
                return False

        elif (Iseq!=Litem):
            if Verbose: logs.log_info('matches stopped at iseq=%s who=%s '%(Iseq,List[ind]))
            return False
    if Vars==[]: return True 
    return Vars 



def listMatches(List,Seq,Verbose):
    if type(List)==types.IntType:
        List = str(List)
    if Seq=='?':
        return [List]

    if type(List)==types.TupleType:
        List = list(List)
    if Verbose:
        logs.log_info('try list=%s pattern=%s'%(List,Seq))

    if type(List)!=type(Seq): 
        if Verbose: logs.log_info('failed on dff types %s %s list=%s pattern=%s'%(type(List),type(Seq),List,Seq))
        return False
    if type(List)==types.StringType:
        if Seq=='?': return [List]
        Ok =  Seq==List
        if Verbose and not Ok: logs.log_info('failed on dff token list=%s pattern=%s'%(List,Seq))
        return Ok
    if len(List)!=len(Seq): 
        if Verbose: logs.log_info('failed on dff len list=%s pattern=%s'%(List,Seq))
        return False
    Res=[]
    for ind,Item in enumerate(List):
        V = listMatches(Item,Seq[ind],Verbose)
        if not V: return False
        if type(V) in [types.ListType,types.TupleType]:
            Res.extend(V)
    return Res 
