<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import JSZip from 'jszip'

const videoFile = ref(null)
const uploadUrl = 'http://localhost:5001/upload'
const frames = ref([])
const displayedFrames = ref([])
const uploadProgress = ref(0)
const processProgress = ref(0)
const isUploading = ref(false)
const uploadStartTime = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalFrames = ref(0)
const previewVisible = ref(false)
const currentPreviewImage = ref('')

// 处理页面变化
const handlePageChange = (page) => {
  currentPage.value = page
  updateDisplayedFrames()
}

// 监听frames数组变化
watch(frames, () => {
  console.log('Frames array length:', frames.value.length);
  currentPage.value = 1;
  totalFrames.value = frames.value.length;
  updateDisplayedFrames();
}, { deep: true });

// 计算当前应该显示的帧
const updateDisplayedFrames = () => {
  if (!frames.value || frames.value.length === 0) {
    displayedFrames.value = [];
    return;
  }
  const start = (currentPage.value - 1) * pageSize.value;
  const end = Math.min(start + pageSize.value, frames.value.length);
  displayedFrames.value = frames.value.slice(start, end);
  totalFrames.value = frames.value.length;
};



const handleUpload = async (file) => {
  try {
    isUploading.value = true;
    uploadProgress.value = 0;
    processProgress.value = 0;
    frames.value = [];
    
    const formData = new FormData();
    formData.append('video', file.raw);
    uploadStartTime.value = Date.now();
    
    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = '上传失败';
      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        errorMessage = `服务器响应错误: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }
    
    uploadProgress.value = 100; // 设置上传进度为100%
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      let boundary = buffer.indexOf('\n');

      while (boundary !== -1) {
        const line = buffer.slice(0, boundary).trim();
        buffer = buffer.slice(boundary + 1);
        boundary = buffer.indexOf('\n');

        if (line.length > 0) {
          try {
            const data = JSON.parse(line);
            if (data.type === 'progress') {
              processProgress.value = data.progress;
            } else if (data.type === 'batch') {
              console.log('收到的帧数据:', data.frames)
              frames.value.push(...data.frames);
              console.log('Updated frames length:', frames.value.length);
            }
          } catch (e) {
            console.error('解析数据失败:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('上传失败:', error);
    ElMessage.error(error.message || '上传失败');
  } finally {
    isUploading.value = false;
  }
};

const beforeUpload = (file) => {
  const isVideo = file.type.startsWith('video/');
  if (!isVideo) {
    ElMessage.error('请上传视频文件');
    return false;
  }
  return true;
};

// 处理图片预览
const handlePreview = (frame) => {
  currentPreviewImage.value = frame;
  previewVisible.value = true;
};

// 保存所有帧
const saveAllFrames = async () => {
  try {
    const zip = new JSZip();
    const promises = frames.value.map(async (frame, index) => {
      try {
        // 从base64数据中提取实际的图片数据
        const base64Data = frame.split(',')[1];
        zip.file(`frame_${index + 1}.jpg`, base64Data, { base64: true });
      } catch (error) {
        console.error(`处理第${index + 1}帧时出错:`, error);
      }
    });

    await Promise.all(promises);
    const content = await zip.generateAsync({ type: 'blob' });
    const url = window.URL.createObjectURL(content);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'frames.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success('帧导出成功');
  } catch (error) {
    console.error('导出帧失败:', error);
    ElMessage.error('导出帧失败');
  }
};
</script>

<template>
  <div class="video-frames">
    <div class="upload-section">
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleUpload"
        :before-upload="beforeUpload"
        accept="video/*"
        :disabled="isUploading"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽视频到这里或 <em>点击上传</em>
        </div>
      </el-upload>
    </div>
    
    <div v-if="isUploading" class="progress-container">
      <div class="progress-item">
        <div class="progress-label">
          <span>上传进度</span>
          <span class="progress-time" v-if="uploadStartTime">
            {{ Math.floor((Date.now() - uploadStartTime) / 1000) }}s
          </span>
        </div>
        <el-progress 
          :percentage="uploadProgress"
          :format="format => `${format}%`"
          :status="uploadProgress === 100 ? 'success' : 'primary'"
          :stroke-width="15"
        />
      </div>
      <div class="progress-item">
        <div class="progress-label">
          <span>处理进度</span>
          <span class="progress-time" v-if="processProgress > 0">
            {{ Math.floor((Date.now() - uploadStartTime) / 1000) }}s
          </span>
        </div>
        <el-progress 
          :percentage="processProgress"
          :format="format => `${format}%`"
          :status="processProgress === 100 ? 'success' : 'primary'"
          :stroke-width="15"
        />
      </div>
    </div>

    <div v-if="frames.length" class="frames-container">
      <h2>分帧结果</h2>
      <el-button type="primary" @click="saveAllFrames" class="save-all-button">
        <el-icon><download /></el-icon>
        保存所有帧
      </el-button>
      <div class="frames-grid">
        <div v-for="(frame, index) in displayedFrames" :key="index" class="frame-item" @click="handlePreview(frame)">
          <el-image :src="frame" fit="cover" />
          <span class="frame-index">帧 {{ (currentPage - 1) * pageSize + index + 1 }}</span>
        </div>
      </div>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="frames.length"
          @current-change="handlePageChange"
          layout="prev, pager, next"
          background
        />
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      width="80%"
      :show-close="true"
      class="preview-dialog"
      :modal-class="'preview-dialog-modal'"
    >
      <div class="preview-image-container">
        <el-image
          :src="currentPreviewImage"
          fit="contain"
          class="preview-image"
        />
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.video-frames {
  width: 100%;
}

.progress-container {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.progress-item {
  margin-bottom: 20px;
}

.progress-item:last-child {
  margin-bottom: 0;
}

.progress-label {
  margin-bottom: 8px;
  color: #ffffff;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-time {
  color: #909399;
  font-size: 12px;
}

:deep(.el-upload-dragger) {
  background-color: #2a2a2a;
  border-color: #4a4a4a;
  color: #ffffff;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409EFF;
}

:deep(.el-upload__text) {
  color: #ffffff;
}

:deep(.el-upload__text em) {
  color: #409EFF;
}

:deep(.el-progress-bar__outer) {
  background-color: #2a2a2a;
}

:deep(.el-progress-bar__inner) {
  background-color: #409EFF;
}

.upload-section {
  margin: 40px 0;
}

.frames-container {
  margin-top: 40px;
  position: relative;
}

.save-all-button {
  position: absolute;
  right: 20px;
  top: 0;
}

.frames-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
  padding: 0 20px;
}

.frame-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  aspect-ratio: 16/9;
  height: auto;
  cursor: pointer;
  transition: transform 0.2s;
}

.frame-item:hover {
  transform: scale(1.02);
}

.frame-item .el-image {
  width: 100%;
  height: 100%;
}

.frame-index {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px;
  text-align: center;
  font-size: 14px;
}

.el-upload__text {
  margin-top: 10px;
}

/* 预览弹窗样式 */
:deep(.preview-dialog) {
  background: transparent;
}

:deep(.preview-dialog .el-dialog__header) {
  display: none;
}

:deep(.preview-dialog .el-dialog__body) {
  padding: 0;
  background: transparent;
}

.preview-image-container {
  width: 100%;
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

:deep(.preview-dialog-modal) {
  background: rgba(0, 0, 0, 0.8);
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: #2a2a2a;
  --el-pagination-hover-color: #409EFF;
  --el-pagination-button-color: #ffffff;
  --el-pagination-button-bg-color: transparent;
  --el-pagination-button-disabled-color: #606266;
  --el-pagination-button-disabled-bg-color: transparent;
  --el-pagination-hover-bg-color: #363636;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled)) {
  background-color: #2a2a2a;
  color: #ffffff;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #409EFF;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background-color: #2a2a2a;
  color: #ffffff;
}

:deep(.el-pagination .btn-prev:disabled),
:deep(.el-pagination .btn-next:disabled) {
  background-color: #1a1a1a;
  color: #606266;
}
</style>