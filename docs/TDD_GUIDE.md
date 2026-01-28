# ONI TDD Guide & Best Practices

> **"Code without tests is legacy code."**

This guide outlines the testing standards for the ONI project. We use `pytest` as our testing framework.

## 1. Testing Philosophy
- **Write tests BEFORE code** when possible (TDD).
- **Unit Tests**: Test individual components in isolation. Mock verification dependent services (`NativeService`, `HumanMouse`).
- **Integration Tests**: Test the interaction between components (e.g., Agent -> Worker -> Guardian).

## 2. Directory Structure
```
tests/
├── conftest.py          # Shared fixtures (mocks, event loops)
├── unit/                # Fast, isolated tests
│   ├── test_creative_engine.py
│   └── test_action_guardian.py
└── integration/         # Slower, connected tests
    └── test_hybrid_flow.py
```

## 3. Mocking Strategy
Since ONI interacts heavily with the OS (Win32 API), proper mocking is crucial to run tests on any environment (including CI/CD).

### Mocking `NativeService`
```python
@pytest.fixture
def mock_native_service(mocker):
    service = mocker.MagicMock()
    service.find_window.return_value = WindowInfo(...)
    return service
```

### Mocking `ValidationCoordinate`
Always use `ValidatedCoordinate` in your tests when invoking `HumanMouse` methods to abide by the Axioms.

## 4. Running Tests
```bash
# Run all tests
pytest

# Run specific file
pytest tests/unit/test_creative_engine.py

# Run with output
pytest -v -s
```

## 5. Axiom Confirmation
Ensure your tests verify that `AxiomViolationError` is raised strictly when safety rules are broken.
