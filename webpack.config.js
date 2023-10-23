// webpack.config.js
var webpack = require('webpack');
const TerserPlugin = require("terser-webpack-plugin");
var path = require('path');

module.exports = {
  entry: {
    'bundle.min': ['whatwg-fetch', './src/main.jsx'],
    'bundle': ['whatwg-fetch', './src/main.jsx'],
    'designer': ['whatwg-fetch', './src/designer.jsx'],
    'designer.min': ['whatwg-fetch', './src/designer.jsx'],
  },
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()],
  },
  output: {
    path: __dirname + '/omero_forms/static/forms/js',
    filename: '[name].js',
    library: 'omeroforms'
  },
  plugins: [],
  module: {
    rules: [
      {
        test: /\.jsx$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          plugins: ['transform-runtime'],
          presets: ['@babel/react', '@babel/env', '@babel/stage-2']
        }
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          plugins: ['transform-runtime'],
          presets: ['@babel/env', '@babel/stage-2']
        }
      },
      {
        test: /\.css$/, // Only .css files
        use: ['style-loader', 'css-loader'], // Run both loaders
      },
      { 
        test: /\.png$/,
        use: [
          {
            loader: "url-loader",
            options: {
              limit: 100000,
            },
          },
        ],
      },

      // Bootstrap
      {
        test: /\.(woff|woff2)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              mimetype: 'application/font-woff',
            },
          },
        ],
      },
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              mimetype: 'application/octet-stream',
            },
          },
        ],
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
          },
        ],
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              mimetype: 'image/svg+xml',
            },
          },
        ],
      }

    ]
  },
  resolve: {
    extensions: ['', '.js', '.jsx', '.json']
  },
};
