# JavaScript Tests for PlanFlan Autocomplete

This directory contains JavaScript tests for the autocomplete functionality using Jest.

## Test Structure

The tests are organized to verify the different behaviors of the autocomplete system:

1. **Page Type Detection**: Tests that the system correctly identifies whether it's on the index page or proposer page
2. **Index Page Behavior**: Tests the redirect behavior when a city is selected on the home page
3. **Proposer Page Behavior**: Tests the hidden field synchronization when a city is selected on the proposer page
4. **URL Parameter Handling**: Tests that URL parameters are correctly set and parsed

## Setup Instructions

To run these tests, you'll need to set up a JavaScript testing environment:

### 1. Install Node.js and npm

Make sure you have Node.js (v14+) and npm installed:

```bash
node -v
npm -v
```

### 2. Install Jest and related dependencies

```bash
npm install --save-dev jest @babel/core @babel/preset-env babel-jest
```

### 3. Configure Babel

Create a `babel.config.js` file in the project root:

```javascript
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        node: 'current'
      }
    }]
  ]
};
```

### 4. Configure Jest

Create a `jest.config.js` file in the project root:

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js', 'json'],
  transform: {
    '^.+\.js$': 'babel-jest'
  },
  testMatch: ['**/tests/javascript/**/*.test.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/app/static/js/$1'
  },
  setupFilesAfterEnv: ['<rootDir>/tests/javascript/setupTests.js']
};
```

### 5. Create setup file

Create `tests/javascript/setupTests.js`:

```javascript
// Mock browser APIs as needed
global.URL = class URL {
  constructor(base, path) {
    this.searchParams = new URLSearchParams();
  }
};

// Add other global mocks as needed
```

### 6. Update package.json

Add test scripts to your `package.json`:

```json
"scripts": {
  "test:js": "jest",
  "test:js:watch": "jest --watch",
  "test:js:coverage": "jest --coverage"
}
```

## Running the Tests

### Run all tests

```bash
npm run test:js
```

### Run tests in watch mode

```bash
npm run test:js:watch
```

### Run tests with coverage

```bash
npm run test:js:coverage
```

## Test Implementation Notes

The current test file (`autocomplete.test.js`) contains the test structure but would need to be adapted to work with the actual implementation:

1. **Module Import**: The tests assume ES6 module imports. You may need to adjust based on how your JavaScript is bundled.

2. **DOM Mocking**: The tests use Jest's mocking capabilities to simulate DOM elements and browser APIs.

3. **Fetch Mocking**: The `fetch` API is mocked to simulate API responses.

4. **Event Simulation**: The tests would need to simulate user interactions like clicking on autocomplete results.

## Alternative Approach: Integration Testing

If setting up Jest proves complex, consider:

1. **Cypress or Playwright**: For end-to-end testing that simulates real user interactions
2. **Python + Selenium**: Use Python's unittest framework with Selenium for browser automation
3. **Manual Testing Guide**: Document the expected behavior for manual QA testing

## Current Test Status

The test file provided is a **template** showing the intended test structure. To make it fully functional:

1. Uncomment and adapt the test implementations
2. Set up proper module mocking for the autocomplete.js file
3. Adjust the mocks to match the actual DOM structure
4. Add error case testing
5. Implement edge case scenarios

## Testing the Specific Fix

The tests should verify that:

1. **On index.html**: City selection redirects to liste_etablissements with proper URL parameters
2. **On proposer_etablissement.html**: City selection updates hidden form fields
3. **No cross-contamination**: Index page doesn't try to sync hidden fields, proposer page doesn't redirect
4. **URL parameter handling**: liste_etablissements correctly extracts and uses the coordinates

This ensures the fix for the lost zoom functionality works correctly while maintaining the proposer page functionality.