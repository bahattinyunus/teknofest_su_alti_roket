#ifndef FOTA_PROTOCOL_H
#define FOTA_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FOTA_SYNC_BYTE             0x7F
#define FOTA_ACK_BYTE              0x06
#define FOTA_NACK_BYTE             0x15
#define FOTA_CHUNK_SIZE            128
#define FOTA_APP_START_ADDRESS     0x08010000UL /* Application Flash Sector */
#define FOTA_BOOTLOADER_TIMEOUT_MS 2000

typedef struct {
    uint8_t chunkIndex;
    uint8_t payload[FOTA_CHUNK_SIZE];
    uint16_t crc16;
} __attribute__((packed)) FOTA_ChunkPacket_t;

/**
 * @brief Initialize custom bootloader peripheral listeners on USART6.
 */
void FOTA_Bootloader_Init(void);

/**
 * @brief Run the bootloader loop: waits 2s for 0x7F sync byte from ESP32-S3.
 * If sync received, programs Flash chunks and jumps to application.
 * If timeout expires without sync, jumps directly to application.
 */
void FOTA_Bootloader_Run(void);

/**
 * @brief De-initializes peripherals, shifts VTOR, and jumps to application at 0x08010000.
 */
void FOTA_JumpToApplication(void);

#ifdef __cplusplus
}
#endif

#endif /* FOTA_PROTOCOL_H */
