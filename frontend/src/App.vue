<script setup>
import { ref } from 'vue'
import VideoFrames from './components/VideoFrames.vue'
import ImageEnhancer from './components/ImageEnhancer.vue'

const activeTab = ref('video-frames')
</script>

<template>
  <div class="container dark">
    <div class="content-wrapper">
      <h1 class="app-title">视频图像工具箱</h1>
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane label="视频分帧" name="video-frames">
          <VideoFrames />
        </el-tab-pane>
        <el-tab-pane label="图片清晰度调整" name="image-enhancer">
          <ImageEnhancer />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.container.dark {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background-color: #1a1a1a;
  color: #ffffff;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  max-width: 100%;
  margin: 0 auto;
  padding: 40px 40px;
  width: 100%;
  box-sizing: border-box;
}

.app-title {
  text-align: center;
  margin-bottom: 40px;
  font-size: 2.5em;
  font-weight: 600;
  background: linear-gradient(45deg, #409EFF, #36cfc9);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

:deep(.main-tabs .el-tabs__header) {
  border-bottom: 1px solid #4a4a4a;
  margin-bottom: 30px;
}

:deep(.main-tabs .el-tabs__nav-wrap::after) {
  background-color: #4a4a4a;
}

:deep(.main-tabs .el-tabs__item) {
  color: #909399;
  font-size: 16px;
}

:deep(.main-tabs .el-tabs__item.is-active) {
  color: #409EFF;
}

:deep(.main-tabs .el-tabs__active-bar) {
  background-color: #409EFF;
}
</style>
