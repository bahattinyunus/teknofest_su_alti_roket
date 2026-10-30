#ifndef SOFTWARE_WATCHDOG_H
#define SOFTWARE_WATCHDOG_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define WATCHDOG_MAX_MONITORED_TASKS 8
#define WATCHDOG_TIMEOUT_MS          100 /* 100ms refresh window */

typedef enum {
    TASK_ID_GATEKEEPER = 0,
    TASK_ID_NAVIGATION,
    TASK_ID_MISSION_MGR,
    TASK_ID_TELEMETRY,
    TASK_ID_SENSOR_IO,
    TASK_ID_COUNT
} MonitoredTaskID_t;

/**
 * @brief Initialize the Software Watchdog system.
 */
void SoftwareWatchdog_Init(void);

/**
 * @brief Pet / feed the watchdog from a monitored task.
 * @param taskId Enum ID of calling task
 */
void SoftwareWatchdog_Feed(MonitoredTaskID_t taskId);

/**
 * @brief Inspect if all registered tasks reported within their deadline.
 * @return true if all healthy, false if any task timed out.
 */
bool SoftwareWatchdog_CheckHealth(void);

/**
 * @brief FreeRTOS task executing periodic 100ms watchdog health checks.
 */
void vSoftwareWatchdogTask(void *pvParameters);

#ifdef __cplusplus
}
#endif

#endif /* SOFTWARE_WATCHDOG_H */
