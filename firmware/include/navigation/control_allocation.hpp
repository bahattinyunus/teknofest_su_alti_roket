#ifndef NAVIGATION_CONTROL_ALLOCATION_HPP
#define NAVIGATION_CONTROL_ALLOCATION_HPP

#include <array>
#include <cmath>
#include <algorithm>
#include <cstdint>

namespace Navigation {

enum class FinConfiguration {
    CRUCIFORM, // Plus (+) config: Fin 1 Top, Fin 2 Bottom, Fin 3 Left, Fin 4 Right
    X_RUDDER   // X config: Fin 1 (Top-Left), Fin 2 (Top-Right), Fin 3 (Bottom-Left), Fin 4 (Bottom-Right)
};

struct FinAngles {
    float fin1_deg;
    float fin2_deg;
    float fin3_deg;
    float fin4_deg;
};

struct FinPwmOutputs {
    uint16_t pwm1_us;
    uint16_t pwm2_us;
    uint16_t pwm3_us;
    uint16_t pwm4_us;
};

class ControlAllocator {
public:
    FinConfiguration config;
    float maxFinAngleDeg;
    float maxSlewRateDegPerSec;
    std::array<bool, 4> finActive{true, true, true, true};
    std::array<float, 4> currentAnglesDeg{0.0f, 0.0f, 0.0f, 0.0f};

    ControlAllocator(FinConfiguration cfg = FinConfiguration::X_RUDDER,
                     float maxAngle = 25.0f,
                     float maxSlewRate = 120.0f)
        : config(cfg), maxFinAngleDeg(maxAngle), maxSlewRateDegPerSec(maxSlewRate) {}

    /**
     * @brief Allocate virtual torque commands (Pitch, Yaw, Roll) into 4 physical fin deflection angles.
     * @param tau_pitch Virtual pitch torque command [-1.0, 1.0]
     * @param tau_yaw   Virtual yaw torque command [-1.0, 1.0]
     * @param tau_roll  Virtual roll torque command [-1.0, 1.0]
     * @param dt        Time delta in seconds
     * @return FinAngles Deflection angles in degrees
     */
    FinAngles allocate(float tau_pitch, float tau_yaw, float tau_roll, float dt) {
        if (dt <= 0.0f) dt = 0.02f;

        tau_pitch = std::clamp(tau_pitch, -1.0f, 1.0f);
        tau_yaw = std::clamp(tau_yaw, -1.0f, 1.0f);
        tau_roll = std::clamp(tau_roll, -1.0f, 1.0f);

        std::array<float, 4> targetAngles{0.0f, 0.0f, 0.0f, 0.0f};

        if (config == FinConfiguration::CRUCIFORM) {
            // Cruciform (+): Decoupled elevator and rudder
            // Fin 1: Top Rudder (Yaw)
            // Fin 2: Bottom Rudder (Yaw)
            // Fin 3: Left Elevator (Pitch + Roll)
            // Fin 4: Right Elevator (Pitch - Roll)
            targetAngles[0] = tau_yaw * maxFinAngleDeg;
            targetAngles[1] = tau_yaw * maxFinAngleDeg;
            targetAngles[2] = (tau_pitch + tau_roll) * maxFinAngleDeg;
            targetAngles[3] = (tau_pitch - tau_roll) * maxFinAngleDeg;
        } else {
            // X-Rudder (X): Fully coupled allocation matrix
            // [delta1; delta2; delta3; delta4] = (1 / sqrt(2)) * [ 1, -1,  1;
            //                                                      1,  1, -1;
            //                                                     -1, -1, -1;
            //                                                     -1,  1,  1 ] * [tau_p; tau_y; tau_r]
            constexpr float INV_SQRT2 = 0.70710678f;
            float p = tau_pitch * maxFinAngleDeg;
            float y = tau_yaw * maxFinAngleDeg;
            float r = tau_roll * maxFinAngleDeg;

            targetAngles[0] = INV_SQRT2 * ( p - y + r);
            targetAngles[1] = INV_SQRT2 * ( p + y - r);
            targetAngles[2] = INV_SQRT2 * (-p - y - r);
            targetAngles[3] = INV_SQRT2 * (-p + y + r);
        }

        // Apply Fault-Tolerance (if a fin is jammed, zero its command or isolate)
        for (size_t i = 0; i < 4; ++i) {
            if (!finActive[i]) {
                targetAngles[i] = 0.0f;
            }
        }

        // Rate limiter and hard angle clamp
        float maxStep = maxSlewRateDegPerSec * dt;
        for (size_t i = 0; i < 4; ++i) {
            float delta = targetAngles[i] - currentAnglesDeg[i];
            delta = std::clamp(delta, -maxStep, maxStep);
            currentAnglesDeg[i] += delta;
            currentAnglesDeg[i] = std::clamp(currentAnglesDeg[i], -maxFinAngleDeg, maxFinAngleDeg);
        }

        return {currentAnglesDeg[0], currentAnglesDeg[1], currentAnglesDeg[2], currentAnglesDeg[3]};
    }

    /**
     * @brief Convert fin deflection angles (deg) to servo PWM in microseconds (1000 - 2000 us)
     */
    FinPwmOutputs toPwm(const FinAngles& angles) const {
        auto angleToUs = [this](float angleDeg) -> uint16_t {
            // 0 deg -> 1500 us, +maxFinAngle -> 2000 us, -maxFinAngle -> 1000 us
            float normalized = angleDeg / maxFinAngleDeg;
            normalized = std::clamp(normalized, -1.0f, 1.0f);
            float pwm = 1500.0f + normalized * 500.0f;
            return static_cast<uint16_t>(std::round(pwm));
        };

        return {
            angleToUs(angles.fin1_deg),
            angleToUs(angles.fin2_deg),
            angleToUs(angles.fin3_deg),
            angleToUs(angles.fin4_deg)
        };
    }

    void setFinHealth(size_t finIndex, bool isHealthy) {
        if (finIndex < 4) {
            finActive[finIndex] = isHealthy;
        }
    }
};

} // namespace Navigation

#endif /* NAVIGATION_CONTROL_ALLOCATION_HPP */
