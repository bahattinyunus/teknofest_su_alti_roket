#include "bno055.h"

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  extern I2C_HandleTypeDef hi2c1;
#endif

/* BNO055 Register definitions */
#define BNO055_PAGE_ID_ADDR         0X07
#define BNO055_CHIP_ID_ADDR         0x00
#define BNO055_OPR_MODE_ADDR        0x3D
#define BNO055_SYS_TRIGGER_ADDR     0x3F
#define BNO055_PWR_MODE_ADDR        0x3E
#define BNO055_CALIB_STAT_ADDR      0x35
#define BNO055_EULER_H_LSB_ADDR     0x1A
#define BNO055_QUAT_DATA_W_LSB_ADDR 0x20

#define OPERATION_MODE_CONFIG       0x00
#define OPERATION_MODE_NDOF         0x0C

bool BNO055_Init(BNO055_Device_t *dev, DelayCallback_t delayFunc, uint8_t addr) {
    if (!dev) return false;
    dev->delay_ms = delayFunc ? delayFunc : myOSDelayFunction;
    dev->i2cAddr = addr ? addr : BNO055_I2C_ADDR_A;
    dev->euler.roll = 0.0f;
    dev->euler.pitch = 0.0f;
    dev->euler.yaw = 0.0f;
    dev->quat.w = 1.0f;
    dev->quat.x = 0.0f;
    dev->quat.y = 0.0f;
    dev->quat.z = 0.0f;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    /* Verify Chip ID */
    uint8_t chipId = 0;
    if (HAL_I2C_Mem_Read(&hi2c1, dev->i2cAddr, BNO055_CHIP_ID_ADDR, 1, &chipId, 1, 50) != HAL_OK || chipId != 0xA0) {
        return false;
    }

    /* Switch to Config Mode */
    uint8_t mode = OPERATION_MODE_CONFIG;
    HAL_I2C_Mem_Write(&hi2c1, dev->i2cAddr, BNO055_OPR_MODE_ADDR, 1, &mode, 1, 50);
    dev->delay_ms(25);

    /* Normal Power Mode */
    uint8_t pwr = 0x00;
    HAL_I2C_Mem_Write(&hi2c1, dev->i2cAddr, BNO055_PWR_MODE_ADDR, 1, &pwr, 1, 50);
    dev->delay_ms(10);

    /* Switch to 9-DoF Fusion (NDOF) */
    mode = OPERATION_MODE_NDOF;
    HAL_I2C_Mem_Write(&hi2c1, dev->i2cAddr, BNO055_OPR_MODE_ADDR, 1, &mode, 1, 50);
    dev->delay_ms(20);
#endif
    return true;
}

bool BNO055_Update(BNO055_Device_t *dev) {
    if (!dev) return false;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    uint8_t buffer[6];
    /* Read Euler heading, roll, pitch (6 bytes, signed 16-bit, 1 LSB = 1/16 degree) */
    if (HAL_I2C_Mem_Read(&hi2c1, dev->i2cAddr, BNO055_EULER_H_LSB_ADDR, 1, buffer, 6, 20) == HAL_OK) {
        int16_t h = (int16_t)((buffer[1] << 8) | buffer[0]);
        int16_t r = (int16_t)((buffer[3] << 8) | buffer[2]);
        int16_t p = (int16_t)((buffer[5] << 8) | buffer[4]);

        dev->euler.yaw = (float)h / 16.0f;
        dev->euler.roll = (float)r / 16.0f;
        dev->euler.pitch = (float)p / 16.0f;
        return true;
    }
    return false;
#else
    return true;
#endif
}

void BNO055_GetCalibration(BNO055_Device_t *dev) {
    if (!dev) return;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    uint8_t calData = 0;
    if (HAL_I2C_Mem_Read(&hi2c1, dev->i2cAddr, BNO055_CALIB_STAT_ADDR, 1, &calData, 1, 20) == HAL_OK) {
        dev->calibMag   = (calData >> 0) & 0x03;
        dev->calibAccel = (calData >> 2) & 0x03;
        dev->calibGyro  = (calData >> 4) & 0x03;
        dev->calibSys   = (calData >> 6) & 0x03;
        dev->isCalibrated = (dev->calibGyro >= 2 && dev->calibAccel >= 2);
    }
#else
    dev->calibSys = 3;
    dev->calibGyro = 3;
    dev->calibAccel = 3;
    dev->calibMag = 3;
    dev->isCalibrated = true;
#endif
}
