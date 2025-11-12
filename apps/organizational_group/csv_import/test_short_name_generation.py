"""
Test script for short name generation logic.

Run with: python apps/organizational_group/csv_import/test_short_name_generation.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Mock Campus class for testing
class MockCampus:
    def __init__(self, code):
        self.code = code

def test_generate_short_name():
    """Test the short name generation logic."""
    from apps.organizational_group.csv_import.group_handler import GroupHandler
    
    handler = GroupHandler()
    
    test_cases = [
        # (name, campus_code, expected_pattern)
        ("Ambiente Construído", "COL", "AC-COL"),
        ("Análise e Desenvolvimento em Sistemas Mecânicos", "VIT", "ADSM-VIT"),
        ("Biodiversidade Urbana", "VIT", "BU-VIT"),
        ("A", "VIT", "A-VIT"),  # Single letter
        ("", None, "non-informed"),  # Empty name
        ("   ", None, "non-informed"),  # Whitespace only
        ("Grupo de Estudos", "SER", "GE-SER"),  # With ignored words
        ("The Study of Materials", "VIT", "SM-VIT"),  # English ignored words
    ]
    
    print("Testing Short Name Generation")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, campus_code, expected in test_cases:
        campus = MockCampus(campus_code) if campus_code else None
        result = handler._generate_short_name(name, campus)
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status}: '{name[:40]:<40}' → '{result}' (expected: '{expected}')")
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = test_generate_short_name()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
