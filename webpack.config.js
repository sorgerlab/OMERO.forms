// webpack.config.js
var webpack = require('webpack');

var path = require('path');

module.exports = {
  entry: {
    'bundle.min': ['whatwg-fetch', './src/main.jsx'],
    'bundle': ['whatwg-fetch', './src/main.jsx'],
    'designer': ['whatwg-fetch', './src/designer.jsx'],
    'designer.min': ['whatwg-fetch', './src/designer.jsx'],
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
          presets: ['react', 'es2015', 'stage-2']
        }
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          plugins: ['transform-runtime'],
          presets: ['es2015', 'stage-2']
        }
      },
      {
        test: /\.css$/, // Only .css files
        loader: 'style-loader!css-loader' // Run both loaders
      },
      { test: /\.png$/,
        loader: "url-loader?limit=100000"
      },

      // Bootstrap
      {
        test: /\.(woff|woff2)(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url?limit=10000&mimetype=application/font-woff'},
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url?limit=10000&mimetype=application/octet-stream'
      },
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'file'
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url?limit=10000&mimetype=image/svg+xml'
      }

    ]
  },
  resolve: {
    extensions: ['', '.js', '.jsx', '.json']
  },
};
