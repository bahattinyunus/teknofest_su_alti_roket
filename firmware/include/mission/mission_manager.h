#ifndef MISSION_MANAGER_H
#define MISSION_MANAGER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CMD_NONE = 0,
    CMD_ARM,
    CMD_DISARM,
    CMD_SET_DEPTH,     /* param: target depth in meters (e.g. 1.5) */
    CMD_GO_DISTANCE,   /* param: distance in meters (e.g. 50.0) */
    CMD_TURN_HEADING,  /* param: relative or absolute heading degrees (e.g. 180.0) */
    CMD_PITCH_UP,      /* param: pitch target in degrees (e.g. 45.0) */
    CMD_OPEN_HATCH,
    CMD_FIRE_ROCKET,
    CMD_EMERGENCY_SURFACE
} MissionCommandType_t;

typedef struct {
    MissionCommandType_t type;
    float parameter;
} MissionCommand_t;

typedef enum {
    MISSION_STATE_STANDBY = 0,
    MISSION_STATE_CALIBRATING_90S,
    MISSION_STATE_ARMED,
    MISSION_STATE_DIVING,
    MISSION_STATE_CRUISE_50M,
    MISSION_STATE_TURN_180,
    MISSION_STATE_RETURN_CRUISE,
    MISSION_STATE_PITCH_SURFACE,
    MISSION_STATE_ROCKET_LAUNCH,
    MISSION_STATE_DISARMED,
    MISSION_STATE_EMERGENCY
} MissionState_t;

/**
 * @brief Initialize the mission manager and event queue.
 */
void Mission_Init(void);

/**
 * @brief Queue an autonomous or Wi-Fi tele-command.
 */
bool Mission_SendCommand(MissionCommandType_t cmd, float param);

/**
 * @brief Get current mission state.
 */
MissionState_t Mission_GetState(void);

/**
 * @brief FreeRTOS task handling autonomous mission execution.
 */
void vMissionExecutionTask(void *pvParameters);

#ifdef __cplusplus
}
#endif

#endif /* MISSION_MANAGER_H */
