#ifndef NAVIGATION_PID_HPP
#define NAVIGATION_PID_HPP

#include <algorithm>

namespace Navigation {

class PID {
public:
    float kp;
    float ki;
    float kd;
    float setpoint;
    float minOutput;
    float maxOutput;

    float integral;
    float prevError;
    float prevMeasurement;
    bool derivativeOnMeasurement;

    PID(float p, float i, float d, float minOut = -500.0f, float maxOut = 500.0f, bool dOnMeas = true)
        : kp(p), ki(i), kd(d), setpoint(0.0f), minOutput(minOut), maxOutput(maxOut),
          integral(0.0f), prevError(0.0f), prevMeasurement(0.0f), derivativeOnMeasurement(dOnMeas) {}

    void reset() {
        integral = 0.0f;
        prevError = 0.0f;
        prevMeasurement = 0.0f;
    }

    void setSetpoint(float sp) {
        setpoint = sp;
    }

    float update(float measurement, float dt) {
        if (dt <= 0.0f) dt = 0.01f;

        float error = setpoint - measurement;

        // Proportional term
        float pTerm = kp * error;

        // Integral term with anti-windup clamp
        integral += ki * error * dt;
        integral = std::clamp(integral, minOutput, maxOutput);

        // Derivative term (on measurement to avoid derivative kick on setpoint change)
        float dTerm = 0.0f;
        if (derivativeOnMeasurement) {
            dTerm = -kd * (measurement - prevMeasurement) / dt;
        } else {
            dTerm = kd * (error - prevError) / dt;
        }

        prevError = error;
        prevMeasurement = measurement;

        float output = pTerm + integral + dTerm;
        return std::clamp(output, minOutput, maxOutput);
    }
};

} // namespace Navigation

#endif /* NAVIGATION_PID_HPP */
