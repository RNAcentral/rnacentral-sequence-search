const path = require('path');
const webpack = require('webpack');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const nodeExternals = require('webpack-node-externals');


module.exports = function(env) {
  // set variables, modifying the config for dev, prod and ssr
  // see: https://github.com/webpack/webpack/issues/2254
  let environment;
  if (env && env.prod) environment = 'production';
  else environment = 'development';

  let target, externals, entry, plugins, publicPath, outputFilename;
  if (environment === 'production') {
    target = 'web';
    externals = [];
    entry = path.join(__dirname, 'src', 'app.jsx');
    plugins = [
      new webpack.HotModuleReplacementPlugin(),
      new ExtractTextPlugin('app.[hash:7].css'),
      new HtmlWebpackPlugin({ inject: "body", template: "src/index.html", filename: path.join(__dirname, "index.html") }),
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', jquery: 'jquery' })
    ];
    publicPath = '/dist/';
    outputFilename = 'app.[hash:7].js';

  } else if (environment === 'development') {
    target = 'web';
    externals = [];
    entry = path.join(__dirname, 'src', 'app.jsx');
    plugins = [
      new webpack.HotModuleReplacementPlugin(),
      new ExtractTextPlugin('app.[hash:7].css'),
      new HtmlWebpackPlugin({ inject: "body", template: "src/index.html", filename: "index.html" }),
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', jquery: 'jquery' })
    ];
    publicPath = '/';
    outputFilename = 'app.[hash:7].js';

  }

  return {
    target: target,
    externals: externals,
    entry: entry,
    output: {
      path: path.join(__dirname, 'dist'),
      publicPath: publicPath,
      filename: outputFilename
    },
    resolve: {
      modules: [path.join(__dirname, 'src'), path.join(__dirname, 'node_modules')]
    },
    plugins: plugins,
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          loader: 'babel-loader',
          exclude: /node_modules/,
          query: {
            presets: ['es2015', 'react'],
            plugins: ['transform-es2015-destructuring', 'transform-object-rest-spread']
          }
        },
        {
          test: /\.(s?css|sass)$/,
          use: ExtractTextPlugin.extract({
            use: [
              { loader: 'css-loader', options: {sourceMap: true} },
              { loader: 'sass-loader', options: {sourceMap: true} }
            ]
          })
        },
        {
          test: /\.(png|jpe?g|gif)(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader' // 'url-loader?limit=10000'
        },
        {
          test: /\.(eot|com|json|ttf|woff|woff2)(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader' // 'url-loader?limit=10000&mimetype=application/octet-stream'
        },
        {
          test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader' // 'url-loader?limit=10000&mimetype=image/svg+xml'
        }
      ]
    },
    devServer: {
      publicPath: '/',
      contentBase: './',
      hot: true
    },
    devtool: "source-map"
  };
};