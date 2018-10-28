





































import apu_core_package::*;


`define REG_S1 19:15
`define REG_S2 24:20
`define REG_S3 29:25
`define REG_D  11:07

`define REG_RM 14:12

`define USE_APU_DSP_MULT if (SHARED_DSP_MULT) begin                            mult_int_en_o   = 1'b0;                            mult_dot_en_o   = 1'b0;                            apu_en          = 1'b1;                            apu_type_o      = APUTYPE_DSP_MULT;                            apu_flags_src_o = APU_FLAGS_DSP_MULT;                            apu_op_o        = mult_operator_o;                            apu_lat_o       = (PIPE_REG_DSP_MULT==1) ? 2'h2 : 2'h1;                         end

`define USE_APU_INT_MULT if (SHARED_INT_MULT) begin                            mult_int_en_o   = 1'b0;                            mult_dot_en_o   = 1'b0;                            apu_en          = 1'b1;                            apu_flags_src_o = APU_FLAGS_INT_MULT;                            apu_op_o        = mult_operator_o;                            apu_type_o      = APUTYPE_INT_MULT;                            apu_lat_o       = 2'h1;                         end

`define USE_APU_INT_DIV if (SHARED_INT_DIV) begin                           alu_en_o = 1'b0;                           apu_en = 1'b1;                           apu_type_o = APUTYPE_INT_DIV;                           apu_op_o = alu_operator_o;                           apu_lat_o       = 2'h3;                         end

`define FP_2OP if (FPU==1) begin                 apu_en              = 1'b1;                 alu_en_o            = 1'b0;                 apu_flags_src_o     = APU_FLAGS_FP;                 rega_used_o         = 1'b1;                 regb_used_o         = 1'b1;                 reg_fp_a_o          = 1'b1;                 reg_fp_b_o          = 1'b1;                 reg_fp_d_o          = 1'b1;               end

`define FP_3OP if (FPU==1) begin                 apu_en              = 1'b1;                 alu_en_o            = 1'b0;                 apu_flags_src_o     = APU_FLAGS_FP;                 rega_used_o         = 1'b1;                 regb_used_o         = 1'b1;                 regc_used_o         = 1'b1;                 reg_fp_a_o          = 1'b1;                 reg_fp_b_o          = 1'b1;                 reg_fp_c_o          = 1'b1;                 reg_fp_d_o          = 1'b1;                 regc_mux_o          = REGC_S4;               end


module riscv_apu_disp (
  input logic                           clk_i,
  input logic                           rst_ni,

  
  input logic                           enable_i,
  input logic [1:0]                     apu_lat_i,
  input logic [5:0]                     apu_waddr_i,

  
  output logic [5:0]                    apu_waddr_o,
  output logic                          apu_multicycle_o,
  output logic                          apu_singlecycle_o,

  
  output logic                          active_o,

  
  output logic                          stall_o,

  
  input  logic [2:0][5:0]               read_regs_i,
  input  logic [2:0]                    read_regs_valid_i,
  output logic                          read_dep_o,

  input  logic [1:0][5:0]               write_regs_i,
  input  logic [1:0]                    write_regs_valid_i,
  output logic                          write_dep_o,

  
  output logic                          perf_type_o,
  output logic                          perf_cont_o,

  
  
  output logic                          apu_master_req_o,
  output logic                          apu_master_ready_o,
  input logic                           apu_master_gnt_i,
  
  input logic                           apu_master_valid_i

  );

  logic [5:0]         addr_req, addr_inflight, addr_waiting;
  logic [5:0]         addr_inflight_dn, addr_waiting_dn;
  logic               valid_req, valid_inflight, valid_waiting;
  logic               valid_inflight_dn, valid_waiting_dn;
  logic               returned_req, returned_inflight, returned_waiting;

  logic               req_accepted;
  logic               active;
  logic [1:0]         apu_lat;
   
   
  logic [2:0] read_deps_req,  read_deps_inflight,  read_deps_waiting;
  logic [1:0] write_deps_req, write_deps_inflight, write_deps_waiting;
  logic       read_dep_req,   read_dep_inflight,   read_dep_waiting;
  logic       write_dep_req,  write_dep_inflight,  write_dep_waiting;

  logic stall_full, stall_type, stall_nack;

  
  assign valid_req    = enable_i & !(stall_full | stall_type);
  assign addr_req     = apu_waddr_i;

  assign req_accepted = valid_req & apu_master_gnt_i;
   
  
  
  
  
  assign returned_req      = valid_req      &  apu_master_valid_i  & !valid_inflight & !valid_waiting;
  assign returned_inflight = valid_inflight & (apu_master_valid_i) & !valid_waiting;
  assign returned_waiting  = valid_waiting  & (apu_master_valid_i);

  
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if(~rst_ni) begin
      valid_inflight   <= 1'b0;
      valid_waiting    <= 1'b0;
      addr_inflight    <= '0;
      addr_waiting     <= '0;
    end else begin     
       valid_inflight  <= valid_inflight_dn;
       valid_waiting   <= valid_waiting_dn;
       addr_inflight   <= addr_inflight_dn;
       addr_waiting    <= addr_waiting_dn;
    end
  end

  always_comb begin
     valid_inflight_dn      = valid_inflight;
     valid_waiting_dn       = valid_waiting;
     addr_inflight_dn       = addr_inflight;
     addr_waiting_dn        = addr_waiting;

     if (req_accepted & !returned_req) begin 
        valid_inflight_dn   = 1'b1;
        addr_inflight_dn    = addr_req;
        if (valid_inflight & !(returned_inflight)) begin 
           valid_waiting_dn = 1'b1;
           addr_waiting_dn  = addr_inflight;
        end 
        if (returned_waiting) begin 
           valid_waiting_dn = 1'b1;
           addr_waiting_dn  = addr_inflight;
        end 
     end 
     else if (returned_inflight) begin 
        valid_inflight_dn   = '0;
        valid_waiting_dn    = '0;
        addr_inflight_dn    = '0;
        addr_waiting_dn     = '0;
     end
     else if (returned_waiting) begin 
        valid_waiting_dn    = '0;
        addr_waiting_dn     = '0;
     end
  end
   
  
  
  
  
  assign active = valid_inflight | valid_waiting;

  
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if(~rst_ni) begin
      apu_lat    <= '0;
    end else begin
      if(valid_req) begin
        apu_lat  <= apu_lat_i;
      end
    end
  end

  
  
  
  
  generate
    for (genvar i = 0; i < 3; i++) begin
      assign read_deps_req[i]      = (read_regs_i[i] == addr_req)      & read_regs_valid_i[i];
      assign read_deps_inflight[i] = (read_regs_i[i] == addr_inflight) & read_regs_valid_i[i];
      assign read_deps_waiting[i]  = (read_regs_i[i] == addr_waiting)  & read_regs_valid_i[i];
    end
  endgenerate

  generate
    for (genvar i = 0; i < 2; i++) begin
      assign write_deps_req[i]      = (write_regs_i[i] == addr_req)      & write_regs_valid_i[i];
      assign write_deps_inflight[i] = (write_regs_i[i] == addr_inflight) & write_regs_valid_i[i];
      assign write_deps_waiting[i]  = (write_regs_i[i] == addr_waiting)  & write_regs_valid_i[i];
    end
  endgenerate

  
  assign read_dep_req       = |read_deps_req       & valid_req      & !returned_req;
  assign read_dep_inflight  = |read_deps_inflight  & valid_inflight & !returned_inflight;
  assign read_dep_waiting   = |read_deps_waiting   & valid_waiting  & !returned_waiting;
  assign write_dep_req      = |write_deps_req      & valid_req      & !returned_req;
  assign write_dep_inflight = |write_deps_inflight & valid_inflight & !returned_inflight;
  assign write_dep_waiting  = |write_deps_waiting  & valid_waiting  & !returned_waiting;

  assign read_dep_o         = read_dep_req  | read_dep_inflight  | read_dep_waiting;
  assign write_dep_o        = write_dep_req | write_dep_inflight | write_dep_waiting;

  
  
  
  
  assign stall_full      = valid_inflight & valid_waiting;
  
  
  
  assign stall_type      = enable_i  & active & ((apu_lat_i==2'h1) | ((apu_lat_i==2'h2) & (apu_lat==2'h3)) | (apu_lat_i==2'h3));
  assign stall_nack      = valid_req & !apu_master_gnt_i;
  assign stall_o         = stall_full | stall_type | stall_nack;

  
  
  
  assign apu_master_req_o      = valid_req;

  
  
  
  assign apu_master_ready_o     = 1'b1;

  
  always_comb begin
    apu_waddr_o = '0;
    if(returned_req)
      apu_waddr_o = addr_req;
    if(returned_inflight)
      apu_waddr_o = addr_inflight;
    if(returned_waiting)
      apu_waddr_o = addr_waiting;
  end

  
  assign active_o = active;

  
  assign perf_type_o = stall_type;
  assign perf_cont_o = stall_nack;
   
  assign apu_multicycle_o  =  (apu_lat == 2'h3);
  assign apu_singlecycle_o = ~(valid_inflight | valid_waiting);
   
  
  
  
  
`ifndef VERILATOR
  assert property (
    @(posedge clk_i) (apu_master_valid_i) |-> (valid_req | valid_inflight | valid_waiting))
    else $warning("[APU Dispatcher] instruction returned while no instruction is in-flight");
`endif
   
endmodule