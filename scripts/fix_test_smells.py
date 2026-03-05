import re

files_to_fix = [
    'backend/tests/test_sprint_risk_model.py',
    'backend/tests/test_feature_extractor.py',
    'backend/tests/test_refactor_safety.py',
    'backend/tests/test_smell_detector.py'
]

for fpath in files_to_fix:
    with open(fpath, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    in_class = False
    
    for line in lines:
        if line.startswith('class Test'):
            continue  # Skip the class definition line
            
        if line.startswith('    '):
            new_lines.append(line[4:])
        elif line.strip() == '':
            new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(fpath, 'w') as f:
        f.writelines(new_lines)

print("Files rewritten successfully.")
