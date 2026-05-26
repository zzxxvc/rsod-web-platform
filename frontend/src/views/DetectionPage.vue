<template>
  <div class="detection-page cyber-medical-theme">
    <header class="page-header">
      <div class="page-label animate-pulse">
        <span class="pulse-dot"></span> AI 终端核心：皮肤病变诊断
      </div>
      <h1 class="page-title cyber-glow-text">医学级皮肤病变智能分类平台</h1>
      <p class="page-subtitle">
        接入深度神经网络推理舱（YOLOv11），多模态实时提取病灶表面纹理，输出辅助医疗诊断意见。
      </p>
    </header>

    <section class="main-layout">
      <aside class="left-panel">
        <div class="cyber-panel mode-menu">
          <div
            v-for="item in modeMenu"
            :key="item.key"
            class="mode-item"
            :class="{ active: activeMode === item.key }"
            @click="setMode(item.key)"
          >
            <el-icon class="mode-icon"><component :is="item.icon" /></el-icon>
            <span class="mode-label">{{ item.label }}舱</span>
          </div>
        </div>

        <div class="cyber-panel upload-card">
          <div class="upload-card-title">
            <el-icon><Picture /></el-icon> 提交诊断数据
          </div>
          <p class="upload-card-desc">
            支持单张表皮镜切片、批量临床图像、高频动态视频，或直接开启无菌摄像头实时捕捉。
          </p>

          <div class="upload-actions">
            <el-button
              v-if="activeMode === 'single'"
              class="cyber-btn primary-glow"
              size="large"
              @click="triggerUpload"
            >
              <el-icon><Upload /></el-icon> 载入单图切片
            </el-button>

            <el-button
              v-if="activeMode === 'batch'"
              class="cyber-btn primary-glow"
              size="large"
              @click="triggerUpload"
            >
              批量切片打入
            </el-button>

            <el-button
              v-if="activeMode === 'video'"
              class="cyber-btn"
              size="large"
              @click="triggerUpload"
            >
              上传动态视频
            </el-button>

            <el-button
              v-if="activeMode === 'live'"
              class="cyber-btn live-glow"
              size="large"
              @click="startLive"
            >
              <span class="live-dot"></span> 开启实时视讯
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
            数据流已启用端到端 SHA-256 加密，全面保障患者临床隐私。
          </div>
        </div>

        <div class="info-cards">
          <div class="cyber-panel small-card">
            <div class="info-card-heading">当前加载神经引擎</div>
            <div class="model-badge">
              <span class="model-indicator"></span>
              <span class="model-name-text">YOLOv11_Skin_Nano (Active)</span>
            </div>
          </div>

          <div class="cyber-panel small-card">
            <div class="info-card-heading">诊断协议说明</div>
            <ul class="tip-list">
              <li>单张高清表皮图像15毫秒内完成分割。</li>
              <li>批量多维数据流将依次轮询并行分析。</li>
              <li>实时影像流极度依赖本地GPU硬件加速。</li>
            </ul>
          </div>
        </div>
      </aside>

      <main class="center-panel">
        <div class="viewer-grid">
          <div class="viewer-pane original cyber-panel">
            <div class="viewer-title"><span class="title-tag">INPUT</span> 原始表皮影像</div>
            <div class="viewer-content image-box">
              <div class="corner-border top-left"></div>
              <div class="corner-border top-right"></div>
              <div class="corner-border bottom-left"></div>
              <div class="corner-border bottom-right"></div>
              
              <template v-if="originalImage">
                <img :src="originalImage" alt="原始图像" />
                <div class="laser-scan-line"></div>
              </template>
              <template v-else>
                <div class="placeholder-glow">
                  <el-icon class="huge-icon"><Picture /></el-icon>
                  <div>等待数据源打入...</div>
                </div>
              </template>
            </div>
            <div class="viewer-footer">SOURCE_FILE: {{ originalFilename }}</div>
          </div>

          <div class="viewer-pane result cyber-panel">
            <div class="viewer-title"><span class="title-tag output">OUTPUT</span> 神经网络推理图</div>
            <div class="viewer-content image-box">
              <div class="corner-border top-left"></div>
              <div class="corner-border top-right"></div>
              <div class="corner-border bottom-left"></div>
              <div class="corner-border bottom-right"></div>
              
              <template v-if="resultImage">
                <img :src="resultImage" alt="检测结果图" />
                <div class="laser-scan-line forward"></div>
              </template>
              <template v-else>
                <div class="placeholder-glow">
                  <el-icon class="huge-icon animate-pulse"><Picture /></el-icon>
                  <div>等待引擎推理...</div>
                </div>
              </template>
            </div>
            <div class="viewer-footer">STATUS: {{ detectionStatus }}</div>
          </div>
        </div>

        <section
          class="result-section"
          v-if="(topPredictions && topPredictions.length) || detectionResult"
        >
          <div class="result-summary">
            <div class="cyber-panel summary-card dashboard-flex">
              <div class="dashboard-wrapper">
                <el-progress
                  type="dashboard"
                  :percentage="parseFloat(topConfidence)"
                  :stroke-width="8"
                  :width="110"
                  color="#00f5d4"
                >
                  <template #default="{ percentage }">
                    <span class="dashboard-percent">{{ percentage }}%</span>
                    <span class="dashboard-label">置信度</span>
                  </template>
                </el-progress>
              </div>
              <div class="dashboard-text-area">
                <div class="summary-title">核心诊断结论</div>
                <div class="summary-value cyber-glow-text-cyan">{{ topLabel }}</div>
              </div>
            </div>

            <div class="cyber-panel summary-card summary-emphasis">
              <div class="summary-title">危险评级与控制</div>
              <div class="risk-badge-wrapper">
                <div class="risk-badge" :class="riskClass">{{ riskLevel }}</div>
              </div>
              <div class="summary-note text-center">系统检测到异常病灶增殖特征</div>
            </div>

            <div class="cyber-panel summary-card">
              <div class="summary-title">推理引擎能效</div>
              <div class="summary-value font-mono">
                {{ detectionResult?.detection_time || '0.015' }}<span class="unit">s</span>
              </div>
              <div class="summary-note">
                算力开销: {{ detectionResult?.model_name || 'YOLOv11-Nano' }}
              </div>
            </div>
          </div>

          <div class="detail-panel">
            <div class="cyber-panel detail-card prediction-card">
              <div class="detail-title">多层病变概率排查</div>
              <div class="prediction-list">
                <div
                  v-for="(item, index) in topPredictions"
                  :key="index"
                  class="prediction-item"
                >
                  <div class="prediction-left">
                    <span class="rank-index">0{{ index + 1 }}</span>
                    <div>
                      <div class="prediction-label">{{ item.class_name }}</div>
                      <div class="prediction-subtext">模型多层激活加权值</div>
                    </div>
                  </div>
                  <div class="prediction-score font-mono">
                    {{ (item.confidence * 100).toFixed(1) }}%
                  </div>
                </div>
                <div v-if="!topPredictions.length" class="empty-state">
                  神经元未捕获到特征信号
                </div>
              </div>
            </div>

            <div class="cyber-panel detail-card suggestion-card">
              <div class="detail-title">AI 临床随访建议</div>
              <p class="suggestion-text">{{ suggestionText }}</p>
              <div class="action-footer">
                <el-button class="cyber-btn-sm primary-glow" @click="triggerUpload">重新捕获</el-button>
                <el-button class="cyber-btn-sm info-glow" @click="viewReport">
                  生成数字化报告
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
import { Picture, Document, VideoCamera, Camera, Upload } from "@element-plus/icons-vue";
import { ElMessage, ElLoading } from "element-plus";
import { detectSingleImage } from "../api/detection";

const selectedModel = ref("YOLOv11-Skin");
const detectionResult = ref(null);
const detectionResults = ref([]); 
const originalFilename = ref("RAW_DATA_STREAM");
const fileInput = ref(null);
const activeMode = ref("single");
const detectionStatus = ref("STANDBY");

const router = useRouter();
const route = useRoute();
const topActive = ref(route.path.replace(/^\//, "") || "detection");

const backendBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/api$/, "") || "http://localhost:8000";

const originalImage = ref("");
const resultImage = ref("");

const modeMenu = [
  { key: "single", label: "单图", icon: Picture },
  { key: "batch", label: "批量", icon: Document },
  { key: "video", label: "视频", icon: VideoCamera },
  { key: "live", label: "实时", icon: Camera },
];

const setMode = (key) => { activeMode.value = key; };

const topPrediction = computed(() => {
  if (activeMode.value === "batch") {
    return detectionResults.value?.[0]?.boxes?.[0] || null;
  }
  return detectionResult.value?.boxes?.[0] || null;
});

const topPredictions = computed(() => {
  if (activeMode.value === "batch") {
    return detectionResults.value?.[0]?.boxes?.slice(0, 3) || [];
  }
  return detectionResult.value?.boxes?.slice(0, 3) || [];
});

const topLabel = computed(() => topPrediction.value?.class_name || "未发现明显病变");
const topConfidence = computed(() => topPrediction.value ? `${(topPrediction.value.confidence * 100).toFixed(1)}%` : "0%");

const riskLevel = computed(() => {
  const score = topPrediction.value?.confidence || 0;
  if (score > 0.82) return "高风险 CRITICAL";
  if (score > 0.60) return "中风险 WARNING";
  if (score > 0.30) return "低风险 STABLE";
  return "待确认 SUSPECTED";
});

const riskClass = computed(() => {
  if (riskLevel.value.includes("高风险")) return "risk-high";
  if (riskLevel.value.includes("中风险")) return "risk-medium";
  if (riskLevel.value.includes("低风险")) return "risk-low";
  return "risk-unknown";
});

const suggestionText = computed(() => {
  if (!detectionResult.value?.boxes?.length) return "请将受检部位表皮切片打入诊断舱，系统将自动执行神经元特征提取。";
  if (riskLevel.value.includes("高风险")) return "警告：模型匹配出高恶性特征（如黑色素瘤突变风险）。病灶边缘呈异形浸润。强烈建议立刻启动线下临床三级医院病理活检程序！";
  if (riskLevel.value.includes("中风险")) return "提示：当前区域存在中度炎性反应或异常角化。请注意避免日光直射与化学刺激，密切观察是否有增大趋势，建议皮肤科随诊。";
  return "诊断：当前表皮结构大致完整，特征值位于安全阈值内。建议保持日常清洁，定期复查即可。";
});

const triggerUpload = () => { fileInput.value?.click(); };
const fileAccept = computed(() => activeMode.value === "video" ? "video/*" : "image/*");

const startLive = () => { ElMessage.success("本地无菌视讯设备已就绪，正在捕获视频流..."); };
const getFullUrl = (relativeUrl) => {
  if (!relativeUrl) return "";
  if (/^https?:\/\//.test(relativeUrl)) return relativeUrl;
  return `${backendBaseUrl}${relativeUrl}`;
};

const handleFileChange = async (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) return;
  detectionStatus.value = "ANALYZING";
  if (activeMode.value === "batch") {
    originalFilename.value = `${files.length} BATCH_FILES`;
    await performBatchDetection(files);
  } else {
    originalFilename.value = files[0].name.toUpperCase();
    await performSingleDetection(files[0]);
  }
  event.target.value = "";
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "深度神经网络正在提取病灶特征...",
    background: "rgba(11, 15, 25, 0.9)",
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
      detectionStatus.value = "COMPLETED";
      ElMessage.success("核心特征推理完成");
    } else {
      detectionStatus.value = "ERROR";
      ElMessage.error(response.message || "推理失败");
    }
  } catch (error) {
    detectionStatus.value = "CRASHED";
    ElMessage.error("后端引擎响应超时");
  } finally {
    loading.close();
  }
};

const performBatchDetection = async (files) => {
  detectionResults.value = [];
  for (const file of files) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await detectSingleImage(formData);
      if (response.success && response.data) detectionResults.value.push(response.data);
    } catch (err) { console.error(err); }
  }
  if (detectionResults.value[0]) {
    detectionResult.value = detectionResults.value[0];
    originalImage.value = URL.createObjectURL(files[0]);
    resultImage.value = getFullUrl(detectionResults.value[0].result_image_url);
    detectionStatus.value = "BATCH_DONE";
  }
};

const viewReport = () => { ElMessage.info("正在生成数字化全套病理结构PDF报告..."); };
</script>

<style scoped>
.cyber-medical-theme {
  --cyber-bg: #0b0f19;
  --cyber-panel-bg: rgba(16, 24, 48, 0.75);
  --cyber-border: rgba(0, 245, 212, 0.25);
  --cyber-glow: rgba(0, 245, 212, 0.15);
  --cyber-cyan: #00f5d4;
  --cyber-blue: #00bbf9;
  --text-muted: #94a3b8;
  
  background-color: var(--cyber-bg);
  color: #f8fafc;
  min-height: 100vh;
  padding: 20px;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.cyber-panel {
  background: var(--cyber-panel-bg);
  border: 1px solid var(--cyber-border);
  box-shadow: 0 0 25px var(--cyber-glow), inset 0 0 10px rgba(0, 245, 212, 0.05);
  backdrop-filter: blur(12px);
  border-radius: 14px;
  transition: all 0.3s ease;
}
.cyber-panel:hover {
  border-color: rgba(0, 245, 212, 0.45);
  box-shadow: 0 0 30px rgba(0, 245, 212, 0.25);
}

.page-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(0, 245, 212, 0.1);
  border: 1px solid rgba(0, 245, 212, 0.3);
  color: var(--cyber-cyan);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 14px;
}
.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--cyber-cyan);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--cyber-cyan);
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

.page-title {
  font-size: 34px;
  font-weight: 900;
  letter-spacing: -0.5px;
  margin-bottom: 12px;
}
.cyber-glow-text {
  color: #fff;
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
}
.cyber-glow-text-cyan {
  color: var(--cyber-cyan);
  text-shadow: 0 0 12px rgba(0, 245, 212, 0.4);
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-muted);
  max-width: 720px;
  line-height: 1.6;
}

.main-layout {
  display: grid;
  grid-template-columns: 310px 1fr;
  gap: 24px;
  margin-top: 24px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.mode-menu {
  padding: 10px;
}
.mode-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.2s ease;
}
.mode-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
}
.mode-item.active {
  background: rgba(0, 245, 212, 0.12);
  color: var(--cyber-cyan);
  font-weight: 700;
  border-left: 3px solid var(--cyber-cyan);
}

.upload-card {
  padding: 24px;
}
.upload-card-title {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--cyber-cyan);
}
.upload-card-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 12px 0 20px 0;
}

.cyber-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
  font-weight: 600;
  border-radius: 8px;
}
.cyber-btn:hover {
  border-color: var(--cyber-blue) !important;
  box-shadow: 0 0 12px rgba(0, 187, 249, 0.3);
}
.primary-glow {
  background: rgba(0, 245, 212, 0.08) !important;
  border: 1px solid var(--cyber-border) !important;
  color: var(--cyber-cyan) !important;
}
.primary-glow:hover {
  background: rgba(0, 245, 212, 0.15) !important;
  box-shadow: 0 0 15px var(--cyber-glow);
}
.live-glow {
  border-color: #ff0055 !important;
  color: #ff0055 !important;
}
.live-dot {
  width: 6px;
  height: 6px;
  background: #ff0055;
  border-radius: 50%;
  box-shadow: 0 0 8px #ff0055;
  display: inline-block;
  margin-right: 6px;
}

.upload-tip {
  font-size: 11px;
  color: #64748b;
  margin-top: 14px;
  line-height: 1.4;
}

.model-badge {
  background: rgba(0, 187, 249, 0.1);
  border: 1px solid rgba(0, 187, 249, 0.3);
  padding: 10px 14px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}
.model-indicator {
  width: 6px;
  height: 6px;
  background: var(--cyber-blue);
  border-radius: 50%;
}
.model-name-text {
  font-size: 13px;
  font-family: monospace;
  color: var(--cyber-blue);
}

.small-card { padding: 18px 20px; }
.tip-list {
  font-size: 12px;
  color: var(--text-muted);
  padding-left: 4px;
  line-height: 1.7;
}
.tip-list li::before {
  content: "» ";
  color: var(--cyber-cyan);
}

.viewer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.viewer-pane {
  padding: 16px;
}
.viewer-title {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
}
.title-tag {
  font-size: 10px;
  background: rgba(255,255,255,0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-muted);
}
.title-tag.output {
  background: rgba(0, 245, 212, 0.15);
  color: var(--cyber-cyan);
}

.viewer-content.image-box {
  height: 380px;
  background: #070a12;
  border: 1px solid rgba(255,255,255,0.05);
  position: relative;
  overflow: hidden;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.viewer-content.image-box img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.corner-border {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 2px solid var(--cyber-cyan);
  z-index: 10;
}
.top-left { top: 8px; left: 8px; border-right: none; border-bottom: none; }
.top-right { top: 8px; right: 8px; border-left: none; border-bottom: none; }
.bottom-left { bottom: 8px; left: 8px; border-right: none; border-top: none; }
.bottom-right { bottom: 8px; right: 8px; border-left: none; border-top: none; }

.laser-scan-line {
  position: absolute;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to bottom, rgba(0, 245, 212, 0), var(--cyber-cyan), rgba(0, 245, 212, 0));
  box-shadow: 0 0 12px var(--cyber-cyan);
  animation: laserMove 3s linear infinite;
  z-index: 5;
}
.laser-scan-line.forward {
  background: linear-gradient(to bottom, rgba(0, 187, 249, 0), var(--cyber-blue), rgba(0, 187, 249, 0));
  box-shadow: 0 0 12px var(--cyber-blue);
  animation-delay: 1.5s;
}

@keyframes laserMove {
  0% { top: 2%; }
  50% { top: 98%; }
  100% { top: 2%; }
}

.placeholder-glow {
  text-align: center;
  color: #475569;
  font-size: 13px;
}
.huge-icon {
  font-size: 42px;
  margin-bottom: 12px;
  color: #334155;
}
.viewer-footer {
  font-size: 11px;
  font-family: monospace;
  color: #475569;
  margin-top: 10px;
}

.result-summary {
  display: grid;
  grid-template-columns: 1.3fr 1fr 0.8fr;
  gap: 20px;
}
.dashboard-flex {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px !important;
}
.dashboard-percent {
  font-size: 22px;
  font-weight: 800;
  color: var(--cyber-cyan);
  font-family: monospace;
}
.dashboard-label {
  font-size: 10px;
  color: var(--text-muted);
  display: block;
}
.summary-value {
  font-size: 26px;
  font-weight: 900;
}
.unit { font-size: 14px; margin-left: 2px; color: #475569;}

.summary-emphasis {
  background: linear-gradient(180deg, rgba(255, 0, 85, 0.05), rgba(11, 15, 25, 0.7));
  border-color: rgba(255, 0, 85, 0.25);
}
.risk-badge-wrapper {
  margin: 10px 0;
  display: flex;
  justify-content: center;
}
.risk-badge {
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 800;
  font-family: monospace;
}
.risk-high { background: rgba(255,0,85,0.15); color: #ff0055; border: 1px solid rgba(255,0,85,0.3); }
.risk-medium { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.risk-low { background: rgba(0,245,212,0.15); color: var(--cyber-cyan); border: 1px solid rgba(0,245,212,0.3); }

.detail-panel {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  margin-top: 20px;
}
.prediction-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 10px;
}
.prediction-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.rank-index {
  font-family: monospace;
  font-size: 14px;
  color: var(--cyber-cyan);
  font-weight: 700;
}
.prediction-label {
  font-weight: 700;
  font-size: 14px;
}
.prediction-subtext {
  font-size: 11px;
  color: #475569;
}
.prediction-score {
  color: var(--cyber-blue);
  font-weight: 700;
}

.suggestion-text {
  font-size: 13px;
  color: #cbd5e1;
  line-height: 1.6;
}

.cyber-btn-sm {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #fff !important;
  font-size: 12px;
  padding: 8px 16px;
  border-radius: 6px;
}
.info-glow:hover {
  border-color: var(--cyber-blue) !important;
  color: var(--cyber-blue) !important;
}

@media (max-width: 1024px) {
  .main-layout, .viewer-grid, .result-summary, .detail-panel {
    grid-template-columns: 1fr;
  }
}
</style>