# Test file with valid code (no issues)
# This should NOT trigger any control flow warnings

i = 0
while i < 10:
    print("i is", i)
    i += 1  # Variable is properly updated

print("Loop completed successfully")
