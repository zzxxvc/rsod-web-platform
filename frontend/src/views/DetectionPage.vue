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
            <div class="info-card small-card">
              <div class="info-card-heading">当前模型</div>
              <div class="model-name">YOLOv11n.pt</div>
            </div>
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
        <!-- 图片预览弹窗 -->
        <el-dialog
          v-model="previewVisible"
          :title="previewTitle"
          width="80%"
          class="image-preview-dialog"
          destroy-on-close
        >
          <div class="preview-container">
            <div class="preview-image-wrapper">
              <img :src="previewImage" alt="预览图片" class="preview-image" />
            </div>
            <div class="preview-info" v-if="previewInfo">
              <h4>{{ previewInfo.filename }}</h4>
              <p><strong>检测结果：</strong>{{ previewInfo.topLabel }}</p>
              <p><strong>置信度：</strong>{{ previewInfo.topConfidence }}</p>
            </div>
          </div>
        </el-dialog>

        <!-- 批量模式结果展示 -->
        <section class="batch-results" v-if="activeMode === 'batch' && batchResults.length">
          <div class="batch-header">
            <h3>批量检测结果</h3>
            <span class="batch-count">共 {{ batchResults.length }} 张图片</span>
          </div>
          <div class="batch-grid">
            <div
              v-for="(item, index) in batchResults"
              :key="index"
              class="batch-item"
              :class="{ active: selectedBatchIndex === index }"
            >
              <div class="batch-item-images">
                <div class="batch-original" @click="openPreview(item, 'original')">
                  <img :src="item.originalUrl" :alt="'原图' + (index + 1)" />
                  <div class="batch-item-overlay">查看原图</div>
                </div>
                <div class="batch-result" @click="openPreview(item, 'result')">
                  <img :src="item.resultUrl" :alt="'结果' + (index + 1)" />
                  <div class="batch-item-overlay">查看结果</div>
                </div>
              </div>
              <div class="batch-item-info" @click="selectBatchResult(index)">
                <div class="batch-item-name">{{ item.filename }}</div>
                <div class="batch-item-label">{{ item.topLabel }}</div>
                <div class="batch-item-confidence">{{ item.topConfidence }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- 实时检测展示 -->
        <section class="live-detection" v-if="activeMode === 'live'">
          <div class="live-header">
            <h3>实时检测</h3>
            <div class="live-controls">
              <el-button
                v-if="!isLiveRunning"
                type="success"
                size="large"
                @click="startLiveDetection"
              >
                开始检测
              </el-button>
              <el-button
                v-else
                type="danger"
                size="large"
                @click="stopLiveDetection"
              >
                停止检测
              </el-button>
              <el-button
                v-if="isLiveRunning && liveHighRiskTargets.length > 0"
                type="warning"
                size="large"
                @click="clearHighRiskTargets"
              >
                清空高风险记录
              </el-button>
            </div>
          </div>

          <!-- 摄像头与结果并排展示 -->
          <div class="live-main-content">
            <!-- 摄像头画面 -->
            <div class="live-viewer">
              <div class="viewer-header">
                <span class="viewer-title">摄像头画面</span>
                <span v-if="isLiveRunning" class="live-indicator">
                  <span class="live-dot"></span>
                  实时检测中
                </span>
              </div>
              <div class="live-video-container">
                <video
                  ref="liveVideo"
                  class="live-video"
                  autoplay
                  muted
                  playsinline
                ></video>
                <canvas
                  ref="liveCanvas"
                  class="live-canvas"
                ></canvas>
                <div v-if="!isLiveRunning" class="live-overlay">
                  <div class="live-overlay-text">点击"开始检测"以启动摄像头</div>
                </div>
              </div>
            </div>

            <!-- 当前检测结果 -->
            <div class="live-result-panel">
              <!-- Results画面 -->
              <div class="viewer-header">
                <span class="viewer-title">检测结果画面</span>
              </div>
              <div class="result-image-container">
                <template v-if="liveCurrentCapture">
                  <img :src="liveCurrentCapture" alt="检测结果" class="result-image" />
                </template>
                <template v-else>
                  <div class="result-placeholder">
                    <el-icon :size="48" class="placeholder-icon"><ImageIcon /></el-icon>
                    <p>等待检测中...</p>
                  </div>
                </template>
              </div>

              <!-- 详细信息卡片 -->
              <div class="live-detail-cards">
                <!-- 当前结论 -->
                <div class="detail-card-small">
                  <div class="detail-card-title">当前结论</div>
                  <div class="detail-card-value">
                    {{ liveTopResult?.class_name || '未检测' }}
                  </div>
                </div>

                <!-- 风险评估 -->
                <div class="detail-card-small">
                  <div class="detail-card-title">风险评估</div>
                  <div class="detail-card-value">
                    <span :class="riskLevelClass">{{ riskLevelText }}</span>
                  </div>
                </div>

                <!-- 分析耗时 -->
                <div class="detail-card-small">
                  <div class="detail-card-title">分析耗时</div>
                  <div class="detail-card-value">{{ liveAnalysisTime }}ms</div>
                </div>
              </div>

              <!-- 检测结果列表 -->
              <div class="live-results-section">
                <div class="section-header">
                  <span class="section-title">检测目标列表</span>
                  <span class="result-count">共 {{ liveResults.length }} 个</span>
                </div>
                <div class="live-results-content">
                  <div v-if="liveResults.length > 0" class="live-results-list">
                    <div
                      v-for="(result, index) in liveResults"
                      :key="index"
                      class="live-result-item"
                      :class="{ 'high-risk': result.confidence >= 0.8 }"
                    >
                      <span class="result-label">{{ result.class_name }}</span>
                      <span class="result-confidence">
                        {{ (result.confidence * 100).toFixed(1) }}%
                      </span>
                      <span v-if="result.confidence >= 0.8" class="risk-badge">高风险</span>
                    </div>
                  </div>
                  <div v-else class="empty-results">
                    <el-icon :size="32" class="empty-icon"><Search /></el-icon>
                    <p>暂无检测结果</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 检测统计数据 -->
          <div class="live-stats">
            <div class="stat-item">
              <span class="stat-label">帧率</span>
              <span class="stat-value">{{ liveFps }} FPS</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已检测</span>
              <span class="stat-value">{{ liveFrameCount }} 帧</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">当前目标</span>
              <span class="stat-value">{{ liveResults.length }} 个</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">高风险记录</span>
              <span class="stat-value highlight">{{ liveHighRiskTargets.length }} 条</span>
            </div>
          </div>

          <!-- 高风险目标记录 -->
          <div class="high-risk-panel" v-if="liveHighRiskTargets.length > 0">
            <div class="panel-header">
              <h4>
                <el-icon class="warning-icon"><AlertTriangle /></el-icon>
                高风险目标记录
              </h4>
              <span class="panel-desc">置信度 ≥ 80% 的检测目标（每种分类只保留最高置信度）</span>
            </div>
            <div class="high-risk-grid">
              <div
                v-for="(target, index) in liveHighRiskTargets"
                :key="target.class_name"
                class="high-risk-card"
              >
                <div class="card-image">
                  <img :src="target.imageUrl" :alt="target.class_name" />
                </div>
                <div class="card-info">
                  <div class="card-label">{{ target.class_name }}</div>
                  <div class="card-confidence">置信度: {{ (target.confidence * 100).toFixed(1) }}%</div>
                  <div class="card-time">{{ target.timestamp }}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 单图模式展示 -->
        <div class="viewer" v-else>
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
import {
  detectSingleImage,
  buildDetectionFormData,
  DETECTION_SINGLE_URL,
} from "../api/detection";
import { staticUrl, authHeaders } from "../config/api";

const selectedModel = ref("DermNet-v1");
const detectionResult = ref(null);
const detectionResults = ref([]); // for batch
const batchResults = ref([]); // 存储所有批量检测结果
const selectedBatchIndex = ref(0); // 当前选中的批量结果索引
const originalFilename = ref("未上传图像");
const fileInput = ref(null);
const activeMode = ref("single");

// 图片预览相关
const previewVisible = ref(false);
const previewImage = ref("");
const previewTitle = ref("");
const previewInfo = ref(null);

// 实时检测相关
const liveStream = ref(null); // 摄像头流
const liveVideo = ref(null); // 视频元素引用
const liveCanvas = ref(null); // Canvas 元素引用
const liveContext = ref(null); // Canvas 绘图上下文
const isLiveRunning = ref(false); // 是否正在检测
const liveResults = ref([]); // 当前帧检测结果
const liveFrameCount = ref(0); // 检测帧数
const liveFps = ref(0); // 当前帧率
const liveLastFrameTime = ref(0); // 上一帧时间戳
const liveDetectionInterval = ref(null); // 检测定时器
const liveFrameInterval = ref(16); // 帧间隔 (ms)，约60fps
const liveDetecting = ref(false); // 是否正在发送检测请求
const liveHighRiskTargets = ref([]); // 高风险目标（置信度>=80%）
const liveCurrentCapture = ref(null); // 当前帧的捕获图像
const liveAnalysisTime = ref(0); // 分析耗时（毫秒）
const liveLastAnalysisTime = ref(0); // 上次分析时间

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
  // 在批量模式下使用当前选中的图片
  if (activeMode.value === "batch" && detectionResult.value) {
    return detectionResult.value?.boxes?.[0] || null;
  }
  if (!detectionResult.value?.boxes?.length) return null;
  return detectionResult.value.boxes[0];
});

const topPredictions = computed(() => {
  // 在批量模式下使用当前选中的图片
  if (activeMode.value === "batch" && detectionResult.value) {
    return detectionResult.value?.boxes?.slice(0, 3) || [];
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

// 实时检测 - 最高置信度结果
const liveTopResult = computed(() => {
  if (!liveResults.value.length) return null;
  return liveResults.value.reduce((prev, current) => {
    return current.confidence > prev.confidence ? current : prev;
  });
});

// 实时检测 - 风险等级文本
const riskLevelText = computed(() => {
  const topConfidence = liveTopResult.value?.confidence || 0;
  if (topConfidence >= 0.8) return "高风险";
  if (topConfidence >= 0.5) return "中风险";
  if (topConfidence > 0) return "低风险";
  return "未检测";
});

// 实时检测 - 风险等级样式类
const riskLevelClass = computed(() => {
  const level = riskLevelText.value;
  if (level === "高风险") return "risk-high";
  if (level === "中风险") return "risk-medium";
  if (level === "低风险") return "risk-low";
  return "risk-unknown";
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

// 启动实时检测
const startLiveDetection = async () => {
  try {
    // 1. 请求摄像头权限
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "environment" // 后置摄像头优先
      }
    });

    liveStream.value = stream;

    // 2. 将摄像头流绑定到 video 元素
    if (liveVideo.value) {
      liveVideo.value.srcObject = stream;
      await liveVideo.value.play();
    }

    // 3. 初始化 Canvas
    if (liveCanvas.value && liveVideo.value) {
      liveCanvas.value.width = liveVideo.value.videoWidth || 640;
      liveCanvas.value.height = liveVideo.value.videoHeight || 480;
      liveContext.value = liveCanvas.value.getContext("2d");
    }

    // 4. 开始检测循环
    isLiveRunning.value = true;
    liveFrameCount.value = 0;
    liveLastFrameTime.value = performance.now();
    liveResults.value = [];

    // 5. 启动帧捕获循环
    requestAnimationFrame(captureFrame);

    ElMessage.success("实时检测已启动");
  } catch (error) {
    console.error("启动摄像头失败:", error);
    ElMessage.error(
      error.name === "NotAllowedError"
        ? "请允许访问摄像头权限"
        : "无法访问摄像头：" + error.message
    );
  }
};

// 停止实时检测
const stopLiveDetection = () => {
  isLiveRunning.value = false;

  // 停止摄像头流
  if (liveStream.value) {
    liveStream.value.getTracks().forEach((track) => track.stop());
    liveStream.value = null;
  }

  // 清除检测定时器
  if (liveDetectionInterval.value) {
    clearInterval(liveDetectionInterval.value);
    liveDetectionInterval.value = null;
  }

  // 清除 Canvas
  if (liveContext.value && liveCanvas.value) {
    liveContext.value.clearRect(
      0,
      0,
      liveCanvas.value.width,
      liveCanvas.value.height
    );
  }

  ElMessage.info("实时检测已停止");
};

// 捕获并处理每一帧
const captureFrame = async () => {
  if (!isLiveRunning.value) return;

  try {
    // 1. 计算帧率
    const now = performance.now();
    const elapsed = now - liveLastFrameTime.value;
    liveFps.value = Math.round(1000 / elapsed);
    liveLastFrameTime.value = now;

    // 2. 绘制视频帧到 Canvas
    if (liveContext.value && liveVideo.value) {
      liveContext.value.drawImage(
        liveVideo.value,
        0,
        0,
        liveCanvas.value.width,
        liveCanvas.value.height
      );
    }

    // 3. 每隔一定帧数进行一次检测 (节流)
    if (liveFrameCount.value % 10 === 0 && !liveDetecting.value) {
      await performLiveDetection();
    }

    liveFrameCount.value++;

    // 4. 继续下一帧
    requestAnimationFrame(captureFrame);
  } catch (error) {
    console.error("帧捕获错误:", error);
  }
};

// 执行实时检测
const performLiveDetection = async () => {
  if (liveDetecting.value || !liveCanvas.value) return;

  liveDetecting.value = true;
  const startTime = performance.now(); // 记录开始时间

  try {
    // 1. 将 Canvas 转换为 Blob
    const blob = await new Promise((resolve) => {
      liveCanvas.value.toBlob(resolve, "image/jpeg", 0.8);
    });

    if (!blob) {
      liveDetecting.value = false;
      return;
    }

    // 2. 创建 FormData
    const formData = buildDetectionFormData(blob, selectedModel.value);

    // 3. 调用检测 API
    const response = await fetch(DETECTION_SINGLE_URL, {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    });

    // 计算分析耗时
    const endTime = performance.now();
    liveAnalysisTime.value = Math.round(endTime - startTime);

    if (!response.ok) {
      throw new Error(`检测失败: ${response.status}`);
    }

    const payload = await response.json();
    const boxes = payload.data?.boxes ?? payload.boxes ?? [];

    // 4. 更新检测结果
    if (boxes.length > 0) {
      liveResults.value = boxes;
      drawDetectionResults(boxes);

      // 5. 处理高风险目标（置信度 >= 80%）
      await processHighRiskTargets(boxes);
    } else {
      liveResults.value = [];
    }
  } catch (error) {
    console.error("实时检测错误:", error);
    // 检测失败时清空结果
    liveResults.value = [];
  } finally {
    liveDetecting.value = false;
  }
};

// 处理高风险目标
const processHighRiskTargets = async (boxes) => {
  if (!liveCanvas.value) return;

  // 获取当前帧的图像
  const imageUrl = liveCanvas.value.toDataURL("image/jpeg", 0.8);
  liveCurrentCapture.value = imageUrl;

  // 筛选置信度 >= 80% 的目标
  const highRiskBoxes = boxes.filter(box => box.confidence >= 0.8);

  // 对每个高风险目标进行处理
  for (const box of highRiskBoxes) {
    const existingIndex = liveHighRiskTargets.value.findIndex(
      target => target.class_name === box.class_name
    );

    if (existingIndex >= 0) {
      // 如果已存在该类别的记录，只保留置信度更高的
      if (box.confidence > liveHighRiskTargets.value[existingIndex].confidence) {
        liveHighRiskTargets.value[existingIndex] = {
          class_name: box.class_name,
          confidence: box.confidence,
          imageUrl: imageUrl,
          timestamp: new Date().toLocaleString('zh-CN')
        };
      }
    } else {
      // 如果不存在该类别的记录，添加新记录
      liveHighRiskTargets.value.push({
        class_name: box.class_name,
        confidence: box.confidence,
        imageUrl: imageUrl,
        timestamp: new Date().toLocaleString('zh-CN')
      });
    }
  }
};

// 清空高风险目标记录
const clearHighRiskTargets = () => {
  liveHighRiskTargets.value = [];
  ElMessage.info("高风险记录已清空");
};

// 绘制检测结果到 Canvas
const drawDetectionResults = (boxes) => {
  if (!liveContext.value || !liveCanvas.value) return;

  const canvas = liveCanvas.value;
  const ctx = liveContext.value;

  // 重新绘制视频帧（清除之前的绘制）
  ctx.drawImage(
    liveVideo.value,
    0,
    0,
    canvas.width,
    canvas.height
  );

  // 绘制每个检测框
  boxes.forEach((box, index) => {
    const [x1, y1, x2, y2] = box.xyxy;
    const confidence = box.confidence;
    const className = box.class_name;

    // 颜色映射（为不同类别分配不同颜色）
    const colors = [
      "#FF6B6B",
      "#4ECDC4",
      "#45B7D1",
      "#FFA07A",
      "#98D8C8"
    ];
    const color = colors[index % colors.length];

    // 绘制边界框
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    // 绘制标签背景
    ctx.fillStyle = color;
    const label = `${className} ${(confidence * 100).toFixed(1)}%`;
    ctx.font = "bold 16px Arial";
    const textWidth = ctx.measureText(label).width;
    ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);

    // 绘制标签文字
    ctx.fillStyle = "#FFFFFF";
    ctx.fillText(label, x1 + 5, y1 - 7);
  });
};

const getFullUrl = staticUrl;

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
  const loading = ElLoading.service({
    lock: true,
    text: `正在检测 ${files.length} 张图片...`,
    background: "rgba(0, 0, 0, 0.75)",
  });

  detectionResults.value = [];
  batchResults.value = [];
  selectedBatchIndex.value = 0;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    try {
      const response = await detectSingleImage(file, selectedModel.value);
      if (response.success && response.data) {
        detectionResults.value.push(response.data);

        // 提取第一张检测结果的标签和置信度
        const topBox = response.data.boxes?.[0];
        batchResults.value.push({
          originalUrl: URL.createObjectURL(file),
          resultUrl: getFullUrl(response.data.result_image_url),
          filename: file.name,
          topLabel: topBox?.class_name || "未知",
          topConfidence: topBox ? `${(topBox.confidence * 100).toFixed(1)}%` : "0%",
          data: response.data
        });
      }
    } catch (err) {
      console.error(`批量检测第 ${i + 1} 张出错`, err);
    }
  }

  loading.close();

  // 显示第一张结果为预览
  if (batchResults.value[0]) {
    selectBatchResult(0);
    detectionStatus.value = "批量检测完成";
    ElMessage.success(`批量检测完成，共 ${batchResults.value.length} 张图片`);
  }
};

// 选择批量结果中的某一项
const selectBatchResult = (index) => {
  selectedBatchIndex.value = index;
  const item = batchResults.value[index];
  if (item) {
    detectionResult.value = item.data;
    originalImage.value = item.originalUrl;
    resultImage.value = item.resultUrl;
    originalFilename.value = item.filename;
    detectionStatus.value = item.topLabel;
  }
};

// 打开图片预览弹窗
const openPreview = (item, type) => {
  if (type === 'original') {
    previewImage.value = item.originalUrl;
    previewTitle.value = `原图预览 - ${item.filename}`;
  } else {
    previewImage.value = item.resultUrl;
    previewTitle.value = `检测结果预览 - ${item.filename}`;
  }
  previewInfo.value = {
    filename: item.filename,
    topLabel: item.topLabel,
    topConfidence: item.topConfidence
  };
  previewVisible.value = true;
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "正在分析图像...",
    background: "rgba(0, 0, 0, 0.75)",
  });

  try {
    originalImage.value = URL.createObjectURL(file);
    const response = await detectSingleImage(file, selectedModel.value);

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

/* 批量检测结果样式 */
.batch-results {
  background: var(--card-bg);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--card-shadow);
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--panel-border);
}

.batch-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.batch-count {
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--primary-light);
  padding: 6px 14px;
  border-radius: 20px;
}

.batch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.batch-grid::-webkit-scrollbar {
  width: 6px;
}

.batch-grid::-webkit-scrollbar-track {
  background: var(--panel-bg);
  border-radius: 3px;
}

.batch-grid::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 3px;
}

.batch-item {
  background: var(--panel-bg);
  border: 2px solid transparent;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.batch-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.batch-item.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.2);
}

.batch-item-images {
  display: flex;
  gap: 2px;
  height: 160px;
}

.batch-original,
.batch-result {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.batch-original::after,
.batch-result::after {
  content: attr(data-label);
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: white;
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 6px;
  border-radius: 4px;
}

.batch-original img,
.batch-result img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.batch-item-info {
  padding: 12px;
  background: var(--card-bg);
}

.batch-item-name {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-item-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.batch-item-confidence {
  font-size: 13px;
  color: var(--secondary-color);
  font-weight: 600;
}

/* 图片预览弹窗样式 */
.preview-container {
  display: flex;
  gap: 24px;
  max-height: 70vh;
}

.preview-image-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--panel-bg);
  border-radius: 12px;
  overflow: hidden;
  min-height: 400px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.preview-info {
  width: 280px;
  flex-shrink: 0;
  background: var(--card-bg);
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  padding: 20px;
}

.preview-info h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--panel-border);
  word-break: break-all;
}

.preview-info p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.6;
}

.preview-info strong {
  color: var(--text-primary);
}

/* 批量图片悬停效果 */
.batch-original,
.batch-result {
  position: relative;
  cursor: pointer;
  overflow: hidden;
}

.batch-item-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(124, 92, 255, 0.8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.batch-original:hover .batch-item-overlay,
.batch-result:hover .batch-item-overlay {
  opacity: 1;
}

.batch-item-info {
  cursor: pointer;
}

.batch-item-info:hover {
  background: rgba(124, 92, 255, 0.1);
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

  .preview-container {
    flex-direction: column;
  }

  .preview-info {
    width: 100%;
  }
}

/* 图片预览对话框样式 */
:deep(.image-preview-dialog) {
  max-width: 1400px;
}

/* 实时检测样式 */
.live-detection {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.live-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
}

.live-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.live-controls {
  display: flex;
  gap: 12px;
}

/* 摄像头与结果并排展示 */
.live-main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.1);
}

.viewer-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #52c41a;
  font-weight: 500;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #52c41a;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.result-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.live-viewer {
  display: flex;
  flex-direction: column;
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.live-result-panel {
  display: flex;
  flex-direction: column;
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

/* Results画面容器 */
.result-image-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.result-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  gap: 12px;
}

.placeholder-icon {
  opacity: 0.5;
}

/* 详细信息卡片容器 */
.live-detail-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

/* 小卡片 - 边框比普通小5px (11px vs 16px) */
.detail-card-small {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 11px;
  padding: 12px;
  text-align: center;
}

.detail-card-title {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.detail-card-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

/* 检测结果区域 */
.live-results-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.live-results-content {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
}

.empty-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  margin-bottom: 12px;
  opacity: 0.5;
}

.live-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-value.highlight {
  color: #ff6b6b;
}

/* 风险等级颜色 */
.risk-high {
  color: #ff6b6b;
}

.risk-medium {
  color: #ffc107;
}

.risk-low {
  color: #52c41a;
}

.risk-unknown {
  color: var(--text-secondary);
}

.live-video-container {
  flex: 1;
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  overflow: hidden;
}

.live-video {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: translate(-50%, -50%);
}

.live-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.live-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 500;
}

.live-overlay-text {
  padding: 20px 30px;
  background: rgba(124, 92, 255, 0.8);
  border-radius: 12px;
}

.live-results {
  background: var(--card-bg);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--card-shadow);
}

.live-results h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.live-results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.live-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 10px;
}

.result-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-confidence {
  font-size: 14px;
  font-weight: 700;
  color: var(--secondary-color);
}

/* 高风险结果样式 */
.live-result-item.high-risk {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
}

.risk-badge {
  padding: 4px 10px;
  background: #ff6b6b;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
}

/* 高风险目标面板 */
.high-risk-panel {
  background: var(--card-bg);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--card-shadow);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h4 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.warning-icon {
  color: #ff6b6b;
}

.panel-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.high-risk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.high-risk-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: rgba(255, 107, 107, 0.05);
  border: 1px solid rgba(255, 107, 107, 0.2);
  border-radius: 12px;
}

.card-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.card-confidence {
  font-size: 13px;
  color: #ff6b6b;
  font-weight: 600;
}

.card-time {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 1080px) {
  .live-main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .live-header {
    flex-direction: column;
    gap: 16px;
  }

  .live-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .high-risk-grid {
    grid-template-columns: 1fr;
  }
}
</style>

:deep(.image-preview-dialog .el-dialog__header) {
  border-bottom: 1px solid var(--panel-border);
  padding: 16px 20px;
}

:deep(.image-preview-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

:deep(.image-preview-dialog .el-dialog__body) {
  padding: 20px;
}

@media (max-width: 1080px) {
  :deep(.preview-container) {
    flex-direction: column;
  }

  :deep(.preview-info) {
    width: 100%;
  }
}
