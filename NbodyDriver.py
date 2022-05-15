from NbodyFunctions import *

# Printing menu
print("Select Menu Option:")
print("1: Simulate Solar System (Suggested Interval: 86400s)")
print("2: Simulate 2-Bodies (Suggested Interval: <5s)")
print("3: Simulate 3-Bodies")
print("4: Manually Enter Objects")
valid = False
selection = -1

# Selection
while not valid:
    # Ensuring an integer is passed
    try:
        selection = int(input())
    except ValueError:
        print("Please enter an integer!")

    if selection == 1:
        loadObjectsAPI()
    elif selection == 2:
        twoBodies()
    elif selection == 3:
        print("I run!")
        threeBodies()
    elif selection == 4:
        manuallyLoadBodies()
    else:
        continue
    runSimulation()
    valid = True
