#include "software_watchdog.h"
#include <string.h>

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  #include "FreeRTOS.h"
  #include "task.h"
#else
  static uint32_t simulated_tick = 0;
  #define xTaskGetTickCount() (simulated_tick++)
  #define pdMS_TO_TICKS(ms) (ms)
  #define vTaskDelay(t)
#endif

typedef struct {
    uint32_t lastFeedTick;
    bool isActive;
} TaskWatchdogEntry_t;

static TaskWatchdogEntry_t s_monitoredTasks[WATCHDOG_MAX_MONITORED_TASKS];

void SoftwareWatchdog_Init(void) {
    memset(s_monitoredTasks, 0, sizeof(s_monitoredTasks));
    for (int i = 0; i < TASK_ID_COUNT; ++i) {
        s_monitoredTasks[i].isActive = true;
        s_monitoredTasks[i].lastFeedTick = xTaskGetTickCount();
    }
}

void SoftwareWatchdog_Feed(MonitoredTaskID_t taskId) {
    if (taskId < WATCHDOG_MAX_MONITORED_TASKS) {
        s_monitoredTasks[taskId].lastFeedTick = xTaskGetTickCount();
    }
}

bool SoftwareWatchdog_CheckHealth(void) {
    uint32_t now = xTaskGetTickCount();
    uint32_t maxAllowedTicks = pdMS_TO_TICKS(WATCHDOG_TIMEOUT_MS);

    for (int i = 0; i < TASK_ID_COUNT; ++i) {
        if (s_monitoredTasks[i].isActive) {
            if ((now - s_monitoredTasks[i].lastFeedTick) > maxAllowedTicks) {
                /* Task hung or starved! */
                return false;
            }
        }
    }
    return true;
}

void vSoftwareWatchdogTask(void *pvParameters) {
    (void)pvParameters;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(50)); /* Check twice per 100ms window */

        if (!SoftwareWatchdog_CheckHealth()) {
            /* Trigger safe emergency descent and hardware reset */
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
            /* Cut motor power and surface */
            NVIC_SystemReset();
#endif
        }
    }
}
