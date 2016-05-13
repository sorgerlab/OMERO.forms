// webpack.config.js
var webpack = require('webpack');

var path = require('path');

module.exports = {
  entry: {
    'bundle.min': ['babel-polyfill', './src/main.jsx'],
    'bundle': ['babel-polyfill', './src/main.jsx'],
  },
  output: {
    path: './static/forms/js',
    filename: '[name].js',
    library: 'omeroforms'
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin({
      include: /\.min\.js$/,
      minimize: true
    })
  ],
  module: {
    loaders: [
      {
        test: /\.jsx$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          plugins: ['transform-runtime'],
          presets: ['react', 'es2015']
        }
      },
      {
        test: /\.css$/, // Only .css files
        loader: 'style-loader!css-loader' // Run both loaders
      },
      { test: /\.png$/,
        loader: "url-loader?limit=100000"
      }
    ]
  },
  resolve: {
    extensions: ['', '.js', '.jsx', '.json']
  },
};
