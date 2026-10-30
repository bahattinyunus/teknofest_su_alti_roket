#ifndef NAVIGATION_ESKF_HPP
#define NAVIGATION_ESKF_HPP

#include <cstddef>
#include <array>
#include <cmath>

#if defined(ARM_MATH_CM4)
  #include "arm_math.h"
#endif

namespace Navigation {

/**
 * @brief Static Compile-Time Fixed-Size Matrix for Zero-Allocation ESKF
 * Eliminates heap allocation, avoids memory fragmentation, and integrates with CMSIS-DSP.
 */
template <size_t Rows, size_t Cols>
class Matrix {
public:
    std::array<float, Rows * Cols> data{};

    Matrix() { data.fill(0.0f); }

    float& operator()(size_t r, size_t c) { return data[r * Cols + c]; }
    const float& operator()(size_t r, size_t c) const { return data[r * Cols + c]; }

    static Matrix Identity() {
        Matrix result;
        size_t minDim = (Rows < Cols) ? Rows : Cols;
        for (size_t i = 0; i < minDim; ++i) {
            result(i, i) = 1.0f;
        }
        return result;
    }

    Matrix<Cols, Rows> transpose() const {
        Matrix<Cols, Rows> result;
        for (size_t r = 0; r < Rows; ++r) {
            for (size_t c = 0; c < Cols; ++c) {
                result(c, r) = (*this)(r, c);
            }
        }
        return result;
    }

    template <size_t OtherCols>
    Matrix<Rows, OtherCols> operator*(const Matrix<Cols, OtherCols>& other) const {
        Matrix<Rows, OtherCols> result;
#if defined(ARM_MATH_CM4)
        arm_matrix_instance_f32 A, B, C;
        arm_mat_init_f32(&A, Rows, Cols, const_cast<float*>(data.data()));
        arm_mat_init_f32(&B, Cols, OtherCols, const_cast<float*>(other.data.data()));
        arm_mat_init_f32(&C, Rows, OtherCols, result.data.data());
        arm_mat_mult_f32(&A, &B, &C);
#else
        for (size_t i = 0; i < Rows; ++i) {
            for (size_t j = 0; j < OtherCols; ++j) {
                float sum = 0.0f;
                for (size_t k = 0; k < Cols; ++k) {
                    sum += (*this)(i, k) * other(k, j);
                }
                result(i, j) = sum;
            }
        }
#endif
        return result;
    }

    Matrix operator+(const Matrix& other) const {
        Matrix result;
        for (size_t i = 0; i < Rows * Cols; ++i) {
            result.data[i] = data[i] + other.data[i];
        }
        return result;
    }

    Matrix operator-(const Matrix& other) const {
        Matrix result;
        for (size_t i = 0; i < Rows * Cols; ++i) {
            result.data[i] = data[i] - other.data[i];
        }
        return result;
    }
};

/**
 * @brief Error State Kalman Filter (ESKF) for Underwater Navigation
 * State Vector (6 states): [Position_Z, Velocity_Z, Pitch, Roll, Yaw, DepthBias]
 */
class UnderwaterESKF {
public:
    static constexpr size_t STATE_DIM = 6;
    static constexpr size_t MEAS_DIM = 2; /* Depth (Pressure) + Pitch (IMU) */

    Matrix<STATE_DIM, 1> x;          // Nominal state estimate
    Matrix<STATE_DIM, STATE_DIM> P;  // Error covariance
    Matrix<STATE_DIM, STATE_DIM> Q;  // Process noise covariance
    Matrix<MEAS_DIM, MEAS_DIM> R;    // Measurement noise covariance

    UnderwaterESKF() {
        x = Matrix<STATE_DIM, 1>();
        P = Matrix<STATE_DIM, STATE_DIM>::Identity() * 0.1f;
        Q = Matrix<STATE_DIM, STATE_DIM>::Identity() * 0.01f;
        R = Matrix<MEAS_DIM, MEAS_DIM>::Identity() * 0.05f;
    }

    /**
     * @brief Prediction step using IMU vertical acceleration and gyro rates
     */
    void predict(float accel_z, float gyro_pitch, float dt) {
        if (dt <= 0.0f) dt = 0.01f;

        // Kinematic integration
        float vz = x(1, 0);
        x(0, 0) += vz * dt + 0.5f * accel_z * dt * dt; // Depth (Z)
        x(1, 0) += accel_z * dt;                        // Vertical velocity
        x(2, 0) += gyro_pitch * dt;                    // Pitch angle

        // State transition Jacobian F
        Matrix<STATE_DIM, STATE_DIM> F = Matrix<STATE_DIM, STATE_DIM>::Identity();
        F(0, 1) = dt;

        // Covariance propagation: P = F * P * F^T + Q
        P = F * P * F.transpose() + Q;
    }

    /**
     * @brief Measurement update fusing MS5837 Depth & BNO055 Pitch
     */
    void update(float measured_depth, float measured_pitch) {
        // Measurement model H
        Matrix<MEAS_DIM, STATE_DIM> H;
        H(0, 0) = 1.0f; // Depth
        H(1, 2) = 1.0f; // Pitch

        // Innovation residual: y = z - Hx
        Matrix<MEAS_DIM, 1> z;
        z(0, 0) = measured_depth;
        z(1, 0) = measured_pitch;

        Matrix<MEAS_DIM, 1> y = z - (H * x);

        // Innovation covariance: S = H * P * H^T + R
        Matrix<MEAS_DIM, MEAS_DIM> S = H * P * H.transpose() + R;

        // 2x2 matrix inversion for S
        float det = S(0, 0) * S(1, 1) - S(0, 1) * S(1, 0);
        if (std::abs(det) < 1e-6f) return;

        Matrix<MEAS_DIM, MEAS_DIM> S_inv;
        S_inv(0, 0) = S(1, 1) / det;
        S_inv(0, 1) = -S(0, 1) / det;
        S_inv(1, 0) = -S(1, 0) / det;
        S_inv(1, 1) = S(0, 0) / det;

        // Kalman Gain: K = P * H^T * S^-1
        Matrix<STATE_DIM, MEAS_DIM> K = P * H.transpose() * S_inv;

        // State update
        x = x + (K * y);

        // Covariance update: P = (I - K * H) * P
        Matrix<STATE_DIM, STATE_DIM> I = Matrix<STATE_DIM, STATE_DIM>::Identity();
        P = (I - (K * H)) * P;
    }

    float getEstimatedDepth() const { return x(0, 0); }
    float getEstimatedVelocityZ() const { return x(1, 0); }
    float getEstimatedPitch() const { return x(2, 0); }
};

} // namespace Navigation

#endif /* NAVIGATION_ESKF_HPP */
