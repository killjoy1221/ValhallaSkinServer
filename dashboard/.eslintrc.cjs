module.exports = {
  root: true,
  env: {
    browser: true,
    commonjs: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/vue3-essential",
    "@vue/eslint-config-typescript",
  ],
  rules: {
    camelcase: "warn",
    "consistent-return": "error",
    "dot-notation": "warn",
    eqeqeq: "warn",
    "no-alert": "error",
    "no-console": "error",
    "no-else-return": "warn",
    "no-eval": "error",
    "no-implicit-coercion": "error",
    "no-implied-eval": "error",
    "no-invalid-this": "error",
    "no-script-url": "error",
    "vue/multi-word-component-names": "off",
  },
};