# Test file for infinite loop detection
# This should trigger control flow graph showing infinite loop

while True:
    print("This will run forever!")
    print("No way to exit this loop")
