// vite.config.js
import { resolve } from 'path'
import { defineConfig } from 'vite'


export default defineConfig({
    build: {
        outDir: 'dist',
        assetsDir: '',
        sourcemap: false,
        minify: true,
        lib: {
            // Could also be a dictionary or array of multiple entry points
            entry: 'src/main.js', // Entry file for your library
            name: 's3Field',
            fileName: 'js/s3field',
        },
        rollupOptions: {
            output: {
                format: 'es',
            },
        },
    },
})


