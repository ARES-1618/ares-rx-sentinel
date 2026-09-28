# ARES-RX Sentinel — Industrial SoC Integration Package
## Directory: `03_Core_Projects/ARES-RX_Sentinel/integration/`

This package provides standard bus wrappers and software drivers to integrate **ARES-RX Sentinel** as a hardware IP block into modern 32-bit System-on-Chip (SoC) architectures (e.g. RISC-V Ibex, CV32E40P, ARM Cortex-M0+/M3/M4, or Peruri Secure Microcontrollers).

---

## 1. Package Contents

* [`ares_sentinel_apb.v`](ares_sentinel_apb.v): Synthesizable AMBA APB4 protocol slave interface wrapper.
* [`ares_sentinel_regs.h`](ares_sentinel_regs.h): ANSI C99 / MISRA-C compliant memory-mapped register header and device driver.

---

## 2. Memory Map & Register Definitions

All registers are word-aligned (4 bytes) within a 256-byte peripheral address space:

| Offset | Register Name | R/W | Description |
| :--- | :--- | :--- | :--- |
| `0x00` | `REG_CTRL` | R/W | Core Enable, Interrupt Masking, Soft Reset Trigger |
| `0x04` | `REG_STATUS` | RO | Real-time reception status, bit counter, tamper alert |
| `0x08` | `REG_FAULT_CODE` | RO | Diagnostic root-cause fault codes (L1 temporal, L2 syntax) |
| `0x0C` | `REG_UNLOCK_KEY` | WO | Security authorization key (`0xA8E5_2026`) to unlock fault clear |
| `0x10` | `REG_PAYLOAD_LO` | RO | Deserialized dynamic telemetry bits 31..0 (Device ID) |
| `0x14` | `REG_PAYLOAD_MID`| RO | Deserialized dynamic telemetry bits 63..32 (Temperatures) |
| `0x18` | `REG_PAYLOAD_HI` | RO | Deserialized dynamic telemetry bits 71..64 (System State) |
| `0x1C` | `REG_HARDWARE_ID`| RO | Hardware identity constant: `0x41524553` ("ARES") |

---

## 3. SoC Firmware Integration Example (C)

```c
#include "ares_sentinel_regs.h"

// Define base address mapped in SoC interconnect (e.g. 0x4000_2000)
#define ARES_SENTINEL_BASE_ADDR   ((ares_sentinel_hw_t *)0x40002000U)

void init_security_sentinel(void) {
    if (!ares_sentinel_init(ARES_SENTINEL_BASE_ADDR)) {
        // Hardware failure or invalid peripheral ID
        panic_handler();
    }
}

// Interrupt Service Routine for Tamper Alert (Connected to CPU IRQ)
void ARES_TAMPER_IRQHandler(void) {
    if (ares_sentinel_is_tampered(ARES_SENTINEL_BASE_ADDR)) {
        ares_fault_code_t fault = ares_sentinel_get_fault(ARES_SENTINEL_BASE_ADDR);
        
        // Log security breach to secure audit log
        log_security_breach(fault);
        
        // Quarantine communication channel
        quarantine_rf_transceiver();
        
        // Clear fault only after cryptographic challenge-response authentication
        if (authenticate_peruri_admin()) {
            ares_sentinel_clear_tamper(ARES_SENTINEL_BASE_ADDR, ARES_SENTINEL_SECURITY_UNLOCK_KEY);
        }
    }
}
```

---

## 4. Hardware Demarcation & Immutability Guarantee

* **Preservation of Core RTL**: The underlying Sentinel core (`ares_sentinel_top.v` and its submodules) in `ares_sentinel/` remains 100% untouched and cryptographically frozen.
* **Pure Additive Architecture**: The APB wrapper acts as a non-invasive translation bridge from memory-mapped bus transactions to the Sentinel core's native ports.
