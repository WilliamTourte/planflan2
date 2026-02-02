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
        "jsdoc/require-description": "warn",
        "jsdoc/require-param": "warn",
        "jsdoc/require-returns": "warn",
        "jsdoc/require-jsdoc": [
            "warn",
            {
                "require": {
                    "FunctionDeclaration": true,
                    "MethodDefinition": true,
                    "ClassDeclaration": true,
                    "ArrowFunctionExpression": false,
                    "FunctionExpression": false
                },
                "contexts": [
                    "any-function"
                ]
            }
        ],
        "jest/no-disabled-tests": "warn",
        "jest/no-focused-tests": "error",
        "jest/no-identical-title": "error",
        "jest/prefer-to-have-length": "warn",
        "jest/valid-expect": "error",
        "max-len": [
            "warn",
            {
                "code": 100,
                "ignorePattern": "(^\\s*import |^\\s*export )",
                "ignoreStrings": true,
                "ignoreTemplateLiterals": true
            }
        ]
    },
    "overrides": [
        {
            "files": ["tests/**/*.test.js", "tests/**/*.spec.js"],
            "rules": {
                "jsdoc/require-jsdoc": "off"
            }
        },
        {
            "files": ["*.config.js"],
            "rules": {
                "jsdoc/require-jsdoc": "off"
            }
        }
    ]
};