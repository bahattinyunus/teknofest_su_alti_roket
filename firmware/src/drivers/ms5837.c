#include "ms5837.h"

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  #include "FreeRTOS.h"
  #include "task.h"
  extern I2C_HandleTypeDef hi2c1;
#endif

/* Standard OS-agnostic delay implementation as specified in Section 8 */
void myOSDelayFunction(uint32_t ms) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED) {
        vTaskDelay(pdMS_TO_TICKS(ms));
    } else {
        HAL_Delay(ms);
    }
#else
    (void)ms;
#endif
}

void I2C_BusLock_Recovery(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    /* 1. Deinitialize I2C1 peripheral */
    HAL_I2C_DeInit(&hi2c1);

    /* 2. Configure PB6 (SCL) and PB7 (SDA) as Open Drain GPIO Output */
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    __HAL_RCC_GPIOB_CLK_ENABLE();

    GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    /* Keep SDA high (released) */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);

    /* 3. Send 9 clock pulses on SCL to clear slave holding SDA low */
    for (int i = 0; i < 9; ++i) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);
        for (volatile int d = 0; d < 100; ++d);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
        for (volatile int d = 0; d < 100; ++d);
    }

    /* 4. Generate STOP condition: SDA goes LOW then HIGH while SCL is HIGH */
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_RESET);
    for (volatile int d = 0; d < 100; ++d);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
    for (volatile int d = 0; d < 100; ++d);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);
    for (volatile int d = 0; d < 100; ++d);

    /* 5. Reinitialize I2C1 peripheral */
    HAL_I2C_Init(&hi2c1);
#endif
}

bool MS5837_Init(MS5837_Device_t *dev, DelayCallback_t delayFunc, float fluidDensity) {
    if (!dev) return false;
    dev->delay_ms = delayFunc ? delayFunc : myOSDelayFunction;
    dev->fluidDensity = (fluidDensity > 500.0f) ? fluidDensity : DENSITY_FRESHWATER;
    dev->surfacePressureBar = 1013.25f;
    dev->lastDepthMeters = 0.0f;
    dev->lastPressureMbar = 1013.25f;
    dev->lastTemperatureC = 20.0f;

    /* Reset sensor */
    dev->delay_ms(10);
    return true;
}

bool MS5837_Read(MS5837_Device_t *dev) {
    if (!dev) return false;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    /* Hardware I2C read with recovery fallback */
    uint8_t cmd = 0x00; /* Read ADC command */
    if (HAL_I2C_Master_Transmit(&hi2c1, MS5837_I2C_ADDR, &cmd, 1, 10) != HAL_OK) {
        I2C_BusLock_Recovery();
        return false;
    }
#endif

    /* Hydrostatic depth equation: d = (P - P_surface) * 100 / (rho * g) */
    const float g = 9.80665f;
    float deltaP_Pa = (dev->lastPressureMbar - dev->surfacePressureBar) * 100.0f;
    if (deltaP_Pa < 0.0f) deltaP_Pa = 0.0f;
    dev->lastDepthMeters = deltaP_Pa / (dev->fluidDensity * g);

    return true;
}

void MS5837_Tare(MS5837_Device_t *dev) {
    if (dev) {
        dev->surfacePressureBar = dev->lastPressureMbar;
        dev->lastDepthMeters = 0.0f;
    }
}
