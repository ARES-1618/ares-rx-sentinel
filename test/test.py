import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge

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

    # ui_in[0] is rx_in, ui_in[2] is halt=1
    dut.ui_in.value = (1 << 2) | lvl1
    await ClockCycles(dut.clk, 9)
    dut.ui_in.value = (1 << 2) | lvl2
    await ClockCycles(dut.clk, 9)

@cocotb.test()
async def test_nominal_transmission(dut):
    """Test 1: Verify clean nominal frame reception with zero false alarms."""
    await setup_dut(dut)

    # Lead-in arming pulses
    dut.ui_in.value = (1 << 2) | 1
    await ClockCycles(dut.clk, 9)
    dut.ui_in.value = (1 << 2) | 0
    await ClockCycles(dut.clk, 9)

    # Send 32-bit preamble (0xAA = 10101010)
    for _ in range(4):
        for bit in [1, 0, 1, 0, 1, 0, 1, 0]:
            await send_manchester_bit(dut, bit)

    # Verify tamper_alert is clean
    tamper = get_tamper_alert(dut)
    assert tamper == 0, f"False alarm: tamper_alert asserted ({tamper}) during nominal transmission!"
    dut._log.info("Nominal transmission test passed: tamper_alert = 0")

@cocotb.test()
async def test_runt_glitch_rejection(dut):
    """Test 2: Verify deterministic fail-closed trap on runt pulse."""
    await setup_dut(dut)

    # Lead-in arming pulses
    dut.ui_in.value = (1 << 2) | 1
    await ClockCycles(dut.clk, 9)
    dut.ui_in.value = (1 << 2) | 0
    await ClockCycles(dut.clk, 9)

    # Inject 4-cycle runt glitch (<8 cycles minimum valid half-bit)
    dut.ui_in.value = (1 << 2) | 1
    await ClockCycles(dut.clk, 4)
    dut.ui_in.value = (1 << 2) | 0
    # Wait 3 clock cycles for edge detection -> timing classifier -> sticky fault latch pipeline
    await ClockCycles(dut.clk, 3)

    # Check tamper_alert latched
    tamper = get_tamper_alert(dut)
    assert tamper == 1, f"Security breach: tamper_alert failed to latch on runt glitch! (got {tamper})"
    assert int(dut.uo_out.value) == 0, f"Fail-closed failure: parallel bus not zeroized! got: {dut.uo_out.value}"
    dut._log.info("Runt glitch rejection test passed: tamper_alert = 1, uo_out = 0x00")
