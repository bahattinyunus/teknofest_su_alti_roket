#include "fota_protocol.h"

#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
  #include "stm32f4xx_hal.h"
  extern UART_HandleTypeDef huart6;
#endif

typedef void (*pFunction)(void);

void FOTA_JumpToApplication(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    uint32_t appStack = *(__IO uint32_t*)FOTA_APP_START_ADDRESS;
    pFunction appEntry = (pFunction)(*(__IO uint32_t*)(FOTA_APP_START_ADDRESS + 4));

    /* 1. Disable all interrupts */
    __disable_irq();

    /* 2. De-init all RCC clocks and SysTick */
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL = 0;

    HAL_RCC_DeInit();

    /* 3. Shift Vector Table Offset Register (VTOR) to Application address */
    SCB->VTOR = FOTA_APP_START_ADDRESS;

    /* 4. Set main stack pointer (MSP) and jump to application entry */
    __set_MSP(appStack);
    appEntry();
#endif
}

void FOTA_Bootloader_Run(void) {
#if defined(STM32F407xx) && defined(USE_HAL_DRIVER)
    uint8_t syncByte = 0;

    /* Wait 2 seconds for ESP32-S3 synchronization byte */
    if (HAL_UART_Receive(&huart6, &syncByte, 1, FOTA_BOOTLOADER_TIMEOUT_MS) == HAL_OK && syncByte == FOTA_SYNC_BYTE) {
        /* Send ACK to ESP32-S3 */
        uint8_t ack = FOTA_ACK_BYTE;
        HAL_UART_Transmit(&huart6, &ack, 1, 100);

        HAL_FLASH_Unlock();

        uint32_t currentFlashAddr = FOTA_APP_START_ADDRESS;
        uint8_t chunkBuffer[FOTA_CHUNK_SIZE];

        while (1) {
            /* Receive 128-byte chunk */
            if (HAL_UART_Receive(&huart6, chunkBuffer, FOTA_CHUNK_SIZE, 5000) != HAL_OK) {
                break; /* Timeout or transfer complete */
            }

            /* Program chunk into STM32 Flash */
            for (int i = 0; i < FOTA_CHUNK_SIZE; i += 4) {
                uint32_t wordData = *(uint32_t*)&chunkBuffer[i];
                HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, currentFlashAddr + i, wordData);
            }
            currentFlashAddr += FOTA_CHUNK_SIZE;

            /* Send ACK for chunk */
            HAL_UART_Transmit(&huart6, &ack, 1, 100);
        }

        HAL_FLASH_Lock();
    }
#endif

    /* Jump to Application */
    FOTA_JumpToApplication();
}
