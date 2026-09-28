/**
 * ==============================================================================
 * Project: ARES-RX Sentinel — Trusted Digital Reception Boundary
 * File:    ares_sentinel_regs.h
 * Standard: ANSI C99 / MISRA-C Compliant Device Driver Header
 * Classification: SoC Embedded Driver for Peruri Secure Element / RISC-V SoC
 *
 * Description:
 *   Memory-mapped register map, bit masks, and hardware access abstraction
 *   for the ARES-RX Sentinel APB4 slave IP block.
 * ==============================================================================
 */

#ifndef ARES_SENTINEL_REGS_H
#define ARES_SENTINEL_REGS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------- */
/* Hardware Identification & Magic Keys                                       */
/* -------------------------------------------------------------------------- */
#define ARES_SENTINEL_HARDWARE_ID          0x41524553U  /**< "ARES" in ASCII */
#define ARES_SENTINEL_SECURITY_UNLOCK_KEY  0xA8E52026U  /**< Fault reset authorization key */

/* -------------------------------------------------------------------------- */
/* Register Memory Map Offsets (Bytes, 32-bit aligned)                        */
/* -------------------------------------------------------------------------- */
#define ARES_REG_CTRL_OFFSET               0x00U  /**< Control Register (RW) */
#define ARES_REG_STATUS_OFFSET             0x04U  /**< Status Register (RO) */
#define ARES_REG_FAULT_CODE_OFFSET         0x08U  /**< Fault Code Telemetry (RO) */
#define ARES_REG_UNLOCK_KEY_OFFSET         0x0CU  /**< Security Unlock Key (WO) */
#define ARES_REG_PAYLOAD_LO_OFFSET         0x10U  /**< Dynamic Payload Bits 31..0 (RO) */
#define ARES_REG_PAYLOAD_MID_OFFSET        0x14U  /**< Dynamic Payload Bits 63..32 (RO) */
#define ARES_REG_PAYLOAD_HI_OFFSET         0x18U  /**< Dynamic Payload Bits 71..64 (RO) */
#define ARES_REG_HARDWARE_ID_OFFSET        0x1CU  /**< Hardware Identification (RO) */

/* -------------------------------------------------------------------------- */
/* Register Bitfield Masks & Shifts                                           */
/* -------------------------------------------------------------------------- */

/* REG_CTRL (0x00) */
#define ARES_CTRL_ENABLE_MASK              (1U << 0)  /**< 1 = Active, 0 = Standby */
#define ARES_CTRL_IRQ_TAMPER_EN_MASK       (1U << 1)  /**< Enable Tamper Alert IRQ */
#define ARES_CTRL_IRQ_RX_EN_MASK           (1U << 2)  /**< Enable RX Complete IRQ */
#define ARES_CTRL_FAULT_CLEAR_MASK         (1U << 8)  /**< Software Fault Reset Strobe */

/* REG_STATUS (0x04) */
#define ARES_STATUS_RECEPTION_ACTIVE_MASK  (1U << 0)  /**< RF Baseband Envelope Active */
#define ARES_STATUS_FRAME_COMPLETE_MASK    (1U << 1)  /**< 192-bit Frame Verified Clean */
#define ARES_STATUS_FAULT_LATCHED_MASK     (1U << 2)  /**< Sticky Hardware Fault Latched */
#define ARES_STATUS_TAMPER_ALERT_MASK      (1U << 3)  /**< Active Tamper Strobe */
#define ARES_STATUS_BIT_COUNTER_SHIFT      (8U)
#define ARES_STATUS_BIT_COUNTER_MASK       (0xFFU << ARES_STATUS_BIT_COUNTER_SHIFT)

/* REG_FAULT_CODE (0x08) */
#define ARES_FAULT_CODE_LATCHED_MASK       (0x07U)     /**< Primary Latched Fault Code */
#define ARES_FAULT_CODE_TEMPORAL_SHIFT     (4U)
#define ARES_FAULT_CODE_TEMPORAL_MASK      (0x07U << ARES_FAULT_CODE_TEMPORAL_SHIFT)
#define ARES_FAULT_CODE_FRAME_SHIFT        (8U)
#define ARES_FAULT_CODE_FRAME_MASK         (0x07U << ARES_FAULT_CODE_FRAME_SHIFT)

/* Enumerated Fault Codes */
typedef enum {
    ARES_FAULT_NONE              = 0x0U,  /**< System nominal, zero faults */
    ARES_FAULT_L1_RUNT_GLITCH    = 0x1U,  /**< Pulse duration N <= 7 cycles */
    ARES_FAULT_L1_MIDBAND_DESYNC = 0x2U,  /**< Pulse duration 11 <= N <= 15 cycles */
    ARES_FAULT_L1_TIMEOUT        = 0x3U,  /**< Missing edge timeout N >= 21 cycles */
    ARES_FAULT_L2_PREAMBLE       = 0x4U,  /**< Corrupted 32-bit preamble (not 0xAAAAAAAA) */
    ARES_FAULT_L2_TYPE_CONST     = 0x5U,  /**< Corrupted type or constant field */
    ARES_FAULT_L2_TRUNCATION     = 0x6U,  /**< Premature carrier drop before 192 bits */
    ARES_FAULT_L2_OVERRUN        = 0x7U   /**< Extra clock pulses post 192 bits */
} ares_fault_code_t;

/* -------------------------------------------------------------------------- */
/* Memory-Mapped Hardware Peripheral Structure                                */
/* -------------------------------------------------------------------------- */
typedef struct {
    volatile uint32_t CTRL;         /**< 0x00: Control Register (RW) */
    volatile uint32_t STATUS;       /**< 0x04: Status Register (RO) */
    volatile uint32_t FAULT_CODE;   /**< 0x08: Fault Telemetry (RO) */
    volatile uint32_t UNLOCK_KEY;   /**< 0x0C: Security Unlock Key (WO) */
    volatile uint32_t PAYLOAD_LO;   /**< 0x10: Dynamic Payload Bits 31..0 (RO) */
    volatile uint32_t PAYLOAD_MID;  /**< 0x14: Dynamic Payload Bits 63..32 (RO) */
    volatile uint32_t PAYLOAD_HI;   /**< 0x18: Dynamic Payload Bits 71..64 (RO) */
    volatile uint32_t HARDWARE_ID;  /**< 0x1C: Hardware Identification (RO) */
} ares_sentinel_hw_t;

/* -------------------------------------------------------------------------- */
/* High-Level Driver Inline Helper Functions                                  */
/* -------------------------------------------------------------------------- */

/**
 * @brief Initialize ARES-RX Sentinel peripheral.
 * @param hw Pointer to peripheral base address.
 * @return true if valid ARES-RX Sentinel hardware detected, false otherwise.
 */
static inline bool ares_sentinel_init(ares_sentinel_hw_t *hw) {
    if (hw == (void *)0) return false;
    if (hw->HARDWARE_ID != ARES_SENTINEL_HARDWARE_ID) return false;

    // Enable Sentinel with default interrupt generation
    hw->CTRL = ARES_CTRL_ENABLE_MASK | ARES_CTRL_IRQ_TAMPER_EN_MASK | ARES_CTRL_IRQ_RX_EN_MASK;
    return true;
}

/**
 * @brief Check if hardware tamper has occurred.
 * @param hw Pointer to peripheral base address.
 * @return true if tamper latched, false if safe.
 */
static inline bool ares_sentinel_is_tampered(const ares_sentinel_hw_t *hw) {
    return (hw->STATUS & ARES_STATUS_FAULT_LATCHED_MASK) != 0U;
}

/**
 * @brief Retrieve the root-cause fault code.
 * @param hw Pointer to peripheral base address.
 * @return Categorized fault code enum.
 */
static inline ares_fault_code_t ares_sentinel_get_fault(const ares_sentinel_hw_t *hw) {
    return (ares_fault_code_t)(hw->FAULT_CODE & ARES_FAULT_CODE_LATCHED_MASK);
}

/**
 * @brief Read deserialized clean telemetry payload.
 * @param hw Pointer to peripheral base address.
 * @param[out] device_id Extracted 32-bit Device / Thermostat ID.
 * @param[out] room_temp Extracted 16-bit Room Temperature.
 * @param[out] set_temp  Extracted 16-bit Target Temperature.
 * @return true if telemetry is valid and untampered, false otherwise.
 */
static inline bool ares_sentinel_read_telemetry(const ares_sentinel_hw_t *hw,
                                               uint32_t *device_id,
                                               uint16_t *room_temp,
                                               uint16_t *set_temp) {
    if (ares_sentinel_is_tampered(hw)) return false;
    if ((hw->STATUS & ARES_STATUS_FRAME_COMPLETE_MASK) == 0U) return false;

    if (device_id != (void *)0) *device_id = hw->PAYLOAD_LO;
    if (room_temp != (void *)0) *room_temp = (uint16_t)(hw->PAYLOAD_MID & 0xFFFFU);
    if (set_temp != (void *)0)  *set_temp  = (uint16_t)((hw->PAYLOAD_MID >> 16U) & 0xFFFFU);

    return true;
}

/**
 * @brief Clear sticky tamper fault using cryptographic unlock authorization key.
 * @param hw Pointer to peripheral base address.
 * @param key Security authorization key (must match ARES_SENTINEL_SECURITY_UNLOCK_KEY).
 * @return true if fault cleared successfully, false if unauthorized.
 */
static inline bool ares_sentinel_clear_tamper(ares_sentinel_hw_t *hw, uint32_t key) {
    hw->UNLOCK_KEY = key;
    hw->CTRL |= ARES_CTRL_FAULT_CLEAR_MASK;
    return !ares_sentinel_is_tampered(hw);
}

#ifdef __cplusplus
}
#endif

#endif /* ARES_SENTINEL_REGS_H */
