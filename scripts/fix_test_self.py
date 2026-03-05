import re

files_to_fix = [
    'backend/tests/test_sprint_risk_model.py',
    'backend/tests/test_feature_extractor.py',
    'backend/tests/test_refactor_safety.py',
    'backend/tests/test_smell_detector.py'
]

for fpath in files_to_fix:
    with open(fpath, 'r') as f:
        content = f.read()
        
    # Replace (self, ...) with (...)
    content = re.sub(r'def (test_\w+)\(self,\s*', r'def \1(', content)
    # Replace (self) with ()
    content = re.sub(r'def (test_\w+)\(self\)', r'def \1()', content)
    
    with open(fpath, 'w') as f:
        f.write(content)

print("Self removed from test functions.")
