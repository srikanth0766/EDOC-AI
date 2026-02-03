# Test file for loop variable not updated
# This should trigger control flow graph showing variable never changes

i = 0
while i < 10:
    print("i is still", i)
    print("Forgot to increment i!")
    # Missing: i += 1
