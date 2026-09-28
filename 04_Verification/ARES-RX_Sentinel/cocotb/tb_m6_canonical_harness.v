`timescale 1ns / 1ps

module tb_m6_canonical_harness;
    reg clk;
    reg rst_n;
    reg rx_in;
    reg serial_clock;
    reg serial_data;
    reg [7:0] raw_data_in;
    reg raw_valid_in;

    wire [7:0] safe_data_out;
    wire safe_valid_out;
    wire tamper_alert;
    wire [2:0] latched_fault_code;
    wire reception_active;
    wire frame_complete;
    wire temporal_fault;
    wire [2:0] temporal_code;
    wire frame_fault;
    wire [2:0] frame_code;
    wire arb_set_fault;
    wire [2:0] arb_fault_code;
    wire [7:0] bit_counter;
    wire fault_latched;

    ares_sentinel_top #(
        .DATA_WIDTH(8)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .rx_in(rx_in),
        .ext_pos_edge(1'b0),
        .ext_neg_edge(1'b0),
        .use_ext_edges(1'b0),
        .serial_clock(serial_clock),
        .serial_data(serial_data),
        .raw_data_in(raw_data_in),
        .raw_valid_in(raw_valid_in),
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

    // Clock generation: 20 kHz -> period = 50,000 ns (25,000 ns half-period)
    initial clk = 0;
    always #25000 clk = ~clk;

    integer stim_file, out_file, trace_file;
    integer cycle_count;
    integer r_in, s_clk, s_data;
    integer scan_res;
    integer tamper_cycle;
    integer latched_code;
    integer isolation_latency;
    integer fault_condition_cycle;
    integer fault_latched_cycle;
    integer isolation_effective_cycle;
    integer safe_output_cycle;
    reg tamper_latched_seen;

    initial begin
        rst_n = 0;
        rx_in = 0;
        serial_clock = 0;
        serial_data = 0;
        raw_data_in = 8'h55;
        raw_valid_in = 1;
        cycle_count = 0;
        tamper_cycle = -1;
        latched_code = 0;
        isolation_latency = -1;
        fault_condition_cycle = -1;
        fault_latched_cycle = -1;
        isolation_effective_cycle = -1;
        safe_output_cycle = -1;
        tamper_latched_seen = 0;

        // Open stimulus file
        stim_file = $fopen("stimulus_in.txt", "r");
        if (stim_file == 0) begin
            $display("[ERROR] Could not open stimulus_in.txt");
            $finish;
        end

        // Open cycle-by-cycle observable trace output
        trace_file = $fopen("sim_trace.tsv", "w");
        if (trace_file == 0) begin
            $display("[ERROR] Could not open sim_trace.tsv");
            $finish;
        end

        // Header for observable trace
        $fwrite(trace_file, "cycle\trx_in\tserial_clock\tserial_data\treception_active\tframe_complete\ttemporal_fault\tframe_fault\ttamper_alert\tlatched_fault_code\tsafe_data_out\tsafe_valid_out\n");

        // Reset sequence: deassert on negedge clk
        @(negedge clk);
        rst_n = 0;
        rx_in = 0;
        serial_clock = 0;
        serial_data = 0;

        @(negedge clk);
        rst_n = 1;

        // Cycle-by-cycle stimulus injection synchronized on negedge
        while (!$feof(stim_file)) begin
            scan_res = $fscanf(stim_file, "%d %d %d\n", r_in, s_clk, s_data);
            if (scan_res == 3) begin
                rx_in = r_in[0];
                serial_clock = s_clk[0];
                serial_data = s_data[0];

                @(posedge clk);
                #1; // Post-edge evaluation
                cycle_count = cycle_count + 1;

                // Log all 11 observable signals on each cycle
                $fwrite(trace_file, "%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\t%0d\n",
                    cycle_count,
                    rx_in,
                    serial_clock,
                    serial_data,
                    reception_active,
                    frame_complete,
                    temporal_fault,
                    frame_fault,
                    tamper_alert,
                    latched_fault_code,
                    safe_data_out,
                    safe_valid_out
                );

                if ((temporal_fault || frame_fault) && (fault_condition_cycle == -1)) begin
                    fault_condition_cycle = cycle_count;
                end

                if (tamper_alert && !tamper_latched_seen) begin
                    tamper_latched_seen = 1;
                    tamper_cycle = cycle_count;
                    fault_latched_cycle = cycle_count;
                    latched_code = latched_fault_code;
                    if (safe_data_out == 8'h00) begin
                        isolation_effective_cycle = cycle_count;
                        safe_output_cycle = cycle_count;
                        isolation_latency = 1;
                    end
                end

                @(negedge clk);
            end
        end

        $fclose(stim_file);
        $fclose(trace_file);

        // Write simulation result JSON
        out_file = $fopen("sim_out.json", "w");
        $fwrite(out_file, "{\n");
        $fwrite(out_file, "  \"total_cycles\": %0d,\n", cycle_count);
        $fwrite(out_file, "  \"tamper_alert\": %0d,\n", tamper_latched_seen ? 1 : 0);
        $fwrite(out_file, "  \"detection_cycle\": %0d,\n", tamper_cycle);
        $fwrite(out_file, "  \"fault_code\": %0d,\n", latched_code);
        $fwrite(out_file, "  \"isolation_latency\": %0d,\n", isolation_latency);
        $fwrite(out_file, "  \"fault_condition_cycle\": %0d,\n", fault_condition_cycle);
        $fwrite(out_file, "  \"fault_latched_cycle\": %0d,\n", fault_latched_cycle);
        $fwrite(out_file, "  \"isolation_effective_cycle\": %0d,\n", isolation_effective_cycle);
        $fwrite(out_file, "  \"safe_output_cycle\": %0d,\n", safe_output_cycle);
        $fwrite(out_file, "  \"safe_data_out\": %0d\n", safe_data_out);
        $fwrite(out_file, "}\n");
        $fclose(out_file);

        $finish;
    end

endmodule
