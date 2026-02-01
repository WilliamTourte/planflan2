module.exports = {
    "env": {
        "browser": true,
        "es2021": true,
        "jest": true,
        "node": true
    },
    "extends": [
        "eslint:recommended",
        "plugin:jsdoc/recommended",
        "plugin:jest/recommended"
    ],
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module"
    },
    "plugins": ["jsdoc", "jest"],
    "rules": {
        "jsdoc/check-alignment": "error",
        "jsdoc/check-indentation": "error",
        "jsdoc/require-description": "error",
        "jsdoc/require-param": "error",
        "jsdoc/require-returns": "error",
        "jsdoc/require-jsdoc": [
            "error",
            {
                "require": {
                    "FunctionDeclaration": true,
                    "MethodDefinition": true,
                    "ClassDeclaration": true,
                    "ArrowFunctionExpression": false
                }
            }
        ],
        "jest/no-disabled-tests": "warn",
        "jest/no-focused-tests": "error",
        "jest/no-identical-title": "error",
        "jest/prefer-to-have-length": "warn",
        "jest/valid-expect": "error"
    },
    "overrides": [
        {
            "files": ["tests/javascript/**/*.test.js"],
            "rules": {
                "jsdoc/require-jsdoc": "off"
            }
        }
    ]
};