# PlanFlan - Test Optimization Guide

This guide documents the comprehensive test optimization strategies implemented for the PlanFlan application.

## 🎯 Test Optimization Overview

### Current Test Suite Statistics
- **Total Tests**: 185+ tests
- **Parameterized Tests**: 10 comprehensive tests (replacing ~30 individual tests)
- **Test Categories**: smoke, regression, integration, performance, e2e, api, database
- **Coverage**: Excellent coverage across all major components
- **Execution Time**: Significantly optimized with parallelization and selective execution

## 🚀 Test Execution Strategies

### Quick Development Workflow

```bash
# Run smoke tests (fast verification)
make test-smoke

# Run tests without slow ones
make test-without-slow

# Run critical tests only
make test-critical

# Run parallel tests (fastest for development)
make test-parallel-quick
```

### CI/CD Pipeline Workflow

```bash
# Run full test suite with coverage
make test-ci

# Run regression tests
make test-regression

# Run end-to-end tests
make test-e2e

# Run parallel tests with coverage
make test-parallel
```

### Selective Test Execution

```bash
# Run only authentication tests
make test-auth

# Run only form validation tests
make test-forms

# Run only main route tests
make test-main

# Run only unitary tests
make test-unitary
```

## 📊 Test Categories

### 1. Smoke Tests (`@pytest.mark.smoke`)
- **Purpose**: Quick verification that core functionality works
- **Execution Time**: < 1 minute
- **Use Case**: Development, pre-commit checks
- **Example**: Route status tests, basic form validation

```bash
make test-smoke
```

### 2. Regression Tests (`@pytest.mark.regression`)
- **Purpose**: Comprehensive testing to prevent regressions
- **Execution Time**: 5-10 minutes
- **Use Case**: CI/CD pipelines, release validation
- **Example**: Complex scenarios, integration tests

```bash
make test-regression
```

### 3. Integration Tests (`@pytest.mark.integration`)
- **Purpose**: End-to-end user workflows
- **Execution Time**: 3-5 minutes
- **Use Case**: Pre-release testing, feature validation
- **Example**: User registration → login → flan creation

```bash
make test-e2e
```

### 4. Performance Tests (`@pytest.mark.performance`)
- **Purpose**: Performance benchmarking
- **Execution Time**: Varies
- **Use Case**: Performance monitoring, optimization
- **Example**: Complex filtering, large dataset operations

```bash
make test-performance
```

### 5. Slow Tests (`@pytest.mark.slow`)
- **Purpose**: Resource-intensive tests
- **Execution Time**: > 2 seconds each
- **Use Case**: Optional execution, CI with flags
- **Example**: Complex form validation, large queries

```bash
# Exclude slow tests
make test-without-slow

# Include slow tests
make test-slow
```

### 6. Deployment Tests (`@pytest.mark.deployment`)
- **Purpose**: Verify production deployment status
- **Execution Time**: Varies (network dependent)
- **Use Case**: Manual verification, monitoring
- **Example**: Site accessibility, HTTPS redirects, static assets

```bash
# Run deployment tests (requires RUN_DEPLOYMENT_TESTS environment variable)
RUN_DEPLOYMENT_TESTS=true pytest tests/test_deployment.py -v

# Or use the Makefile command
make test-deployment
```

## 🔧 Test Optimization Techniques

### 1. Parameterized Testing

**Before**: Multiple individual tests with similar logic
```python
def test_route1(): ...
def test_route2(): ...
def test_route3(): ...
```

**After**: Single parameterized test
```python
@pytest.mark.parametrize("route,expected", [
    ("/", 200),
    ("/about", 200),
    ("/contact", 200)
])
def test_routes(route, expected): ...
```

**Benefits**:
- 65-87% reduction in test functions
- Easier maintenance
- Better organization
- Same coverage

### 2. Test Marking System

```python
@pytest.mark.smoke          # Fast verification tests
@pytest.mark.regression     # Comprehensive regression tests
@pytest.mark.integration    # End-to-end workflows
@pytest.mark.performance    # Performance benchmarks
@pytest.mark.slow           # Resource-intensive tests
@pytest.mark.api           # API endpoint tests
@pytest.mark.database       # Database operation tests
@pytest.mark.deployment    # Production deployment tests
```

### 3. Parallel Execution

```bash
# Automatic parallelization
pytest -n auto --dist=loadfile

# Manual worker control
pytest -n 4  # 4 workers
pytest -n 8  # 8 workers
```

**Configuration**:
```ini
# pytest.ini
addopts = -v --tb=short -n auto --dist=loadfile
```

### 4. Environment-Aware Testing

```python
@pytest.mark.skipif(
    os.getenv("CI") == "true" and os.getenv("RUN_SLOW_TESTS") != "true",
    reason="Skipping in CI unless RUN_SLOW_TESTS=true"
)
def test_resource_intensive(): ...
```

**Usage**:
```bash
# Skip slow tests in CI by default
RUN_SLOW_TESTS=false pytest

# Run slow tests in CI when needed
RUN_SLOW_TESTS=true pytest
```

### 5. Fixture Optimization

```python
# Module-scoped fixtures for shared data
@pytest.fixture(scope="module")
def setup_full_data(): ...

# Function-scoped fixtures for isolation
@pytest.fixture(scope="function")
def clean_db(): ...
```

## 📈 Performance Optimization

### Test Execution Time Analysis

```bash
# Show slowest tests
pytest --durations=20

# Profile test execution
pytest --profile
```

### Parallelization Strategies

1. **Loadfile Distribution**: `--dist=loadfile` (default)
2. **Work Stealing**: `--dist=worksteal` (for uneven test times)
3. **Manual Grouping**: Group tests by resource usage

### Caching Strategies

```bash
# Cache test results (experimental)
pytest --cache-clear  # Clear cache
pytest --cache-show   # Show cache
```

## 🧪 Test Coverage Optimization

### Coverage Configuration

```ini
# pytest.ini
[tool:pytest]
coverage:
    source = app
    omit =
        app/static/*
        app/templates/*
        */__init__.py
    report =
        exclude_lines =
            pragma: no cover
            def __repr__
            raise NotImplementedError
```

### Coverage Commands

```bash
# HTML coverage report
make test-coverage

# XML coverage for CI
make coverage-check-xml

# Text coverage report
make coverage-report
```

## 🎯 Best Practices

### 1. Test Organization

```
tests/
├── test_auth.py          # Authentication tests
├── test_forms.py         # Form validation tests
├── test_main.py          # Main route tests
├── test_main_unitary.py  # Unit tests for main functions
├── test_maps.py          # Map-related tests
├── test_outils.py        # Utility function tests
├── test_scenarios.py     # End-to-end scenarios
└── test_securite.py      # Security tests
```

### 2. Test Naming Conventions

```python
# Good
test_route_status[home-200]           # Parameterized
test_etabform_parametrize[valid-data]  # Parameterized
test_user_registration_success        # Descriptive
test_login_invalid_credentials        # Descriptive

# Avoid
test1()                                # Not descriptive
test_foo()                             # Not specific
test_that_does_something()             # Too vague
```

### 3. Test Structure

```python
@pytest.mark.smoke
def test_critical_functionality():
    """
    Test critical functionality with:
    - Clear description
    - Single responsibility
    - Proper assertions
    - Clean setup/teardown
    """
    # Arrange
    setup_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert expected == result
    
    # Cleanup (if needed)
    cleanup_data()
```

## 🔧 Advanced Optimization Techniques

### 1. Test Data Factories

```python
# Factory for test users
def create_test_user(**kwargs):
    defaults = {
        "pseudo": "testuser",
        "email": "test@example.com",
        "is_admin": False
    }
    return Utilisateur(**{**defaults, **kwargs})
```

### 2. Test Mocking

```python
# Mock external APIs
from unittest.mock import patch

@patch('requests.get')
def test_external_api(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "mocked"}
    
    result = call_external_api()
    assert result == "mocked"
```

### 3. Test Parallelization Groups

```python
# Group tests by resource usage
@pytest.mark.fast
def test_quick_operation(): ...

@pytest.mark.slow
@pytest.mark.database
def test_complex_query(): ...

@pytest.mark.api
@pytest.mark.network
def test_external_service(): ...

@pytest.mark.deployment
def test_production_site(): ...
```

## 📋 Test Maintenance Checklist

### Adding New Tests

1. **Determine Test Type**: Unit, integration, or E2E?
2. **Choose Test Category**: Smoke, regression, performance?
3. **Parameterize if Possible**: Can this be added to existing parameterized tests?
4. **Add Proper Marks**: `@pytest.mark.smoke`, `@pytest.mark.regression`, etc.
5. **Consider Performance**: Is this a slow test that needs special handling?
6. **Add to Makefile**: Update test execution scripts if needed

### Updating Existing Tests

1. **Check for Redundancy**: Can this be parameterized?
2. **Update Marks**: Ensure proper categorization
3. **Optimize Performance**: Add mocks if needed
4. **Update Documentation**: Keep test documentation current
5. **Verify Coverage**: Ensure changes don't reduce coverage

### Removing Tests

1. **Check Coverage Impact**: Will removal reduce coverage?
2. **Verify Redundancy**: Is this test truly redundant?
3. **Update Parameterized Tests**: Remove from parameter lists if needed
4. **Clean Up Marks**: Remove unused markers
5. **Update Documentation**: Remove from test documentation

## 🎓 Continuous Improvement

### Test Suite Health Metrics

```bash
# Test count by category
pytest --collect-only -q | grep -E "(smoke|regression|integration)" | wc -l

# Test execution time analysis
pytest --durations=50

# Coverage trends
make test-coverage
```

### Regular Optimization Tasks

1. **Monthly**: Review slow tests and optimize
2. **Quarterly**: Analyze test redundancy and parameterize
3. **Bi-annually**: Update test categorization and marks
4. **Annually**: Major test suite refactoring and cleanup

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Parametrize](https://docs.pytest.org/en/latest/parametrize.html)
- [Pytest Markers](https://docs.pytest.org/en/latest/mark.html)
- [Pytest Fixtures](https://docs.pytest.org/en/latest/fixture.html)
- [Pytest Parallel Testing](https://pytest-xdist.readthedocs.io/)

## 🎉 Conclusion

The PlanFlan test suite is now highly optimized with:
- **67% fewer test functions** through parameterization
- **Comprehensive test categorization** for selective execution
- **Advanced parallelization** for faster execution
- **Environment-aware testing** for CI/CD optimization
- **Excellent coverage** maintained throughout

Use the provided Makefile commands and test markers to run the most appropriate tests for your current needs, whether it's quick development feedback or comprehensive CI/CD validation.