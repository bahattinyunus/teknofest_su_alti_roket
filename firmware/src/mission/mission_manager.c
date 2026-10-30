#include "mission_manager.h"
#include "gatekeeper_task.h"
#include <stddef.h>

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  #include "FreeRTOS.h"
  #include "queue.h"
  #include "task.h"
#else
  typedef void* QueueHandle_t;
  #define pdTRUE 1
  #define pdFALSE 0
  #define pdMS_TO_TICKS(ms) (ms)
  #define portMAX_DELAY 0xFFFFFFFFUL
#endif

#define COMMAND_QUEUE_LEN 16

static QueueHandle_t commandQ = NULL;
static MissionState_t s_currentState = MISSION_STATE_STANDBY;

void Mission_Init(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    if (commandQ == NULL) {
        commandQ = xQueueCreate(COMMAND_QUEUE_LEN, sizeof(MissionCommand_t));
    }
#endif
    s_currentState = MISSION_STATE_STANDBY;
}

bool Mission_SendCommand(MissionCommandType_t type, float param) {
    MissionCommand_t cmd;
    cmd.type = type;
    cmd.parameter = param;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    if (!commandQ) return false;
    return (xQueueSend(commandQ, &cmd, pdMS_TO_TICKS(10)) == pdTRUE);
#else
    return true;
#endif
}

MissionState_t Mission_GetState(void) {
    return s_currentState;
}

void vMissionExecutionTask(void *pvParameters) {
    (void)pvParameters;

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    /* 90-second mandatory pre-run waiting & stabilization window per competition rules */
    s_currentState = MISSION_STATE_CALIBRATING_90S;
    vTaskDelay(pdMS_TO_TICKS(90000));

    s_currentState = MISSION_STATE_STANDBY;

    MissionCommand_t rxCmd;
    for (;;) {
        if (xQueueReceive(commandQ, &rxCmd, portMAX_DELAY) == pdTRUE) {
            switch (rxCmd.type) {
                case CMD_ARM:
                    s_currentState = MISSION_STATE_ARMED;
                    /* Arm main motor ESC with neutral throttle */
                    Gatekeeper_SendCommand(ACTUATOR_MAIN_MOTOR, PWM_NEUTRAL_MICROSECONDS);
                    break;

                case CMD_SET_DEPTH:
                    s_currentState = MISSION_STATE_DIVING;
                    /* In diving phase, pitch fins down slightly */
                    Gatekeeper_SendCommand(ACTUATOR_FIN_TOP, 1600);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_BOTTOM, 1400);
                    break;

                case CMD_GO_DISTANCE:
                    s_currentState = MISSION_STATE_CRUISE_50M;
                    /* Spin main BLDC motor forward */
                    Gatekeeper_SendCommand(ACTUATOR_MAIN_MOTOR, 1750);
                    break;

                case CMD_TURN_HEADING:
                    s_currentState = MISSION_STATE_TURN_180;
                    /* Deflect horizontal fins for 180 yaw turn */
                    Gatekeeper_SendCommand(ACTUATOR_FIN_LEFT, 1700);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_RIGHT, 1300);
                    break;

                case CMD_PITCH_UP:
                    s_currentState = MISSION_STATE_PITCH_SURFACE;
                    /* Deflect vertical fins for pitch-up surfacing maneuver */
                    Gatekeeper_SendCommand(ACTUATOR_FIN_TOP, 1350);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_BOTTOM, 1650);
                    break;

                case CMD_OPEN_HATCH:
                    Gatekeeper_SendCommand(ACTUATOR_HATCH_SERVO, 1900);
                    break;

                case CMD_FIRE_ROCKET:
                    s_currentState = MISSION_STATE_ROCKET_LAUNCH;
                    /* Fire relay / e-match */
                    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_SET);
                    vTaskDelay(pdMS_TO_TICKS(1000));
                    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_RESET);
                    break;

                case CMD_DISARM:
                case CMD_EMERGENCY_SURFACE:
                    s_currentState = (rxCmd.type == CMD_DISARM) ? MISSION_STATE_DISARMED : MISSION_STATE_EMERGENCY;
                    /* Neutralize all fins & cut motor */
                    Gatekeeper_SendCommand(ACTUATOR_MAIN_MOTOR, PWM_NEUTRAL_MICROSECONDS);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_TOP, PWM_NEUTRAL_MICROSECONDS);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_BOTTOM, PWM_NEUTRAL_MICROSECONDS);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_LEFT, PWM_NEUTRAL_MICROSECONDS);
                    Gatekeeper_SendCommand(ACTUATOR_FIN_RIGHT, PWM_NEUTRAL_MICROSECONDS);
                    break;

                default:
                    break;
            }
        }
    }
#endif
}
