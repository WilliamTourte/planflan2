import jsdoc from "eslint-plugin-jsdoc";

export default [
    {
        files: ["**/*.js"],
        ignores: ["node_modules/**"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            globals: {
                browser: true
            }
        },
        plugins: {
            jsdoc
        },
        rules: {
            ...jsdoc.configs.recommended.rules,
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
            ]
        }
    }
];