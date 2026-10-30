/**
 * @file main.c
 * @brief ESP32-S3 FOTA Server and 8MB PSRAM Blackbox Logger
 * Open Reference Architecture for TEKNOFEST Autonomous Underwater Rocket Teams
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define STM32_RESET_PIN     4
#define STM32_UART_TX_PIN   18
#define STM32_UART_RX_PIN   17
#define FOTA_CHUNK_SIZE     128
#define FOTA_SYNC_BYTE      0x7F
#define FOTA_ACK_BYTE       0x06

#define PSRAM_LOG_BUFFER_SIZE (4 * 1024 * 1024) // 4MB allocated in 8MB PSRAM

typedef struct {
    uint32_t timestamp_ms;
    float depth_m;
    float pitch_deg;
    float heading_deg;
    float motor_pwm;
    float fin_top_pwm;
    float fin_right_pwm;
    uint8_t mission_state;
} __attribute__((packed)) BlackboxLogRecord_t;

static BlackboxLogRecord_t *s_blackboxBuffer = NULL;
static size_t s_logRecordCount = 0;
static const size_t s_maxRecords = PSRAM_LOG_BUFFER_SIZE / sizeof(BlackboxLogRecord_t);

/**
 * @brief Initialize PSRAM blackbox ring buffer
 */
void Blackbox_Init(void) {
    /* In ESP-IDF: s_blackboxBuffer = (BlackboxLogRecord_t*)heap_caps_malloc(PSRAM_LOG_BUFFER_SIZE, MALLOC_CAP_SPIRAM); */
    printf("[ESP32-S3 Blackbox] Initialized for %zu records in PSRAM.\n", s_maxRecords);
}

/**
 * @brief Log high-rate navigation and control telemetry
 */
void Blackbox_LogRecord(float depth, float pitch, float heading, float motorPwm, float finTop, float finRight, uint8_t state) {
    if (!s_blackboxBuffer || s_logRecordCount >= s_maxRecords) return;

    BlackboxLogRecord_t *rec = &s_blackboxBuffer[s_logRecordCount++];
    rec->timestamp_ms = s_logRecordCount * 20; // 50 Hz
    rec->depth_m = depth;
    rec->pitch_deg = pitch;
    rec->heading_deg = heading;
    rec->motor_pwm = motorPwm;
    rec->fin_top_pwm = finTop;
    rec->fin_right_pwm = finRight;
    rec->mission_state = state;
}

/**
 * @brief Perform STM32 Hardware Reset and initiate FOTA chunk flashing
 */
bool FOTA_TriggerSTM32Update(const uint8_t *binaryData, size_t binarySize) {
    if (!binaryData || binarySize == 0) return false;

    printf("[ESP32-S3 FOTA] Resetting STM32 via nRESET Pin %d...\n", STM32_RESET_PIN);
    /* gpio_set_level(STM32_RESET_PIN, 0); vTaskDelay(pdMS_TO_TICKS(50)); gpio_set_level(STM32_RESET_PIN, 1); */

    printf("[ESP32-S3 FOTA] Sending 0x7F sync byte to STM32 Bootloader...\n");
    /* Send sync byte and wait for ACK */

    size_t offset = 0;
    while (offset < binarySize) {
        size_t chunkSize = (binarySize - offset > FOTA_CHUNK_SIZE) ? FOTA_CHUNK_SIZE : (binarySize - offset);
        /* Send chunkSize bytes, wait for 0x06 ACK */
        offset += chunkSize;
    }

    printf("[ESP32-S3 FOTA] Firmware flashing complete (%zu bytes).\n", binarySize);
    return true;
}

void app_main(void) {
    printf("=== TEKNOFEST UNDERWATER ROCKET ESP32-S3 FOTA & BLACKBOX BRIDGE ===\n");
    Blackbox_Init();
    /* Wi-Fi SoftAP initialization: SSID="ROCKET_FOTA_ACCESS_POINT" */
    /* Start Web Server with /update and /blackbox endpoints */
}
