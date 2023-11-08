import numpy as np


class TrackingData:  # structure of data output for tracking process
    def __init__(self, coords, time):
        self.coords = coords
        self.time = time

    def get_speed(self, prev_data):  # return the speed between this data and the one in parameter
        if type(prev_data) != type(self):
            print("ERROR: Must use TrackingData type to calculate speed!")
            return None
        (r1, theta1, phi1) = self.coords
        (r2, theta2, phi2) = prev_data.coords
        d = np.sqrt(r1*r1+r2*r2-2*r1*r2*(np.sin(theta1)*np.sin(theta2)*np.cos(phi1-phi2)+np.cos(theta1)*np.cos(theta2)))
        dt = (self.time - prev_data.time).total_seconds()
        return d/dt

    def get_color(self, prev_data):  # return a color based on the speed of the point in a gradient from yellow to red
        if type(prev_data) != type(self):
            print("ERROR: Must use TrackingData type to calculate color!")
            return None
        speed = self.get_speed(prev_data)
        alpha = 1/max(1, (speed*0.1))
        return 1, 1 * alpha, 0

    def get_cartesian(self):  # return the coordinates in cartesian coordinates (x, y, z)
        (r, theta, phi) = self.coords
        return r*np.sin(phi)*np.cos(theta), r*np.sin(phi)*np.sin(theta), r*np.cos(phi)

    def get_distance(self, p):  # return the distance in centimetres between this point and the one in parameter
        r, theta1, phi1 = self.coords
        _, theta2, phi2 = p.coords
        return r * np.arccos(np.sin(phi1)*np.sin(phi2) + np.cos(phi1)*np.cos(phi2)*np.cos(theta2-theta1))
