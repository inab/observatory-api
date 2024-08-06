from app.models.instance import Documentation, Instance
from app.services.r_indicators import compR3_1
 
# Define valid and invalid contribution policy types for testing
VALID_CONTRIBUTION_POLICIES = [
    'contribution policy',
    'contributing guidelines',
    'contribution guidelines',
    'contribution rules',
    'contributing rules',
    'contributing policy',
    'contribution procedures'
]

INVALID_CONTRIBUTION_POLICIES = [
    'usage guide',
    'user manual',
    'technical document',
    'reference guide'
]

# Test cases for compR3_1 function
def test_compR3_1_with_valid_policy_types():
    for policy in VALID_CONTRIBUTION_POLICIES:
        instance = Instance(documentation=[Documentation(type=policy)])
        result, logs = compR3_1(instance)
        assert result == True

def test_compR3_1_with_invalid_policy_types():
    for policy in INVALID_CONTRIBUTION_POLICIES:
        instance = Instance(documentation=[Documentation(type=policy)])
        result, logs = compR3_1(instance)
        assert result ==  False

def test_compR3_1_with_mixed_policy_types():
    mixed_documentation = [
        Documentation(type='contribution policy'),
        Documentation(type='technical document'),
        Documentation(type='contributing guidelines')
    ]
    instance = Instance(documentation=mixed_documentation)
    result, logs = compR3_1(instance)
    assert result ==  True

def test_compR3_1_with_empty_documentation():
    instance = Instance(documentation=[])
    result, logs = compR3_1(instance)
    assert result ==  False


def test_compR3_1_with_none_documentation():
    instance = Instance()
    result, logs = compR3_1(instance)
    assert result ==  False


def test_compR3_1_with_case_insensitive_check():
    case_insensitive_policies = [
        'CONTRIBUTION POLICY',
        'Contributing Guidelines',
        'contribution RULES'
    ]
    for policy in case_insensitive_policies:
        instance = Instance(documentation=[Documentation(type=policy)])
        result, logs = compR3_1(instance)
        assert result ==  True