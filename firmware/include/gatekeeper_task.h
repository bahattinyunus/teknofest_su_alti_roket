#ifndef GATEKEEPER_TASK_H
#define GATEKEEPER_TASK_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Actuator Channels */
#define ACTUATOR_FIN_TOP      0
#define ACTUATOR_FIN_BOTTOM   1
#define ACTUATOR_FIN_LEFT     2
#define ACTUATOR_FIN_RIGHT    3
#define ACTUATOR_MAIN_MOTOR   4
#define ACTUATOR_HATCH_SERVO  5

/* PWM Boundaries in microseconds (1000 - 2000 us) */
#define PWM_MIN_MICROSECONDS  1000
#define PWM_NEUTRAL_MICROSECONDS 1500
#define PWM_MAX_MICROSECONDS  2000

typedef struct {
    uint8_t channel;
    uint16_t targetPosition; /* Microseconds (e.g., 1500 for neutral) */
} ServoCommand_t;

/**
 * @brief Initialize the Gatekeeper Queue and task.
 */
void Gatekeeper_Init(void);

/**
 * @brief Thread-safe actuator command dispatch.
 * @param channel Target actuator index
 * @param targetPosition PWM pulse in microseconds
 * @return true if queued successfully, false if queue is full
 */
bool Gatekeeper_SendCommand(uint8_t channel, uint16_t targetPosition);

/**
 * @brief FreeRTOS task function that owns the hardware UART interface.
 */
void vGatekeeperTask(void *pvParameters);

#ifdef __cplusplus
}
#endif

#endif /* GATEKEEPER_TASK_H */
