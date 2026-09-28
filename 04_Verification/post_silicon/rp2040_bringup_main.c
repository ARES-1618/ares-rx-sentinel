/**
 * ==============================================================================
 * Project: ARES-RX Sentinel — Post-Silicon Validation Firmware
 * File:    rp2040_bringup_main.c
 * Target:  Raspberry Pi Pico (RP2040 Dual ARM Cortex-M0+ @ 133 MHz)
 * SDK:     Raspberry Pi Pico C/C++ SDK
 *
 * Description:
 *   Autonomous laboratory benchtop test runner for validating physical
 *   SkyWater 130nm TT08 ARES-RX Sentinel silicon chips.
 *
 * Pin Assignment (Raspberry Pi Pico -> TT08 Carrier Board):
 *   GPIO 2  -> clk (Master Clock, 20 kHz synchronous square wave)
 *   GPIO 3  -> rst_n (Active-low system reset)
 *   GPIO 4  -> rx_in (Baseband digital pulse injection)
 *   GPIO 5  <- tamper_alert (Security fault interrupt monitor)
 *   GPIO 6  <- reception_active (Layer-1 RF envelope monitor)
 *   GPIO 8..15 <- uo_out[7:0] (Safe 8-bit parallel data output bus)
 * ==============================================================================
 */

#include <stdio.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "stimulus_vectors.h"

#define PIN_CLK              2
#define PIN_RST_N            3
#define PIN_RX_IN            4
#define PIN_TAMPER_ALERT     5
#define PIN_RECEPTION_ACTIVE 6
#define PIN_DATA_BASE        8   // 8 pins: GPIO 8..15

#define F_CLK_HZ             20000
#define HALF_CLK_PERIOD_US   25  // 20 kHz period = 50 us -> 25 us high, 25 us low

static void init_harness_gpio(void) {
    // Outputs to DUT
    gpio_init(PIN_CLK);
    gpio_set_dir(PIN_CLK, GPIO_OUT);
    gpio_put(PIN_CLK, 0);

    gpio_init(PIN_RST_N);
    gpio_set_dir(PIN_RST_N, GPIO_OUT);
    gpio_put(PIN_RST_N, 0); // Hold in reset

    gpio_init(PIN_RX_IN);
    gpio_set_dir(PIN_RX_IN, GPIO_OUT);
    gpio_put(PIN_RX_IN, 0);

    // Inputs from DUT
    gpio_init(PIN_TAMPER_ALERT);
    gpio_set_dir(PIN_TAMPER_ALERT, GPIO_IN);

    gpio_init(PIN_RECEPTION_ACTIVE);
    gpio_set_dir(PIN_RECEPTION_ACTIVE, GPIO_IN);

    for (int i = 0; i < 8; i++) {
        gpio_init(PIN_DATA_BASE + i);
        gpio_set_dir(PIN_DATA_BASE + i, GPIO_IN);
    }
}

static void apply_hardware_reset(void) {
    gpio_put(PIN_RST_N, 0);
    sleep_ms(5);
    gpio_put(PIN_RST_N, 1);
    sleep_ms(5);
}

static uint8_t read_data_bus(void) {
    uint8_t val = 0;
    for (int i = 0; i < 8; i++) {
        if (gpio_get(PIN_DATA_BASE + i)) {
            val |= (1 << i);
        }
    }
    return val;
}

static bool test_nominal_transmission(void) {
    printf("[TEST 1] Executing Nominal 192-bit Transmission Test...\n");
    apply_hardware_reset();

    size_t num_pulses = sizeof(nominal_frame_stimulus) / sizeof(stimulus_pulse_t);
    bool tamper_seen = false;

    for (size_t i = 0; i < num_pulses; i++) {
        uint8_t lvl = nominal_frame_stimulus[i].level;
        uint16_t dur = nominal_frame_stimulus[i].duration_us;

        gpio_put(PIN_RX_IN, lvl);

        // Run clock while waiting
        uint32_t elapsed = 0;
        while (elapsed < dur) {
            gpio_put(PIN_CLK, 1);
            sleep_us(HALF_CLK_PERIOD_US);
            gpio_put(PIN_CLK, 0);
            sleep_us(HALF_CLK_PERIOD_US);
            elapsed += (2 * HALF_CLK_PERIOD_US);

            if (gpio_get(PIN_TAMPER_ALERT)) {
                tamper_seen = true;
            }
        }
    }

    uint8_t bus_val = read_data_bus();
    printf("         Output Data Bus: 0x%02X | Tamper Strobe: %d\n", bus_val, tamper_seen ? 1 : 0);

    if (!tamper_seen) {
        printf("         -> RESULT: PASS (Zero false alarm)\n\n");
        return true;
    } else {
        printf("         -> RESULT: FAIL (Unexpected tamper alert on nominal frame)\n\n");
        return false;
    }
}

static bool test_runt_glitch_injection(void) {
    printf("[TEST 2] Executing Adversarial Runt-Pulse Glitch Injection Test...\n");
    apply_hardware_reset();

    // 1. Arming lead-in
    gpio_put(PIN_RX_IN, 1);
    sleep_us(450);
    gpio_put(PIN_RX_IN, 0);
    sleep_us(450);

    // 2. Inject 200 us runt pulse (< 400 us minimum valid half-bit)
    gpio_put(PIN_RX_IN, 1);
    
    // Clock 4 cycles
    for (int c = 0; c < 4; c++) {
        gpio_put(PIN_CLK, 1); sleep_us(HALF_CLK_PERIOD_US);
        gpio_put(PIN_CLK, 0); sleep_us(HALF_CLK_PERIOD_US);
    }
    gpio_put(PIN_RX_IN, 0);

    // Clock another cycle to latch fault
    gpio_put(PIN_CLK, 1); sleep_us(HALF_CLK_PERIOD_US);
    gpio_put(PIN_CLK, 0); sleep_us(HALF_CLK_PERIOD_US);

    bool tamper = gpio_get(PIN_TAMPER_ALERT);
    uint8_t bus_val = read_data_bus();

    printf("         Output Data Bus: 0x%02X | Tamper Strobe: %d\n", bus_val, tamper ? 1 : 0);

    if (tamper && bus_val == 0x00) {
        printf("         -> RESULT: PASS (Runt trapped in 1 cycle, bus zeroized)\n\n");
        return true;
    } else {
        printf("         -> RESULT: FAIL (Glitch leaked through or unlatched)\n\n");
        return false;
    }
}

int main(void) {
    stdio_init_all();
    sleep_ms(2000); // Wait for USB-CDC terminal connection

    printf("==============================================================\n");
    printf("   ARES-RX SENTINEL: PHYSICAL SILICON POST-BRINGUP RUNNER     \n");
    printf("   Target: SkyWater 130nm TT08 ASIC Test Coupon               \n");
    printf("==============================================================\n\n");

    init_harness_gpio();

    bool pass1 = test_nominal_transmission();
    bool pass2 = test_runt_glitch_injection();

    printf("--------------------------------------------------------------\n");
    if (pass1 && pass2) {
        printf(">>> ALL SILICON BENCHTOP ACCEPTANCE TESTS PASSED (100%%) <<<\n");
    } else {
        printf(">>> SOME ACCEPTANCE TESTS FAILED — CHECK WIRE CONNECTIONS <<<\n");
    }
    printf("--------------------------------------------------------------\n");

    while (true) {
        tight_loop_contents();
    }
    return 0;
}
