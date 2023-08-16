module.exports = {
  extends: ["airbnb", "prettier"],
  env: {
    browser: true,
  },
  overrides: [
    {
      files: ["**/*.test.js"],
      env: {
        jest: true,
      },
    },
  ],
  parser: "@babel/eslint-parser",
  plugins: ["prettier"],
  rules: {
    "prettier/prettier": "error",
    "react/jsx-filename-extension": ["error", { extensions: [".js"] }],
    "react/jsx-fragments": "off",
    "react/jsx-props-no-spreading": "off",
    "react/state-in-constructor": "off",
    "react/static-property-placement": "off",
    "react/function-component-definition": "off",
  },
  parserOptions: {
    ecmaVersion: "2018",
  },
};
