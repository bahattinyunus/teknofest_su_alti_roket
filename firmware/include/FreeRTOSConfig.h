#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif

/* STM32F407VG FreeRTOS Configuration - ITU Sungur Autonomous Underwater Rocket */

#define configUSE_PREEMPTION                     1
#define configUSE_IDLE_HOOK                      0
#define configUSE_TICK_HOOK                      0
#define configCPU_CLOCK_HZ                       (168000000UL)
#define configTICK_RATE_HZ                       ((TickType_t)1000)
#define configMAX_PRIORITIES                     (8)
#define configMINIMAL_STACK_SIZE                 ((uint16_t)128)
#define configTOTAL_HEAP_SIZE                    ((size_t)(64 * 1024))
#define configMAX_TASK_NAME_LEN                  (16)
#define configUSE_16_BIT_TICKS                   0
#define configIDLE_SHOULD_YIELD                  1
#define configUSE_MUTEXES                        1
#define configUSE_RECURSIVE_MUTEXES              1
#define configUSE_COUNTING_SEMAPHORES            1
#define configQUEUE_REGISTRY_SIZE                8
#define configUSE_QUEUE_SETS                     1

/* Memory allocation */
#define configSUPPORT_STATIC_ALLOCATION          1
#define configSUPPORT_DYNAMIC_ALLOCATION         1

/* Hook functions */
#define configCHECK_FOR_STACK_OVERFLOW           2
#define configUSE_MALLOC_FAILED_HOOK             1

/* Cortex-M specific definitions */
#ifdef __NVIC_PRIO_BITS
 #define configPRIO_BITS                         __NVIC_PRIO_BITS
#else
 #define configPRIO_BITS                         4
#endif

/* The lowest interrupt priority that can be used in a call to a "set priority" function. */
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY         15

/* The highest interrupt priority that can be used by any interrupt service
routine that makes calls to interrupt safe FreeRTOS API functions.
CRITICAL: Interrupts calling FreeRTOS API must have numeric priority >= 6! */
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY    6

#define configKERNEL_INTERRUPT_PRIORITY         (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))

/* Software Watchdog & Task Notifications */
#define configUSE_TASK_NOTIFICATIONS             1

#ifdef __cplusplus
}
#endif

#endif /* FREERTOS_CONFIG_H */
