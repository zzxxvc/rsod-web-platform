<template>
  <div class="detection-page">
    <header class="page-header">
      <div class="page-label">皮肤病变诊断</div>
      <h1 class="page-title">医学级皮肤病变智能分类平台</h1>
      <p class="page-subtitle">
        上传皮肤影像，快速识别病变类型、风险等级和辅助诊断建议。
      </p>
    </header>

    <!-- 顶部导航由全局 Header 提供 -->

    <!-- 主体：左侧上传，右侧大区域显示原图与检测图并显示结果 -->
    <section class="main-layout">
      <aside class="left-panel">
        <div class="mode-menu">
          <div
            v-for="item in modeMenu"
            :key="item.key"
            class="mode-item"
            :class="{ active: activeMode === item.key }"
            @click="setMode(item.key)"
          >
            <el-icon class="mode-icon"><component :is="item.icon" /></el-icon>
            <span class="mode-label">{{ item.label }}</span>
          </div>
        </div>

        <div class="upload-card">
          <p class="upload-card-desc">
            选择上传方式：单张图像、批量图像、视频文件，或开启摄像头实时检测。
          </p>

          <div class="upload-actions">
            <el-button
              v-if="activeMode === 'single'"
              type="primary"
              size="large"
              @click="triggerUpload"
            >
              <el-icon><Upload /></el-icon>
              上传单图
            </el-button>

            <el-button
              v-if="activeMode === 'batch'"
              type="primary"
              size="large"
              @click="triggerUpload"
            >
              上传批量图片
            </el-button>

            <el-button
              v-if="activeMode === 'video'"
              type="primary"
              size="large"
              @click="triggerUpload"
            >
              上传视频
            </el-button>

            <el-button
              v-if="activeMode === 'live'"
              type="primary"
              size="large"
              @click="startLive"
            >
              实时检测
            </el-button>

            <input
              ref="fileInput"
              type="file"
              :accept="fileAccept"
              :multiple="activeMode === 'batch'"
              class="file-input"
              @change="handleFileChange($event)"
            />
          </div>

          <div class="upload-tip">
            支持 JPG / PNG /
            MP4（视频），批量支持多选图片。隐私保护，上传后开始分析。
          </div>
        </div>

        <div class="info-cards">
          <div class="info-card small-card">
            <div class="info-card-heading">当前模型</div>
            <el-select v-model="selectedModel" class="model-select">
              <el-option label="DermNet-v1" value="DermNet-v1" />
              <el-option label="DermNet-v2" value="DermNet-v2" />
            </el-select>
          </div>

          <div class="info-card small-card">
            <div class="info-card-heading">使用提示</div>
            <ul class="tip-list">
              <li>单张图像即可完成分类。</li>
              <li>批量模式会逐张上传并显示结果。</li>
              <li>实时检测需允许摄像头权限。</li>
            </ul>
          </div>
        </div>
      </aside>

      <main class="center-panel">
        <div class="viewer">
          <div class="viewer-pane original">
            <div class="viewer-title">原图</div>
            <div class="viewer-content image-box">
              <template v-if="originalImage">
                <img :src="originalImage" alt="原始图像" />
              </template>
              <template v-else>
                <div class="placeholder">未上传图像</div>
              </template>
            </div>
            <div class="viewer-footer">{{ originalFilename }}</div>
          </div>

          <div class="viewer-pane result">
            <div class="viewer-title">检测结果</div>
            <div class="viewer-content image-box">
              <template v-if="resultImage">
                <img :src="resultImage" alt="检测结果图" />
              </template>
              <template v-else>
                <div class="placeholder">未检测</div>
              </template>
            </div>
            <div class="viewer-footer">{{ detectionStatus }}</div>
          </div>
        </div>

        <section
          class="result-section"
          v-if="currentPredictions.length || detectionResult"
        >
          <div class="result-summary">
            <div class="summary-card">
              <div class="summary-title">当前结论</div>
              <div class="summary-value">{{ topLabel }}</div>
              <div class="summary-note">最高置信度 {{ topConfidence }}</div>
            </div>

            <div class="summary-card summary-emphasis">
              <div class="summary-title">风险评估</div>
              <div class="risk-badge" :class="riskClass">{{ riskLevel }}</div>
              <div class="summary-note">建议根据结果安排专家复诊。</div>
            </div>

            <div class="summary-card">
              <div class="summary-title">分析耗时</div>
              <div class="summary-value">
                {{ detectionResult?.detection_time || 0 }}s
              </div>
              <div class="summary-note">
                模型：{{ detectionResult?.model_name || selectedModel }}
              </div>
            </div>
          </div>

          <div class="detail-panel">
            <div class="detail-card prediction-card">
              <div class="detail-title">分类结果</div>
              <div class="prediction-list">
                <div
                  v-for="(item, index) in currentPredictions"
                  :key="index"
                  class="prediction-item"
                >
                  <div>
                    <div class="prediction-label">{{ item.class_name }}</div>
                    <div class="prediction-subtext">
                      辅助概率排名 {{ index + 1 }}
                    </div>
                  </div>
                  <div class="prediction-score">
                    {{ (item.confidence * 100).toFixed(1) }}%
                  </div>
                </div>
                <div v-if="!currentPredictions.length" class="empty-state">
                  暂无分类结果
                </div>
              </div>
            </div>

            <div class="detail-card suggestion-card">
              <div class="detail-title">辅助建议</div>
              <p class="suggestion-text">{{ suggestionText }}</p>
              <div class="action-footer">
                <el-button type="primary" size="small" @click="triggerUpload"
                  >重新上传</el-button
                >
                <el-button size="small" @click="viewReport">
                  查看报告
                </el-button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Picture,
  Document,
  VideoCamera,
  Camera,
} from "@element-plus/icons-vue";
import { ElMessage, ElLoading } from "element-plus";
import { ChatDotRound, Upload } from "@element-plus/icons-vue";
import { detectSingleImage } from "../api/detection";

const selectedModel = ref("DermNet-v1");
const detectionResult = ref(null);
const detectionResults = ref([]); // for batch
const originalFilename = ref("未上传图像");
const fileInput = ref(null);
const activeMode = ref("single");

const detectionStatus = ref("未检测");

// 顶部应用导航状态
const router = useRouter();
const route = useRoute();
const topActive = ref(route.path.replace(/^\//, "") || "detection");

const onTopTabClick = (pane) => {
  const name = pane?.name || "";
  if (name) router.push(`/` + name);
};

watch(
  () => route.path,
  (p) => {
    topActive.value = p.replace(/^\//, "") || "detection";
  },
);

const backendBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/api$/, "") ||
  "http://localhost:8000";

const originalImage = ref(
  new URL("../assets/images/bus.jpg", import.meta.url).href,
);
const resultImage = ref(
  new URL("../assets/images/predict-bus.png", import.meta.url).href,
);

const modeMenu = [
  { key: "single", label: "单图", icon: Picture },
  { key: "batch", label: "批量", icon: Document },
  { key: "video", label: "视频", icon: VideoCamera },
  { key: "live", label: "实时", icon: Camera },
];

const setMode = (key) => {
  activeMode.value = key;
};

const topPrediction = computed(() => {
  if (activeMode.value === "batch") {
    const first = detectionResults.value?.[0];
    return first?.boxes?.[0] || null;
  }
  if (!detectionResult.value?.boxes?.length) return null;
  return detectionResult.value.boxes[0];
});

const topPredictions = computed(() => {
  if (activeMode.value === "batch") {
    const first = detectionResults.value?.[0];
    return first?.boxes?.slice(0, 3) || [];
  }
  return detectionResult.value?.boxes?.slice(0, 3) || [];
});

const topLabel = computed(() => topPrediction.value?.class_name || "暂无预测");

const topConfidence = computed(() =>
  topPrediction.value
    ? `${(topPrediction.value.confidence * 100).toFixed(1)}%`
    : "0%",
);

const riskLevel = computed(() => {
  const score = topPrediction.value?.confidence || 0;
  if (score > 0.86) return "高风险";
  if (score > 0.72) return "中风险";
  if (score > 0.48) return "低风险";
  return "待确认";
});

const riskClass = computed(() => {
  if (riskLevel.value === "高风险") return "risk-high";
  if (riskLevel.value === "中风险") return "risk-medium";
  if (riskLevel.value === "低风险") return "risk-low";
  return "risk-unknown";
});

const suggestionText = computed(() => {
  if (!detectionResult.value?.boxes?.length) return "请先上传图像开始诊断。";
  if (riskLevel.value === "高风险")
    return "建议尽快结合专家诊断并安排进一步检查。";
  if (riskLevel.value === "中风险") return "建议关注病变变化并及时复诊。";
  return "建议继续观察，必要时定期随访。";
});

const triggerUpload = () => {
  fileInput.value?.click();
};

const fileAccept = computed(() => {
  if (activeMode.value === "video") return "video/*";
  return "image/*";
});

const modeLabel = computed(() => {
  if (activeMode.value === "single") return "单图";
  if (activeMode.value === "batch") return "批量";
  if (activeMode.value === "video") return "视频";
  return "实时";
});

const startLive = () => {
  ElMessage.info("实时检测已启动（示例 UI，仅前端占位）");
};

const getFullUrl = (relativeUrl) => {
  if (!relativeUrl) return "";
  if (/^https?:\/\//.test(relativeUrl)) return relativeUrl;
  return `${backendBaseUrl}${relativeUrl}`;
};

const handleFileChange = async (event) => {
  event.stopPropagation();
  event.preventDefault();
  const files = Array.from(event.target.files || []);
  if (!files.length) return;
  if (activeMode.value === "batch") {
    originalFilename.value = `${files.length} 张图片`;
    await performBatchDetection(files);
  } else if (activeMode.value === "video") {
    originalFilename.value = files[0].name;
    detectionStatus.value = "视频上传，处理中...";
    // 视频处理占位
    await performSingleDetection(files[0]);
  } else {
    const file = files[0];
    originalFilename.value = file.name;
    await performSingleDetection(file);
  }
  setTimeout(() => {
    event.target.value = "";
  }, 0);
};

const performBatchDetection = async (files) => {
  detectionResults.value = [];
  for (const file of files) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("model_name", selectedModel.value);
      const response = await detectSingleImage(formData);
      if (response.success && response.data) {
        detectionResults.value.push(response.data);
      }
    } catch (err) {
      console.error("批量检测单张出错", err);
    }
  }
  // 显示第一张结果为预览
  if (detectionResults.value[0]) {
    detectionResult.value = detectionResults.value[0];
    originalImage.value = URL.createObjectURL(files[0]);
    resultImage.value = getFullUrl(detectionResults.value[0].result_image_url);
    detectionStatus.value = "批量检测完成";
    ElMessage.success("批量检测完成");
  }
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "正在分析图像...",
    background: "rgba(0, 0, 0, 0.75)",
  });

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", selectedModel.value);

    originalImage.value = URL.createObjectURL(file);
    const response = await detectSingleImage(formData);

    if (response.success && response.data) {
      detectionResult.value = response.data;
      resultImage.value = getFullUrl(response.data.result_image_url);
      detectionStatus.value = "检测完成";
      ElMessage.success("分类完成");
    } else {
      ElMessage.error(response.message || "分类失败");
    }
  } catch (error) {
    console.error("分类错误:", error);
    ElMessage.error("分类失败，请稍后重试");
  } finally {
    loading.close();
  }
};

const viewReport = () => {
  ElMessage.info("诊断报告功能正在接入中。");
};

const currentPredictions = computed(() => topPredictions.value || []);
</script>

<style scoped>
.detection-page {
  width: 100%;
  position: relative;
  padding-bottom: 30px;
}

.page-header {
  margin-bottom: 28px;
}

.page-label {
  display: inline-flex;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(124, 92, 255, 0.18);
  color: var(--primary-color);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 14px;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.05;
  margin-bottom: 14px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 680px;
  line-height: 1.8;
}

.main-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
}

.left-panel {
  width: 320px;
}

/* 抵消全局 .content 的左内边距，使左侧面板更靠左 */
/* previously used negative offset removed so left-panel stays inside white content area */

.mode-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
}

/* Viewer: vertical image frames for original and result */
.viewer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.viewer-pane {
  background: var(--card-bg);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 18px;
  box-shadow: var(--card-shadow);
}

.viewer-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.viewer-content.image-box {
  width: 100%;
  height: 420px;
  border-radius: 12px;
  background: var(--panel-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.viewer-content.image-box img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.placeholder {
  color: var(--text-secondary);
  font-size: 14px;
}

.mode-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
}

.mode-item:hover {
  background: var(--primary-light);
}

.mode-item.active {
  background: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
}

.mode-icon {
  font-size: 18px;
}

.mode-label {
  font-size: 14px;
}

.upload-card,
.info-card {
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 26px;
  box-shadow: var(--card-shadow);
}

.upload-card {
  padding: 32px;
}

.upload-card-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.upload-card-desc {
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 22px;
}

.upload-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.file-input {
  display: none;
}

.upload-tip {
  color: var(--text-secondary);
  font-size: 13px;
}

.info-cards {
  display: grid;
  gap: 20px;
}

.small-card {
  padding: 24px;
}

.info-card-heading,
.detail-title,
.summary-title {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.model-select {
  width: 100%;
}

.tip-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
  color: var(--text-secondary);
}

.tip-list li::before {
  content: "●";
  color: var(--primary-color);
  display: inline-block;
  width: 16px;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.summary-card {
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 26px;
  box-shadow: var(--card-shadow);
}

.summary-emphasis {
  background: linear-gradient(
    180deg,
    rgba(124, 92, 255, 0.18),
    rgba(57, 217, 201, 0.14)
  );
}

.summary-title {
  margin-bottom: 12px;
}

.summary-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.summary-note {
  color: var(--text-secondary);
  font-size: 14px;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 96px;
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.risk-high {
  background: rgba(255, 111, 134, 0.18);
  color: #ff6f86;
}

.risk-medium {
  background: rgba(255, 195, 0, 0.16);
  color: #fbbf24;
}

.risk-low {
  background: rgba(86, 227, 159, 0.18);
  color: #38bdf8;
}

.risk-unknown {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.result-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.85fr);
  gap: 24px;
}

.image-panel,
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-panel {
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
  padding: 26px;
  box-shadow: var(--card-shadow);
}

.image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  color: var(--text-secondary);
}

.image-preview {
  border-radius: 24px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.03);
  min-height: 420px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.image-footer {
  display: flex;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-card {
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  box-shadow: var(--card-shadow);
}

.detail-title {
  margin-bottom: 16px;
}

.prediction-list {
  display: grid;
  gap: 14px;
}

.prediction-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.prediction-label {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.prediction-subtext {
  color: var(--text-secondary);
  font-size: 13px;
}

.prediction-score {
  font-size: 15px;
  font-weight: 700;
  color: var(--secondary-color);
}

.suggestion-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.suggestion-text {
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 20px;
}

.action-footer {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.empty-state {
  color: var(--text-secondary);
  padding: 14px 0;
}

@media (max-width: 1080px) {
  .upload-panel,
  .result-grid,
  .result-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .page-title {
    font-size: 28px;
  }

  .image-preview {
    min-height: 260px;
  }
}
</style>
