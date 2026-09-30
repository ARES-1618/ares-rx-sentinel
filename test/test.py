import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

# Clock frequency = 20 kHz -> Period = 50,000 ns = 50 us
CLOCK_PERIOD_NS = 50_000

def get_tamper_alert(dut):
    """Robustly extract tamper_alert whether via scalar wire or bus bit."""
    try:
        if hasattr(dut, "tamper_alert"):
            return int(dut.tamper_alert.value)
    except Exception:
        pass
    return (int(dut.uio_out.value) >> 6) & 1

async def setup_dut(dut):
    """Initialize inputs and reset DUT."""
    clock = Clock(dut.clk, CLOCK_PERIOD_NS, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

async def send_manchester_bit(dut, bit):
    """Send a Manchester-encoded bit (9 cycles high/low)."""
    # Bit 1: High for 9 cycles, Low for 9 cycles
    # Bit 0: Low for 9 cycles, High for 9 cycles
    lvl1 = 1 if bit == 1 else 0
    lvl2 = 0 if bit == 1 else 1

    # halt = 0 during active reception (ui_in[2] = 0, ui_in[0] = rx_in)
    dut.ui_in.value = lvl1
    await ClockCycles(dut.clk, 9)
    dut.ui_in.value = lvl2
    await ClockCycles(dut.clk, 9)

@cocotb.test()
async def test_nominal_transmission(dut):
    """Test 1: Verify clean nominal frame reception with zero false alarms."""
    await setup_dut(dut)

    # Nominal 192-bit frame:
    # Preamble (32b): 0xAAAAAAAA
    # Type 1 (16b): 0xD391, Type 2 (16b): 0xD391
    # Constant (32b): 0x0DFFFFFE
    # Thermostat ID (32b): 0x03391F89
    # Room Temp (16b): 0x00F6 (246)
    # Set Temp (16b): 0x00B5 (181)
    # State (8b): 0x00
    # Tail 1 (8b): 0x94, Tail 2 (8b): 0xAE, Tail 3 (8b): 0x16
    nominal_hex = "aaaaaaaad391d3910dfffffe03391f8900f600b50094ae16"
    nominal_bits = [int(b) for b in bin(int(nominal_hex, 16))[2:].zfill(192)]

    # Stream the full 192-bit frame without spurious lead-in pulses
    for bit in nominal_bits:
        await send_manchester_bit(dut, bit)

    # Wait 65 silence cycles for End-of-Packet (EOP) settling (> EOF_CYC = 64)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 65)

    # Verify tamper_alert remains low (no false alarms)
    tamper = get_tamper_alert(dut)
    assert tamper == 0, f"False alarm: tamper_alert asserted ({tamper}) during nominal transmission!"

    # Set halt = 1 to enable parallel output bus readback
    # Verify all 12 multiplexer registers (address = 0..11)
    expected_registers = {
        0: 0x89,  # thermostat_id[7:0]
        1: 0x1F,  # thermostat_id[15:8]
        2: 0x39,  # thermostat_id[23:16]
        3: 0x03,  # thermostat_id[31:24]
        4: 0xF6,  # room_temp[7:0]
        5: 0x00,  # room_temp[15:8]
        6: 0xB5,  # set_temp[7:0]
        7: 0x00,  # set_temp[15:8]
        8: 0x00,  # state
        9: 0x94,  # tail_1
        10: 0xAE, # tail_2
        11: 0x16, # tail_3
    }

    for addr, exp_val in expected_registers.items():
        # ui_in[7:4] = address, ui_in[2] = halt (1), ui_in[0] = rx_in (0)
        dut.ui_in.value = (addr << 4) | (1 << 2)
        await ClockCycles(dut.clk, 2)
        val = int(dut.uo_out.value)
        assert val == exp_val, f"Register mismatch at address {addr}: expected 0x{exp_val:02X}, got 0x{val:02X}"

    assert get_tamper_alert(dut) == 0, "tamper_alert asserted after frame readback!"
    dut._log.info("Nominal transmission test passed: all 12 registers verified, tamper_alert = 0")

@cocotb.test()
async def test_runt_glitch_rejection(dut):
    """Test 2: Verify deterministic fail-closed trap on runt pulse and zeroization when halt = 1."""
    await setup_dut(dut)

    # Arming pulse to transition Layer-1 Sentinel from IDLE -> ARMED -> ACTIVE (halt = 0)
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 9)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 9)

    # Inject 4-cycle runt glitch (<8 cycles minimum valid half-bit HB_MIN)
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 4)
    dut.ui_in.value = 0

    # Wait 3 clock cycles for edge detection -> timing classifier -> sticky fault latch pipeline
    await ClockCycles(dut.clk, 3)

    # Verify sticky latching of tamper_alert == 1
    tamper = get_tamper_alert(dut)
    assert tamper == 1, f"Security breach: tamper_alert failed to latch on runt glitch! (got {tamper})"

    # Verify zeroization of uo_out when halt = 1 across all multiplexer addresses
    for addr in range(12):
        dut.ui_in.value = (addr << 4) | (1 << 2)
        await ClockCycles(dut.clk, 2)
        assert int(dut.uo_out.value) == 0, f"Fail-closed failure at address {addr}: parallel bus not zeroized! got: {dut.uo_out.value}"

    # Confirm tamper_alert remains sticky high
    assert get_tamper_alert(dut) == 1, "tamper_alert unexpectedly cleared after readback!"
    dut._log.info("Runt glitch rejection test passed: tamper_alert = 1 sticky, uo_out = 0x00 across all addresses with halt = 1")
