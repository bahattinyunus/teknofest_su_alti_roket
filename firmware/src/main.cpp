/**
 * @file main.cpp
 * @brief Open-Source Autonomous Underwater Rocket - Reference Flight Controller Main Entry
 * Architecture: STM32F407VG + FreeRTOS + CMSIS-DSP + Zero-Allocation ESKF
 * Purpose: Open reference architecture for TEKNOFEST & Roketsan underwater rocket teams
 */

#include "gatekeeper_task.h"
#include "software_watchdog.h"
#include "mission_manager.h"
#include "bno055.h"
#include "ms5837.h"
#include "eskf.hpp"
#include "pid.hpp"

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  #include "FreeRTOS.h"
  #include "task.h"
#endif

// Global Navigation Objects
static Navigation::UnderwaterESKF g_eskf;
static Navigation::PID g_depthPid(120.0f, 15.0f, 35.0f, -400.0f, 400.0f);
static Navigation::PID g_pitchPid(4.5f, 0.2f, 1.2f, -300.0f, 300.0f);
static Navigation::PID g_yawPid(5.0f, 0.1f, 1.5f, -350.0f, 350.0f);

static MS5837_Device_t g_barometer;
static BNO055_Device_t g_imu;

extern "C" void vSensorIOTask(void *pvParameters) {
    (void)pvParameters;

    for (;;) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
        // 50 Hz Sensor fusion loop (20ms)
        vTaskDelay(pdMS_TO_TICKS(20));

        // Read sensors with DMA / non-blocking driver calls
        MS5837_Read(&g_barometer);
        BNO055_Update(&g_imu);

        // ESKF predict & update
        float accelZ = g_imu.linearAccel.z;
        float gyroPitch = g_imu.gyro.y;
        g_eskf.predict(accelZ, gyroPitch, 0.02f);
        g_eskf.update(g_barometer.lastDepthMeters, g_imu.euler.pitch);

        // Control Loops
        float currentDepth = g_eskf.getEstimatedDepth();
        float currentPitch = g_eskf.getEstimatedPitch();

        float pitchTarget = g_depthPid.update(currentDepth, 0.02f);
        g_pitchPid.setSetpoint(pitchTarget);
        float finPitchEffort = g_pitchPid.update(currentPitch, 0.02f);

        // Queue actuator commands to Gatekeeper
        uint16_t topFinPwm = (uint16_t)(PWM_NEUTRAL_MICROSECONDS + finPitchEffort);
        uint16_t bottomFinPwm = (uint16_t)(PWM_NEUTRAL_MICROSECONDS - finPitchEffort);

        Gatekeeper_SendCommand(ACTUATOR_FIN_TOP, topFinPwm);
        Gatekeeper_SendCommand(ACTUATOR_FIN_BOTTOM, bottomFinPwm);

        // Feed software watchdog
        SoftwareWatchdog_Feed(TASK_ID_SENSOR_IO);
#endif
    }
}

int main(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    // 1. Initialize HAL and system clocks (168 MHz)
    HAL_Init();

    // 2. Initialize drivers and gatekeeper queue
    Gatekeeper_Init();
    SoftwareWatchdog_Init();
    Mission_Init();

    MS5837_Init(&g_barometer, myOSDelayFunction, DENSITY_SEAWATER);
    BNO055_Init(&g_imu, myOSDelayFunction, BNO055_I2C_ADDR_A);

    // 3. Create FreeRTOS Tasks with deterministic priority assignments
    xTaskCreate(vGatekeeperTask, "Gatekeeper", 256, NULL, 5, NULL);
    xTaskCreate(vSensorIOTask, "SensorIO", 512, NULL, 4, NULL);
    xTaskCreate(vMissionExecutionTask, "MissionMgr", 512, NULL, 3, NULL);
    xTaskCreate(vSoftwareWatchdogTask, "Watchdog", 128, NULL, 6, NULL);

    // 4. Start Kernel Scheduler
    vTaskStartScheduler();
#endif

    while (1) {
        // Should never reach here if FreeRTOS starts
    }
}
