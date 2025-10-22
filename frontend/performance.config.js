// Configuración de optimización de rendimiento para React
module.exports = {
  // Deshabilitar source maps en desarrollo para acelerar
  generateSourceMap: false,
  
  // Habilitar Fast Refresh
  fastRefresh: true,
  
  // Optimizaciones de Webpack
  webpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      },
    },
  },
};
