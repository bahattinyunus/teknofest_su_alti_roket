import time

class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.prev_error = 0
        self.integral = 0
        self.last_time = time.time()

    def update(self, current_value):
        now = time.time()
        dt = now - self.last_time
        if dt <= 0:
            dt = 0.001

        error = self.setpoint - current_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

        self.prev_error = error
        self.last_time = now

        return output

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
        self.integral = 0 # Reset integral on setpoint change to avoid windup
