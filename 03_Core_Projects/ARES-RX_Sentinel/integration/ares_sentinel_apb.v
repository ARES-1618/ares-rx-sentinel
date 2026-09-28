/*
 * ==============================================================================
 * Project: ARES-RX Sentinel — Trusted Digital Reception Boundary
 * Module:  ares_sentinel_apb.v
 * Standard: AMBA APB4 Protocol Slave Interface
 * Classification: Industrial SoC Integration Wrapper (Peruri Secure Element / RISC-V)
 *
 * Description:
 *   AMBA 3/4 APB Slave wrapper encapsulating the core ARES-RX Sentinel
 *   demarcation boundary subsystem (ares_sentinel_top.v). Allows seamless
 *   memory-mapped integration into 32-bit SoC architectures (e.g. RISC-V Ibex,
 *   ARM Cortex-M0+/M3/M4, or Peruri Secure Microcontroller).
 *
 * Register Map (32-bit Word Aligned):
 *   Offset 0x00 (RW): REG_CTRL
 *     [0]   : ENABLE (1 = Sentinel active, 0 = Standby)
 *     [1]   : IRQ_TAMPER_EN (1 = Enable hardware tamper interrupt)
 *     [2]   : IRQ_RX_VALID_EN (1 = Enable valid frame received interrupt)
 *     [8]   : FAULT_CLEAR_TRIGGER (Write 1 to clear sticky fault if UNLOCK_KEY matches)
 *   Offset 0x04 (RO): REG_STATUS
 *     [0]   : RECEPTION_ACTIVE (Physical RF envelope monitor)
 *     [1]   : FRAME_COMPLETE (192-bit frame received & verified)
 *     [2]   : FAULT_LATCHED (Sticky hardware fault state)
 *     [3]   : TAMPER_ALERT (Active security alarm strobe)
 *     [15:8]: BIT_COUNTER (Current frame bit count: 0..191)
 *   Offset 0x08 (RO): REG_FAULT_CODE
 *     [2:0]  : LATCHED_FAULT_CODE (Primary cause of security trip)
 *     [6:4]  : TEMPORAL_CODE (Raw Layer-1 fault telemetry)
 *     [10:8] : FRAME_CODE (Raw Layer-2 syntax fault telemetry)
 *     [14:12]: ARB_FAULT_CODE (Arbiter resolved fault)
 *   Offset 0x0C (WO): REG_UNLOCK_KEY
 *     [31:0] : Security unlock authorization key (0xA8E5_2026)
 *   Offset 0x10 (RO): REG_PAYLOAD_LO
 *     [31:0] : Dynamic telemetry bits 31..0 (e.g. Thermostat / Sensor ID)
 *   Offset 0x14 (RO): REG_PAYLOAD_MID
 *     [31:0] : Dynamic telemetry bits 63..32 (e.g. Room Temp & Set Temp)
 *   Offset 0x18 (RO): REG_PAYLOAD_HI
 *     [7:0]  : Dynamic telemetry bits 71..64 (e.g. System State)
 *   Offset 0x1C (RO): REG_HARDWARE_ID
 *     [31:0] : Hardware identification constant 0x41524553 ("ARES" ASCII)
 * ==============================================================================
 */

`default_nettype none

module ares_sentinel_apb #(
    parameter [31:0] UNLOCK_KEY_VAL = 32'hA8E5_2026
) (
    // --------------------------------------------------------------------------
    // AMBA APB4 Slave Bus Interface
    // --------------------------------------------------------------------------
    input  wire        PCLK,       // Bus clock
    input  wire        PRESETn,    // Active-low asynchronous reset
    input  wire [7:0]  PADDR,      // Address bus (byte address, word-aligned)
    input  wire        PSEL,       // Peripheral select
    input  wire        PENABLE,    // Enable strobe
    input  wire        PWRITE,     // 1 = Write, 0 = Read
    input  wire [31:0] PWDATA,     // Write data bus
    input  wire [3:0]  PSTRB,      // Byte write strobes
    output wire        PREADY,     // Ready handshake
    output reg  [31:0] PRDATA,     // Read data bus
    output wire        PSLVERR,    // Transfer error indicator

    // --------------------------------------------------------------------------
    // Physical Baseband Radio Interface
    // --------------------------------------------------------------------------
    input  wire        rx_in,      // Demodulated baseband digital input from RF IC

    // --------------------------------------------------------------------------
    // Interrupt Outputs to SoC Interrupt Controller (NVIC / CLIC / PLIC)
    // --------------------------------------------------------------------------
    output wire        irq_tamper,   // Security alarm interrupt (Active-High)
    output wire        irq_rx_valid  // Clean frame reception interrupt (Active-High)
);

    // --------------------------------------------------------------------------
    // APB Handshake Protocol Logic
    // --------------------------------------------------------------------------
    // Single-cycle zero-wait-state response: PREADY is permanently asserted
    assign PREADY  = 1'b1;
    assign PSLVERR = 1'b0;

    wire apb_write = PSEL && PENABLE && PWRITE;
    wire apb_read  = PSEL && !PENABLE && !PWRITE;

    // --------------------------------------------------------------------------
    // Internal Registers
    // --------------------------------------------------------------------------
    reg        reg_enable;
    reg        reg_irq_tamper_en;
    reg        reg_irq_rx_en;
    reg [31:0] reg_unlock_key;
    reg        soft_reset_pulse;

    // Shift register for capturing dynamic payload bits (bits 96..167 = 72 bits)
    reg [71:0] payload_shift_reg;

    // --------------------------------------------------------------------------
    // Core Sentinel Hardware Signals
    // --------------------------------------------------------------------------
    wire [7:0] safe_data_out;
    wire       safe_valid_out;
    wire       tamper_alert;
    wire [2:0] latched_fault_code;
    wire       reception_active;
    wire       frame_complete;
    wire       temporal_fault;
    wire [2:0] temporal_code;
    wire       frame_fault;
    wire [2:0] frame_code;
    wire       arb_set_fault;
    wire [2:0] arb_fault_code;
    wire [7:0] bit_counter;
    wire       fault_latched;

    // Derived reset: PRESETn AND software clear (if authorized by unlock key)
    wire core_rst_n = PRESETn && !(soft_reset_pulse && (reg_unlock_key == UNLOCK_KEY_VAL));

    // --------------------------------------------------------------------------
    // ARES-RX Sentinel Core Demarcation Subsystem Instantiation
    // --------------------------------------------------------------------------
    ares_sentinel_top #(
        .DATA_WIDTH(8)
    ) u_sentinel_core (
        .clk(PCLK),
        .rst_n(core_rst_n),
        .rx_in(rx_in),
        .ext_pos_edge(1'b0),
        .ext_neg_edge(1'b0),
        .use_ext_edges(1'b0),
        .serial_clock(1'b0),
        .serial_data(1'b0),
        .raw_data_in(8'h00),
        .raw_valid_in(1'b0),
        .safe_data_out(safe_data_out),
        .safe_valid_out(safe_valid_out),
        .tamper_alert(tamper_alert),
        .latched_fault_code(latched_fault_code),
        .reception_active(reception_active),
        .frame_complete(frame_complete),
        .temporal_fault(temporal_fault),
        .temporal_code(temporal_code),
        .frame_fault(frame_fault),
        .frame_code(frame_code),
        .arb_set_fault(arb_set_fault),
        .arb_fault_code(arb_fault_code),
        .bit_counter(bit_counter),
        .fault_latched(fault_latched)
    );

    // --------------------------------------------------------------------------
    // Payload Sampling Logic (Dynamic telemetry bits 96..167)
    // --------------------------------------------------------------------------
    always @(posedge PCLK or negedge core_rst_n) begin
        if (!core_rst_n) begin
            payload_shift_reg <= 72'd0;
        end else if (reception_active && !fault_latched) begin
            // Shift data during dynamic payload window
            if (bit_counter >= 8'd96 && bit_counter <= 8'd167) begin
                payload_shift_reg <= {payload_shift_reg[70:0], rx_in};
            end
        end
    end

    // --------------------------------------------------------------------------
    // APB Write Register Operations
    // --------------------------------------------------------------------------
    always @(posedge PCLK or negedge PRESETn) begin
        if (!PRESETn) begin
            reg_enable        <= 1'b1; // Enabled by default
            reg_irq_tamper_en <= 1'b1; // Tamper IRQ enabled by default
            reg_irq_rx_en     <= 1'b1;
            reg_unlock_key    <= 32'd0;
            soft_reset_pulse  <= 1'b0;
        end else begin
            soft_reset_pulse <= 1'b0; // Auto-clearing strobe
            
            if (apb_write) begin
                case (PADDR[7:0])
                    8'h00: begin // REG_CTRL
                        if (PSTRB[0]) reg_enable        <= PWDATA[0];
                        if (PSTRB[0]) reg_irq_tamper_en <= PWDATA[1];
                        if (PSTRB[0]) reg_irq_rx_en     <= PWDATA[2];
                        if (PSTRB[1]) soft_reset_pulse  <= PWDATA[8];
                    end
                    8'h0C: begin // REG_UNLOCK_KEY
                        if (PSTRB[0]) reg_unlock_key[7:0]   <= PWDATA[7:0];
                        if (PSTRB[1]) reg_unlock_key[15:8]  <= PWDATA[15:8];
                        if (PSTRB[2]) reg_unlock_key[23:16] <= PWDATA[23:16];
                        if (PSTRB[3]) reg_unlock_key[31:24] <= PWDATA[31:24];
                    end
                    default: ; // Other registers are read-only
                endcase
            end
        end
    end

    // --------------------------------------------------------------------------
    // APB Read Register Multiplexing
    // --------------------------------------------------------------------------
    always @(*) begin
        case (PADDR[7:0])
            8'h00: begin // REG_CTRL
                PRDATA = {23'd0, soft_reset_pulse, 5'd0, reg_irq_rx_en, reg_irq_tamper_en, reg_enable};
            end
            8'h04: begin // REG_STATUS
                PRDATA = {16'd0, bit_counter, 4'd0, tamper_alert, fault_latched, frame_complete, reception_active};
            end
            8'h08: begin // REG_FAULT_CODE
                PRDATA = {17'd0, arb_fault_code, 1'b0, frame_code, 1'b0, temporal_code, 1'b0, latched_fault_code};
            end
            8'h0C: begin // REG_UNLOCK_KEY
                PRDATA = reg_unlock_key;
            end
            8'h10: begin // REG_PAYLOAD_LO (Bits 31..0: Thermostat / Device ID)
                PRDATA = payload_shift_reg[31:0];
            end
            8'h14: begin // REG_PAYLOAD_MID (Bits 63..32: Temperatures)
                PRDATA = payload_shift_reg[63:32];
            end
            8'h18: begin // REG_PAYLOAD_HI (Bits 71..64: System State)
                PRDATA = {24'd0, payload_shift_reg[71:64]};
            end
            8'h1C: begin // REG_HARDWARE_ID
                PRDATA = 32'h41524553; // "ARES" in ASCII
            end
            default: begin
                PRDATA = 32'h00000000;
            end
        endcase
    end

    // --------------------------------------------------------------------------
    // Interrupt Generation
    // --------------------------------------------------------------------------
    assign irq_tamper   = reg_irq_tamper_en && tamper_alert;
    assign irq_rx_valid = reg_irq_rx_en && frame_complete && !fault_latched;

endmodule

`default_nettype wire
