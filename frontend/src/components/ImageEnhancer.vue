<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const imageFile = ref(null)
const previewImage = ref('')
const enhancedImage = ref('')
const isProcessing = ref(false)
const brightness = ref(100)
const contrast = ref(100)
const sharpness = ref(100)

// 图片预览相关
const previewVisible = ref(false)
const currentPreviewImage = ref('')

// 打开预览弹窗
const handlePreview = (image) => {
  currentPreviewImage.value = image
  previewVisible.value = true
}

// 处理图片上传
const handleUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target.result
    imageFile.value = file.raw
  }
  reader.readAsDataURL(file.raw)
}

// 处理图片增强
const handleEnhance = async () => {
  if (!imageFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  isProcessing.value = true
  const formData = new FormData()
  formData.append('image', imageFile.value)

  try {
    const response = await axios.post('http://localhost:5001/enhance', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.enhanced_image) {
      enhancedImage.value = response.data.enhanced_image
      ElMessage.success('图片增强处理完成')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '图片处理失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return false
  }
  return true
}
</script>

<template>
  <div class="image-enhancer">
    <div class="upload-section">
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleUpload"
        :before-upload="beforeUpload"
        accept="image/*"
        :disabled="isProcessing"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽图片到这里或 <em>点击上传</em>
        </div>
      </el-upload>
    </div>

    <div v-if="previewImage" class="content-container">
      <div class="preview-section">
        <h3>原图预览</h3>
        <div class="image-preview" @click="handlePreview(previewImage)">
          <el-image :src="previewImage" fit="contain" />
        </div>
      </div>

      <div class="controls-section">
        <h3>参数调整</h3>
        <div class="control-item">
          <span class="label">亮度</span>
          <el-slider
            v-model="brightness"
            :min="0"
            :max="200"
            :step="1"
            :format-tooltip="value => `${value}%`"
          />
        </div>
        <div class="control-item">
          <span class="label">对比度</span>
          <el-slider
            v-model="contrast"
            :min="0"
            :max="200"
            :step="1"
            :format-tooltip="value => `${value}%`"
          />
        </div>
        <div class="control-item">
          <span class="label">锐度</span>
          <el-slider
            v-model="sharpness"
            :min="0"
            :max="200"
            :step="1"
            :format-tooltip="value => `${value}%`"
          />
        </div>
        <el-button 
          type="primary" 
          @click="handleEnhance"
          :loading="isProcessing"
          class="enhance-button"
        >
          开始处理
        </el-button>
      </div>
    </div>

    <div v-if="enhancedImage" class="enhanced-preview">
      <h3>增强效果</h3>
      <div class="image-preview" @click="handlePreview(enhancedImage)">
        <el-image :src="enhancedImage" fit="contain" />
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
.image-enhancer {
  width: 100%;
}

.upload-section {
  margin: 40px 0;
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

.content-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 40px;
  margin-top: 40px;
  padding: 0 20px;
}

.preview-section,
.controls-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.preview-section h3,
.controls-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #ffffff;
}

.image-preview {
  width: 100%;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.image-preview:hover {
  transform: scale(1.02);
}

.image-preview .el-image {
  width: 100%;
  height: 100%;
  background-color: #2a2a2a;
}

.control-item {
  margin-bottom: 24px;
}

.control-item .label {
  display: block;
  margin-bottom: 8px;
  color: #ffffff;
}

:deep(.el-slider__runway) {
  background-color: #2a2a2a;
}

:deep(.el-slider__bar) {
  background-color: #409EFF;
}

.enhance-button {
  width: 100%;
  margin-top: 20px;
}

.enhanced-preview {
  margin-top: 40px;
  padding: 0 20px;
}

.enhanced-preview h3 {
  color: #ffffff;
  margin-bottom: 20px;
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
</style>