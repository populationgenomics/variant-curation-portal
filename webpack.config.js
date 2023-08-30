const path = require("path");

const BundleTracker = require("webpack-bundle-tracker");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

const isDev = process.env.NODE_ENV === "development";

const config = {
  devServer: {
    historyApiFallback: true,
    port: 3000,
    proxy: {
      "/": "http://127.0.0.1:8000",
    },
    static: {
      directory: path.join(__dirname, "static/bundles"),
      publicPath: "/static/bundles/",
    },
    client: {
      logging: "error",
    },
  },
  devtool: "source-map",
  entry: {
    bundle: "./assets/index.js",
  },
  mode: isDev ? "development" : "production",
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            rootMode: "upward",
            presets: ["@babel/react", "@babel/preset-env"],
            plugins: ["@babel/plugin-proposal-class-properties"],
          },
        },
      },
      {
        test: /\.css$/,
        use: [isDev ? "style-loader" : MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(png|svg|eot|ttf|woff2?)$/,
        use: "file-loader",
      },
    ],
  },
  output: {
    path: path.join(path.resolve(__dirname), "static/bundles"),
    publicPath: "/static/bundles/",
    filename: isDev ? "[name].js" : "[name]-[hash].js",
    hashFunction: "sha256",
  },
  plugins: [
    new webpack.EnvironmentPlugin({ NODE_ENV: "production" }),
    new BundleTracker({ path: path.resolve(__dirname), filename: "webpack-stats.json" }),
    new CleanWebpackPlugin(),
    new CopyPlugin({
      patterns: ["assets/results-schema.json", "assets/variants-schema.json"],
    }),
    new MiniCssExtractPlugin({
      filename: isDev ? "[name].css" : "[name]-[hash].css",
      chunkFilename: isDev ? "[id].css" : "[id]-[hash].css",
    }),
  ],
};

module.exports = config;
