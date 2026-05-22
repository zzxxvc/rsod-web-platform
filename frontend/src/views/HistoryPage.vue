<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">诊断历史记录</h1>
      <p class="page-subtitle">
        查看皮肤病变诊断历史，定位高风险病例与复诊建议
      </p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索诊断记录..."
        size="default"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        size="default"
        class="filter-select"
      >
        <el-option label="全部" value="" />
        <el-option label="检测完成" value="completed" />
        <el-option label="检测中" value="processing" />
        <el-option label="失败" value="failed" />
      </el-select>

      <el-select
        v-model="filterType"
        placeholder="诊断类型"
        size="default"
        class="filter-select"
      >
        <el-option label="全部" value="" />
        <el-option label="单次诊断" value="single" />
        <el-option label="批量诊断" value="batch" />
        <el-option label="病例库" value="folder" />
        <el-option label="AI 辅助" value="video" />
      </el-select>
    </div>

    <!-- 记录列表 -->
    <div class="history-list">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="history-card"
        @click="viewRecord(record)"
      >
        <div class="record-preview">
          <img
            :src="record.image"
            :alt="record.filename"
            class="preview-image"
          />
          <div class="status-badge" :class="record.status">
            <el-icon><component :is="getStatusIcon(record.status)" /></el-icon>
            {{ getStatusText(record.status) }}
          </div>
        </div>

        <div class="record-info">
          <div class="record-header">
            <span class="record-filename">{{ record.filename }}</span>
            <span class="record-type">{{ getTypeText(record.type) }}</span>
          </div>
          <div class="record-meta">
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ record.time }}
            </span>
            <span class="meta-item">
              <el-icon><Picture /></el-icon>
              {{ record.count }} 张图片
            </span>
            <span class="meta-item">
              <el-icon><Aim /></el-icon>
              {{ record.targets }} 个目标
            </span>
          </div>
          <div class="record-tags">
            <span
              v-for="tag in record.detectedTargets"
              :key="tag"
              class="detected-tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="record-actions">
          <el-button size="small" @click.stop="viewRecord(record)">
            <el-icon><Monitor /></el-icon>
            查看
          </el-button>
          <el-button size="small" @click.stop="downloadRecord(record)">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click.stop="deleteRecord(record)"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredRecords.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">暂无检测记录</p>
      <el-button type="primary" @click="goToDetection">
        <el-icon><Plus /></el-icon>
        开始检测
      </el-button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-if="totalRecords > 0"
        :total="totalRecords"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        layout="prev, pager, next"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  Search,
  Clock,
  Picture,
  Aim,
  Monitor,
  Download,
  Delete,
  Plus,
  Help,
  CircleCheck,
  Loading,
  CircleClose,
} from "@element-plus/icons-vue";
import { getDetectionHistory } from "../api/detection";

const router = useRouter();

const searchQuery = ref("");
const filterStatus = ref("");
const filterType = ref("");
const currentPage = ref(1);
const pageSize = ref(10);

const historyRecords = ref([]);

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  ? import.meta.env.VITE_API_BASE_URL.replace(/\/api$/, "")
  : "http://localhost:8000";

const loadHistory = async () => {
  try {
    const res = await getDetectionHistory();
    if (res.success && Array.isArray(res.data)) {
      historyRecords.value = res.data.map((item) => ({
        id: item.id,
        filename: item.image_url.split("/").pop() || item.id,
        image: item.result_image_url.startsWith("http")
          ? item.result_image_url
          : `${apiBaseUrl}${item.result_image_url}`,
        type: "single",
        status: "completed",
        time: new Date(item.created_at).toLocaleString(),
        count: 1,
        targets: item.total_objects,
        detectedTargets: [item.model_name],
      }));
    }
  } catch (error) {
    console.error("加载检测历史失败:", error);
  }
};

onMounted(() => {
  loadHistory();
});

const filteredRecords = computed(() => {
  return historyRecords.value.filter((record) => {
    const matchesSearch =
      !searchQuery.value ||
      record.filename.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesStatus =
      !filterStatus.value || record.status === filterStatus.value;
    const matchesType = !filterType.value || record.type === filterType.value;
    return matchesSearch && matchesStatus && matchesType;
  });
});

const totalRecords = computed(() => filteredRecords.value.length);

const getStatusIcon = (status) => {
  const icons = {
    completed: CircleCheck,
    processing: Loading,
    failed: CircleClose,
  };
  return icons[status] || CircleCheck;
};

const getStatusText = (status) => {
  const texts = {
    completed: "检测完成",
    processing: "检测中",
    failed: "失败",
  };
  return texts[status] || status;
};

const getTypeText = (type) => {
  const texts = {
    single: "单次诊断",
    batch: "批量诊断",
    folder: "病例库",
    video: "AI 辅助",
  };
  return texts[type] || type;
};

const viewRecord = (record) => {
  console.log("查看记录:", record);
  // 这里可以跳转到检测详情页面
};

const downloadRecord = (record) => {
  console.log("下载记录:", record);
};

const deleteRecord = (record) => {
  if (confirm(`确定要删除记录 "${record.filename}" 吗？`)) {
    const index = historyRecords.value.findIndex((r) => r.id === record.id);
    if (index > -1) {
      historyRecords.value.splice(index, 1);
    }
  }
};

const goToDetection = () => {
  router.push("/detection");
};

const handlePageChange = (page) => {
  currentPage.value = page;
};
</script>

<style scoped lang="scss">
.history-page {
  width: 100%;

  .page-header {
    margin-bottom: 24px;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .page-subtitle {
      font-size: 14px;
      color: var(--text-secondary);
    }
  }

  .search-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    align-items: center;

    .search-input {
      flex: 1;
      max-width: 320px;
    }

    .filter-select {
      width: 150px;
    }
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .history-card {
    background: var(--card-bg);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 22px;
    box-shadow: var(--card-shadow);
    display: flex;
    align-items: center;
    gap: 20px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      box-shadow: 0 18px 40px rgba(8, 15, 40, 0.18);
      transform: translateY(-2px);
    }

    .record-preview {
      position: relative;
      width: 130px;
      height: 92px;
      border-radius: 18px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.08);

      .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .status-badge {
        position: absolute;
        bottom: 8px;
        left: 8px;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;

        &.completed {
          background-color: rgba(34, 197, 94, 0.9);
          color: white;
        }

        &.processing {
          background-color: rgba(59, 130, 246, 0.9);
          color: white;
        }

        &.failed {
          background-color: rgba(239, 68, 68, 0.9);
          color: white;
        }
      }
    }

    .record-info {
      flex: 1;
      min-width: 0;

      .record-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;

        .record-filename {
          font-size: 15px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .record-type {
          padding: 5px 12px;
          background: rgba(124, 92, 255, 0.14);
          border-radius: 999px;
          font-size: 12px;
          color: var(--primary-color);
        }
      }

      .record-meta {
        display: flex;
        gap: 20px;
        margin-bottom: 10px;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: var(--text-secondary);

          :deep(.el-icon) {
            font-size: 14px;
          }
        }
      }

      .record-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;

        .detected-tag {
          padding: 4px 10px;
          background: rgba(57, 217, 201, 0.16);
          color: #39d9c9;
          border-radius: 999px;
          font-size: 12px;
        }
      }
    }

    .record-actions {
      display: flex;
      gap: 8px;
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 0;

    .empty-icon {
      color: #9ca3af;
      margin-bottom: 16px;
    }

    .empty-text {
      font-size: 15px;
      color: var(--text-secondary);
      margin-bottom: 24px;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 32px;
  }
}
</style>
