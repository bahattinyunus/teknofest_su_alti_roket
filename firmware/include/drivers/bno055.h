#ifndef DRIVERS_BNO055_H
#define DRIVERS_BNO055_H

#include <stdint.h>
#include <stdbool.h>
#include "ms5837.h" /* For DelayCallback_t */

#ifdef __cplusplus
extern "C" {
#endif

#define BNO055_I2C_ADDR_A     (0x28 << 1)
#define BNO055_I2C_ADDR_B     (0x29 << 1)

typedef struct {
    float roll;    /* degrees */
    float pitch;   /* degrees */
    float yaw;     /* degrees (0-360) */
} EulerAngles_t;

typedef struct {
    float w;
    float x;
    float y;
    float z;
} Quaternion_t;

typedef struct {
    float x;
    float y;
    float z;
} Vector3_t;

typedef struct {
    DelayCallback_t delay_ms;
    uint8_t i2cAddr;
    EulerAngles_t euler;
    Quaternion_t quat;
    Vector3_t gyro;
    Vector3_t linearAccel;
    uint8_t calibSys;
    uint8_t calibGyro;
    uint8_t calibAccel;
    uint8_t calibMag;
    bool isCalibrated;
} BNO055_Device_t;

/**
 * @brief Initialize BNO055 in NDOF (9-Degrees of Freedom Fusion) Mode.
 */
bool BNO055_Init(BNO055_Device_t *dev, DelayCallback_t delayFunc, uint8_t addr);

/**
 * @brief Read Euler angles, Quaternion and Angular rates.
 */
bool BNO055_Update(BNO055_Device_t *dev);

/**
 * @brief Read calibration status (0-3 for each sensor).
 */
void BNO055_GetCalibration(BNO055_Device_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* DRIVERS_BNO055_H */
