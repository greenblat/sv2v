

import os,sys,string,random
import veri
NewName = os.path.expanduser('~')
sys.path.append('%s/verification_libs'%NewName)
import logs
Monitors=[]
cycles=0

REGS = 'tb.dut.id_stage_i.registers_i'
class regsMonitor:
    def __init__(self,Monitors):
        self.regs={}
        for ii in range(32):
            self.regs[ii]= -1
        Monitors.append(self)

    def peek(self,Sig):
        return veri.peek('%s.%s'%(REGS,Sig))
    
    def run(self):
        Now = self.peek('mem')
        ind = 0
        while Now!='':
            Val = Now[-32:]
            Now = Now[:-32]
            self.assign(ind,Val)
            ind += 1

    def assign(self,Reg,Val):
        Val = logs.intx(Val)
        if Val!=self.regs[Reg]:
            logs.log_info('reg=%x got %08x was %08x'%(Reg,Val,self.regs[Reg]))
            self.regs[Reg] = Val

regsMonitor(Monitors)

class instrMonitor:
    def __init__(self,Path,Fname,Monitors):
        Monitors.append(self)
        self.Path = Path
        self.queue=[]
        self.rom={}
        self.loadListing(Fname)

    def force(self,Sig,Val):
        veri.force('%s.%s'%(self.Path,Sig),str(Val))

    def peek(self,Sig):
        return logs.peek('%s.%s'%(self.Path,Sig))

    def valid(self,Sig):
        return self.peek(Sig)==1

    def run(self):
        self.force('instr_gnt_i',1)
        if self.queue!=[]:
            addr = self.queue.pop(0)
            self.force('instr_rvalid_i',1)
            Instr = self.instruction(addr)
            self.force('instr_rdata_i',Instr)
            logs.log_info('served addr=%x data=%08x'%(addr,Instr))

        if self.valid('instr_req_o'):
            addr = self.peek('instr_addr_o')
            self.queue.append(addr/4)

    def instruction(self,Addr):
        if Addr in self.rom:
            return self.rom[Addr]
        return 0

    def loadRom(self,Fname):
        File = open(Fname)
        Addr = 0
        while 1:
            line = File.readline()
            if line=='': return
            wrds = string.split(line)
            if wrds==[]:
                pass
            for Wrd in wrds:
                if Wrd[0]=='@':
                    Addr = int(Wrd[1:],16)
                else:
                    Data = int(Wrd,16)
                    self.rom[Addr]=Data
                    Addr += 1


    def loadListing(self,Fname):
        if '.rom' in Fname:
            self.loadRom(Fname)
            return
        File = open(Fname)
        while 1:
            line = File.readline()
            if line=='': return
            wrds = string.split(line)
            if wrds==[]:
                pass
            elif (len(wrds)>6):
                Addr = int(wrds[3],16)
                Data = int(wrds[4],16)
                self.rom[Addr]=Data



#instrMonitor('tb','x.asm.lst',Monitors)
instrMonitor('tb','out.rom',Monitors)



def negedge():
    global cycles
    cycles += 1
    veri.force('tb.cycles',str(cycles))
    if (cycles>1000):
        veri.finish()
    rst_n = veri.peek('tb.rst_n')
    if (rst_n!='1'):
        return

    if (cycles==30):
        veri.listing('tb','100','deep.list')
        veri.force('tb.clock_en_i','1')
        veri.force('tb.boot_addr_i','0x0')  # if ==0x400 adds 0x100 to fetching rom
        veri.force('tb.fetch_enable_i','1')
    if (cycles>30):
        for Mon in Monitors: Mon.run()







def cucu():
    veri.force('tb.apu_master_flags_i','0')
    veri.force('tb.apu_master_gnt_i','0')
    veri.force('tb.apu_master_result_i','0')
    veri.force('tb.apu_master_valid_i','0')
    veri.force('tb.boot_addr_i','0')
    veri.force('tb.clk_i','0')
    veri.force('tb.clock_en_i','0')
    veri.force('tb.cluster_id_i','0')
    veri.force('tb.core_id_i','0')
    veri.force('tb.data_err_i','0')
    veri.force('tb.data_gnt_i','0')
    veri.force('tb.data_rdata_i','0')
    veri.force('tb.data_rvalid_i','0')
    veri.force('tb.debug_addr_i','0')
    veri.force('tb.debug_halt_i','0')
    veri.force('tb.debug_req_i','0')
    veri.force('tb.debug_resume_i','0')
    veri.force('tb.debug_wdata_i','0')
    veri.force('tb.debug_we_i','0')
    veri.force('tb.ext_perf_counters_i','0')
    veri.force('tb.fetch_enable_i','0')
    veri.force('tb.instr_gnt_i','0')
    veri.force('tb.instr_rdata_i','0')
    veri.force('tb.instr_rvalid_i','0')
    veri.force('tb.irq_i','0')
    veri.force('tb.irq_id_i','0')
    veri.force('tb.irq_sec_i','0')
    veri.force('tb.rst_ni','0')
    veri.force('tb.test_en_i','0')
    apu_master_flags_o = logs.peek('tb.apu_master_flags_o')
    apu_master_op_o = logs.peek('tb.apu_master_op_o')
    apu_master_operands_o = logs.peek('tb.apu_master_operands_o')
    apu_master_ready_o = logs.peek('tb.apu_master_ready_o')
    apu_master_req_o = logs.peek('tb.apu_master_req_o')
    apu_master_type_o = logs.peek('tb.apu_master_type_o')
    core_busy_o = logs.peek('tb.core_busy_o')
    data_addr_o = logs.peek('tb.data_addr_o')
    data_be_o = logs.peek('tb.data_be_o')
    data_req_o = logs.peek('tb.data_req_o')
    data_wdata_o = logs.peek('tb.data_wdata_o')
    data_we_o = logs.peek('tb.data_we_o')
    debug_gnt_o = logs.peek('tb.debug_gnt_o')
    debug_halted_o = logs.peek('tb.debug_halted_o')
    debug_rdata_o = logs.peek('tb.debug_rdata_o')
    debug_rvalid_o = logs.peek('tb.debug_rvalid_o')
    instr_addr_o = logs.peek('tb.instr_addr_o')
    instr_req_o = logs.peek('tb.instr_req_o')
    irq_ack_o = logs.peek('tb.irq_ack_o')
    irq_id_o = logs.peek('tb.irq_id_o')
    sec_lvl_o = logs.peek('tb.sec_lvl_o')
