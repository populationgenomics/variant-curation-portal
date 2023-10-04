module.exports = {
  testEnvironment: "jsdom",
  transformIgnorePatterns: ["!node_modules/(?!query-string|decode-uri-component)"],
  globals: {
    TextDecoder: require("util").TextDecoder, // eslint-disable-line
  },
};
