#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
from pynput import keyboard

# List of body objects
bodies = []
# Maximum x/y position of an object
max_pos = 0


class Body:
    # Gravitational constant
    G = 6.67430e-11

    # Body constructor
    def __init__(self, position=np.zeros(2, dtype=float), velocity=np.zeros(2, dtype=float),
                 mass=0.0, name=""):
        self.position = position
        self.velocity = velocity
        self.acceleration = np.zeros(2, dtype=float)
        self.mass = mass
        self.name = name

    # 'Objects' argument is a list of Bodies in simulation
    def calculateAcceleration(self, objects):
        # Resetting acceleration vector to 0's
        for i in range(self.acceleration.size):
            self.acceleration[i] = 0
        # Iterating through all the bodies - skipping over self
        for i in range(len(objects)):
            if self == objects[i]:
                continue

            # Calculating r vector
            x = objects[i].position[0] - self.position[0]
            y = objects[i].position[1] - self.position[1]

            # Calculating magnitude of r vector
            r = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

            # Normalizing components
            x /= r
            y /= r

            # Calculating acceleration magnitude
            accel = self.G * objects[i].mass / r ** 2

            # Assignment
            self.acceleration[0] += x * accel
            self.acceleration[1] += y * accel

    # Updates position followed by velocity
    def updatePosition(self, step_size):
        for i in range(self.velocity.size):
            self.position[i] += step_size * self.velocity[i]
        for i in range(self.velocity.size):
            self.velocity[i] += step_size * self.acceleration[i]


# Draws objects to plot upon call. Decided to make a global scaling value (only increases as objects move outward).
# Makes for a more visually appealing result
def display():
    global max_pos
    # Finding the extreme coordinate so everything is within view (will scale)
    for i in range(len(bodies)):
        for a in range(bodies[i].position.size):
            if abs(bodies[i].position[a]) > max_pos:
                max_pos = abs(bodies[i].position[a])
    # Setting the bounds to 1.5 * the maximum coordinate
    plt.xlim([-max_pos * 1.5, max_pos * 1.5])
    plt.ylim([-max_pos * 1.5, max_pos * 1.5])
    # Iterating through the bodies and plotting each one & adding text
    for i in range(len(bodies)):
        plt.scatter(bodies[i].position[0], bodies[i].position[1])
        plt.text(bodies[i].position[0], bodies[i].position[1], bodies[i].name, fontsize='xx-small')
    # Pausing for a short increment & clearing the figure
    plt.pause(.0001)
    plt.clf()


# Utilizing The Solar System OpenData API (found online)
def loadObjectsAPI():
    # Only including planets (and stars) with a mass of magnitude 10^22 or greater (the 8 planets & the sun)
    data = requests.get("https://api.le-systeme-solaire.net/rest/bodies/", params="filter[]=massExponent,gt,22")
    solarBodies = data.json()["bodies"]
    for i in solarBodies:
        # Excluding moons
        if i["bodyType"] != "Moon":
            name = i["englishName"]

            # Semi-major axis given in km - converted to meters
            radius = [i["semimajorAxis"] * 1000, 0]

            # Sidereal orbit gives orbital period in Earth days - converted to seconds & multiplied by 2pi * radius
            # in meters (gives tangential velocity)
            if i["sideralOrbit"] > 0:
                angular_velocity = (radius[0] * 2 * math.pi) / (i["sideralOrbit"] * 86400)
            else:
                # Prevents divide by 0
                angular_velocity = 0

            # MassValue * 10^massExponent
            mass = i["mass"]["massValue"] * math.pow(10, i["mass"]["massExponent"])

            # Added to bodies
            bodies.append(Body(np.array(radius, dtype=float), np.array([0, angular_velocity], dtype=float), mass, name))


# Chose starting condition with interesting behavior
def twoBodies():
    bodies.append(Body(np.zeros(2, dtype=float), np.zeros(2, dtype=float), 1e11, "Object 1"))
    bodies.append(Body(np.array([50, 0], dtype=float), np.array([0, .25], dtype=float), 1e7, "Object 2"))


# Chose starting condition with interesting behavior
def threeBodies():
    bodies.append(Body(np.array([1, -0.25]), np.zeros(2, dtype=float), 1e6, "Object 1"))
    bodies.append(Body(np.array([-1, -0.25]), np.zeros(2, dtype=float), 1e6, "Object 2"))
    bodies.append(Body(np.array([0, .75]), np.zeros(2, dtype=float), 1e6, "Object 3"))


# Manually has user input values for objects - loads into bodies
def manuallyLoadBodies():
    usrInput = ''
    while usrInput.lower() != 'n':
        try:
            x = float(input("Enter the starting x coordinate: "))
            y = float(input("Enter the starting y coordinate: "))
            vx = float(input("Enter the starting x component of velocity: "))
            vy = float(input("Enter the starting y component of velocity: "))
            mass = float(input("Enter the mass: "))
            name = input("Enter the name: ")
            bodies.append(Body(np.array([x, y], dtype=float), np.array([vx, vy]), mass, name))
        except ValueError:
            print("Enter a valid number!")
        usrInput = input("Continue? [y/n]: ")


# Function for keyboard listener (listens for escape key)
def on_press(key):
    if key == keyboard.Key.esc:
        return False


# Prompts for stepSize - approximates an integral by choosing the width of Riemann Sum
def runSimulation():
    print("Click esc to stop the simulation")
    stepSize = input("Enter step size (seconds): ")
    # Opening thread for keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while listener.running:
        # First calculate all object's accelerations
        for body in bodies:
            body.calculateAcceleration(bodies)
        # Then update their positions
        for body in bodies:
            body.updatePosition(float(stepSize))
        # Display result
        display()
    print("Simulation Ended")
