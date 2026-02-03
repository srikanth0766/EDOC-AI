# Test file for unreachable code
# This should trigger control flow graph showing code after return

def calculate():
    x = 10
    y = 20
    return x + y
    print("This line will never execute")
    z = 30
    return z
