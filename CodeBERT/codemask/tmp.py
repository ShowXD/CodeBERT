import re

# assume the list is stored in a variable named 'lst'
lst = ['File "/app", line 15', 'File "/app", line 20', 'File "/app", line 25']

# find the line number containing the digit 15
result = next(filter(lambda s: '15' in s, lst), None)

# print the result
if result is not None:
    pattern = r"File \"/[^\"]+\", line (\d+)"
    match = re.search(pattern, result)
    if match:
        line_number = match.group(1)
        print("Line number:", line_number)
    else:
        print("No match")
else:
    print("No element found")
