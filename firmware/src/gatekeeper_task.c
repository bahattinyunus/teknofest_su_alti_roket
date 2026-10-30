#include "gatekeeper_task.h"
#include <stddef.h>

/* FreeRTOS and HAL types stub/wrapper for portable build and target execution */
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  #include "FreeRTOS.h"
  #include "queue.h"
  #include "task.h"
  extern UART_HandleTypeDef huart1;
#else
  /* Simulation / unit-testing fallback definitions */
  typedef void* QueueHandle_t;
  typedef uint32_t TickType_t;
  #define pdTRUE 1
  #define pdFALSE 0
  #define pdMS_TO_TICKS(ms) (ms)
  #define portMAX_DELAY 0xFFFFFFFFUL
#endif

#define MAESTRO_QUEUE_LENGTH 16

static QueueHandle_t maestroCommandQ = NULL;

void Gatekeeper_Init(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    if (maestroCommandQ == NULL) {
        maestroCommandQ = xQueueCreate(MAESTRO_QUEUE_LENGTH, sizeof(ServoCommand_t));
    }
#endif
}

bool Gatekeeper_SendCommand(uint8_t channel, uint16_t targetPosition) {
    if (targetPosition < PWM_MIN_MICROSECONDS) targetPosition = PWM_MIN_MICROSECONDS;
    if (targetPosition > PWM_MAX_MICROSECONDS) targetPosition = PWM_MAX_MICROSECONDS;

    ServoCommand_t cmd;
    cmd.channel = channel;
    cmd.targetPosition = targetPosition;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    if (maestroCommandQ == NULL) return false;
    /* Send to queue non-blocking or with short 5ms timeout */
    return (xQueueSend(maestroCommandQ, &cmd, pdMS_TO_TICKS(5)) == pdTRUE);
#else
    return true;
#endif
}

void vGatekeeperTask(void *pvParameters) {
    (void)pvParameters;
    ServoCommand_t rxCmd;

    for (;;) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
        /* Wait up to 2ms for incoming actuator command to maintain 38400 baud synchronization */
        if (xQueueReceive(maestroCommandQ, &rxCmd, pdMS_TO_TICKS(2)) == pdTRUE) {
            /* Pololu Maestro Compact Protocol: 0x84, Channel, Target Low 7-bits, Target High 7-bits
             * Note: Maestro target is in quarter-microseconds (value * 4) */
            uint16_t quarterUs = rxCmd.targetPosition * 4;
            uint8_t packet[4];
            packet[0] = 0x84;
            packet[1] = rxCmd.channel;
            packet[2] = quarterUs & 0x7F;
            packet[3] = (quarterUs >> 7) & 0x7F;

            /* Transmit via UART DMA - non-blocking, atomic access owned exclusively by Gatekeeper */
            HAL_UART_Transmit_DMA(&huart1, packet, sizeof(packet));
        }
#endif
    }
}
