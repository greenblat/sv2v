module tb;
reg [31:0] cycles;   initial cycles=0;
reg [31:0] errors;   initial errors=0;
reg [31:0] wrongs;   initial wrongs=0;
reg [31:0] panics;   initial panics=0;
reg [31:0] corrects; initial corrects=0;
reg [31:0] marker;   initial marker=0;
parameter INSTR_RDATA_WIDTH = 32;
parameter SHARED_FP_DIVSQRT = 0;
parameter WAPUTYPE = 0;
parameter APU_NARGS_CPU = 3;
parameter APU_WOP_CPU = 6;
parameter SHARED_INT_DIV = 0;
parameter FPU = 0;
parameter APU_NDSFLAGS_CPU = 15;
parameter APU_NUSFLAGS_CPU = 5;
parameter PULP_SECURE = 0;
parameter SHARED_DSP_MULT = 0;
parameter SHARED_FP = 0;
parameter N_EXT_PERF_COUNTERS = 2;
reg [(APU_NUSFLAGS_CPU - 1):0] apu_master_flags_i;
wire [(APU_NDSFLAGS_CPU - 1):0] apu_master_flags_o;
reg  apu_master_gnt_i;
wire [(APU_WOP_CPU - 1):0] apu_master_op_o;
wire [95:0] apu_master_operands_o;
wire  apu_master_ready_o;
wire  apu_master_req_o;
reg [31:0] apu_master_result_i;
wire [(WAPUTYPE - 1):0] apu_master_type_o;
reg  apu_master_valid_i;
reg [31:0] boot_addr_i;
reg  clk_i;
reg  clock_en_i;
reg [5:0] cluster_id_i;
wire  core_busy_o;
reg [3:0] core_id_i;
wire [31:0] data_addr_o;
wire [3:0] data_be_o;
reg  data_err_i;
reg  data_gnt_i;
reg [31:0] data_rdata_i;
wire  data_req_o;
reg  data_rvalid_i;
wire [31:0] data_wdata_o;
wire  data_we_o;
reg [14:0] debug_addr_i;
wire  debug_gnt_o;
reg  debug_halt_i;
wire  debug_halted_o;
wire [31:0] debug_rdata_o;
reg  debug_req_i;
reg  debug_resume_i;
wire  debug_rvalid_o;
reg [31:0] debug_wdata_i;
reg  debug_we_i;
reg [(N_EXT_PERF_COUNTERS - 1):0] ext_perf_counters_i;
reg  fetch_enable_i;
wire [31:0] instr_addr_o;
reg  instr_gnt_i;
reg [(INSTR_RDATA_WIDTH - 1):0] instr_rdata_i;
wire  instr_req_o;
reg  instr_rvalid_i;
wire  irq_ack_o;
reg  irq_i;
reg [4:0] irq_id_i;
wire [4:0] irq_id_o;
reg  irq_sec_i;
reg  rst_n;
wire  sec_lvl_o;
reg  test_en_i;

always begin
    clk_i=0;
    #10;
    clk_i=1;
    #3;
    $python("negedge()");
    #7;
end
wire clk = clk_i;
initial begin
    $dumpvars(0,tb);
    apu_master_flags_i[(APU_NUSFLAGS_CPU - 1):0] = 0;
    apu_master_gnt_i = 0;
    apu_master_result_i[31:0] = 0;
    apu_master_valid_i = 0;
    boot_addr_i[31:0] = 0;
    clk_i = 0;
    clock_en_i = 0;
    cluster_id_i[5:0] = 0;
    core_id_i[3:0] = 0;
    data_err_i = 0;
    data_gnt_i = 0;
    data_rdata_i[31:0] = 0;
    data_rvalid_i = 0;
    debug_addr_i[14:0] = 0;
    debug_halt_i = 0;
    debug_req_i = 0;
    debug_resume_i = 0;
    debug_wdata_i[31:0] = 0;
    debug_we_i = 0;
    ext_perf_counters_i[(N_EXT_PERF_COUNTERS - 1):0] = 0;
    fetch_enable_i = 0;
    instr_gnt_i = 0;
    instr_rdata_i = 0;
    instr_rvalid_i = 0;
    irq_i = 0;
    irq_id_i[4:0] = 0;
    irq_sec_i = 0;
    rst_n = 0;
    test_en_i = 0;
    #100;
    rst_n=1;
end
riscv_core dut (
     .apu_master_flags_i(apu_master_flags_i[(APU_NUSFLAGS_CPU - 1):0])
    ,.apu_master_flags_o(apu_master_flags_o[(APU_NDSFLAGS_CPU - 1):0])
    ,.apu_master_gnt_i(apu_master_gnt_i)
    ,.apu_master_op_o(apu_master_op_o[(APU_WOP_CPU - 1):0])
    ,.apu_master_operands_o(apu_master_operands_o)
    ,.apu_master_ready_o(apu_master_ready_o)
    ,.apu_master_req_o(apu_master_req_o)
    ,.apu_master_result_i(apu_master_result_i[31:0])
    ,.apu_master_type_o(apu_master_type_o[(WAPUTYPE - 1):0])
    ,.apu_master_valid_i(apu_master_valid_i)
    ,.boot_addr_i(boot_addr_i[31:0])
    ,.clk_i(clk_i)
    ,.clock_en_i(clock_en_i)
    ,.cluster_id_i(cluster_id_i[5:0])
    ,.core_busy_o(core_busy_o)
    ,.core_id_i(core_id_i[3:0])
    ,.data_addr_o(data_addr_o[31:0])
    ,.data_be_o(data_be_o[3:0])
    ,.data_err_i(data_err_i)
    ,.data_gnt_i(data_gnt_i)
    ,.data_rdata_i(data_rdata_i[31:0])
    ,.data_req_o(data_req_o)
    ,.data_rvalid_i(data_rvalid_i)
    ,.data_wdata_o(data_wdata_o[31:0])
    ,.data_we_o(data_we_o)
    ,.debug_addr_i(debug_addr_i[14:0])
    ,.debug_gnt_o(debug_gnt_o)
    ,.debug_halt_i(debug_halt_i)
    ,.debug_halted_o(debug_halted_o)
    ,.debug_rdata_o(debug_rdata_o[31:0])
    ,.debug_req_i(debug_req_i)
    ,.debug_resume_i(debug_resume_i)
    ,.debug_rvalid_o(debug_rvalid_o)
    ,.debug_wdata_i(debug_wdata_i[31:0])
    ,.debug_we_i(debug_we_i)
    ,.ext_perf_counters_i(ext_perf_counters_i[(N_EXT_PERF_COUNTERS - 1):0])
    ,.fetch_enable_i(fetch_enable_i)
    ,.instr_addr_o(instr_addr_o[31:0])
    ,.instr_gnt_i(instr_gnt_i)
    ,.instr_rdata_i(instr_rdata_i[(INSTR_RDATA_WIDTH - 1):0])
    ,.instr_req_o(instr_req_o)
    ,.instr_rvalid_i(instr_rvalid_i)
    ,.irq_ack_o(irq_ack_o)
    ,.irq_i(irq_i)
    ,.irq_id_i(irq_id_i[4:0])
    ,.irq_id_o(irq_id_o[4:0])
    ,.irq_sec_i(irq_sec_i)
    ,.rst_ni(rst_n)
    ,.sec_lvl_o(sec_lvl_o)
    ,.test_en_i(test_en_i)
);
endmodule
