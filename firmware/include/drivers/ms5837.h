#ifndef DRIVERS_MS5837_H
#define DRIVERS_MS5837_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MS5837_I2C_ADDR       (0x76 << 1) /* 7-bit 0x76 shifted for STM32 HAL */

/* Water densities */
#define DENSITY_FRESHWATER    997.0f  /* kg/m^3 (e.g. ITU Olympic Pool) */
#define DENSITY_SEAWATER      1029.0f /* kg/m^3 (e.g. ITU Tuzla Marine Test) */

typedef void (*DelayCallback_t)(uint32_t ms);

typedef struct {
    DelayCallback_t delay_ms;
    float fluidDensity;
    float surfacePressureBar;
    uint16_t c[8]; /* Factory PROM calibration coeffs */
    float lastPressureMbar;
    float lastTemperatureC;
    float lastDepthMeters;
} MS5837_Device_t;

/**
 * @brief Initialize MS5837 driver with OS-agnostic delay function.
 */
bool MS5837_Init(MS5837_Device_t *dev, DelayCallback_t delayFunc, float fluidDensity);

/**
 * @brief Read pressure (mbar), temperature (°C), and calculate depth (meters).
 */
bool MS5837_Read(MS5837_Device_t *dev);

/**
 * @brief Zero the current depth measurement at the surface.
 */
void MS5837_Tare(MS5837_Device_t *dev);

/**
 * @brief Execute I2C Bus Lock Recovery by clocking SCL 9 times to free stuck SDA line.
 */
void I2C_BusLock_Recovery(void);

#ifdef __cplusplus
}
#endif

#endif /* DRIVERS_MS5837_H */
