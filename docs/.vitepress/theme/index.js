import DefaultTheme from 'vitepress/theme'
import './custom.css'
import VideoPlayer from './components/VideoPlayer.vue'

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {
    app.component('VideoPlayer', VideoPlayer)
  }
}
