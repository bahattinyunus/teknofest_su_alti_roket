class KalmanFilter1D:
    def __init__(self, process_variance, measurement_variance, estimated_error, initial_value):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_error = estimated_error
        self.value = initial_value
        self.kalman_gain = 0

    def update(self, measurement):
        # Prediction update
        self.estimated_error = self.estimated_error + self.process_variance

        # Measurement update
        self.kalman_gain = self.estimated_error / (self.estimated_error + self.measurement_variance)
        self.value = self.value + self.kalman_gain * (measurement - self.value)
        self.estimated_error = (1 - self.kalman_gain) * self.estimated_error

        return self.value

if __name__ == "__main__":
    # Example usage
    kf = KalmanFilter1D(0.01, 0.1, 1.0, 0)
    measurements = [1, 1.1, 0.9, 1.2, 1.0, 0.8]
    for m in measurements:
        print(f"Measured: {m}, Filtered: {kf.update(m)}")
