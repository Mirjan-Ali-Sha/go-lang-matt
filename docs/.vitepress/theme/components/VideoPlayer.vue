<template>
  <div class="video-visualization-box no-print">
    <details>
      <summary>🎥 Video Lecture: <code>Go Class {{ chapter }}</code></summary>
      <div class="player-controls">
        <div class="player-modes">
          <button 
            :class="['mode-btn', currentMode === 'standard' ? 'active' : '']" 
            @click="setMode('standard')"
          >
            Standard
          </button>
          <button 
            :class="['mode-btn', currentMode === 'privacy' ? 'active' : '']" 
            @click="setMode('privacy')"
          >
            Privacy Mode
          </button>
          <a 
            class="mode-btn link-btn" 
            :href="youtubeUrl" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Watch on YouTube ↗
          </a>
        </div>
      </div>
      <div class="video-iframe-container">
        <iframe 
          :src="embedUrl" 
          title="YouTube video player" 
          frameborder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
          allowfullscreen
          class="video-iframe"
        ></iframe>
      </div>
    </details>
  </div>
</template>

<script>
export default {
  name: 'VideoPlayer',
  props: {
    videoId: {
      type: String,
      required: true
    },
    chapter: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      currentMode: 'standard'
    }
  },
  computed: {
    embedUrl() {
      if (this.currentMode === 'privacy') {
        return `https://www.youtube-nocookie.com/embed/${this.videoId}`
      }
      return `https://www.youtube.com/embed/${this.videoId}`
    },
    youtubeUrl() {
      return `https://www.youtube.com/watch?v=${this.videoId}`
    }
  },
  methods: {
    setMode(mode) {
      this.currentMode = mode
    }
  }
}
</script>

<style scoped>
.video-visualization-box {
  margin: 1rem 0;
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
}

.video-visualization-box summary {
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  color: var(--vp-c-brand-1);
}

.video-visualization-box summary:hover {
  color: var(--vp-c-brand-2);
}

.player-controls {
  margin-top: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.player-modes {
  display: flex;
  gap: 0.5rem;
  background: var(--vp-c-bg-alt);
  padding: 0.25rem;
  border-radius: 6px;
  border: 1px solid var(--vp-c-divider);
}

.mode-btn {
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.mode-btn:hover {
  color: var(--vp-c-text-1);
  background-color: var(--vp-c-bg-soft-hover);
}

.mode-btn.active {
  background-color: var(--vp-c-brand-1);
  color: var(--vp-c-white);
}

.link-btn {
  display: flex;
  align-items: center;
}

.video-iframe-container {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  height: 0;
  overflow: hidden;
  border-radius: 6px;
  border: 1px solid var(--vp-c-divider);
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
