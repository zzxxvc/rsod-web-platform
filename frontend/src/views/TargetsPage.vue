<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">皮肤病变类型库</h1>
      <p class="page-subtitle">查看常见皮肤病变类别与模型判断依据</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="搜索病变类别..."
        size="default"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon target-icon">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalTargets }}</div>
          <div class="stat-label">病变类型</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon category-icon">
          <el-icon><Grid /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ categories.length }}</div>
          <div class="stat-label">分组数量</div>
        </div>
      </div>
    </div>

    <!-- 目标类别列表 -->
    <div class="target-categories">
      <div
        v-for="category in filteredCategories"
        :key="category.id"
        class="category-card"
      >
        <div class="category-header">
          <div
            class="category-icon"
            :style="{ backgroundColor: category.color }"
          >
            <component :is="category.icon" />
          </div>
          <div class="category-info">
            <div class="category-name">{{ category.name }}</div>
            <div class="category-count">
              {{ category.targets.length }} 个目标
            </div>
          </div>
        </div>
        <div class="target-list">
          <div
            v-for="target in category.targets"
            :key="target.id"
            class="target-item"
            @click="showTargetDetail(target)"
          >
            <el-icon :size="14" class="target-item-icon"
              ><CircleCheck
            /></el-icon>
            <span>{{ target.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCategories.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">未找到匹配的目标类别</p>
    </div>

    <!-- 目标详情弹窗 -->
    <el-dialog
      v-if="selectedTarget"
      :title="selectedTarget.name"
      v-model="showDialog"
      width="600px"
      class="target-detail-dialog"
    >
      <div class="target-detail">
        <!-- 病变图片 -->
        <div class="detail-image-container">
          <div v-if="selectedTarget.image" class="detail-image">
            <el-image
              :src="selectedTarget.image"
              :preview-src-list="[selectedTarget.image]"
              fit="cover"
              class="lesion-image"
            >
              <template #error>
                <div class="image-error">
                  <el-icon :size="48"><PictureRounded /></el-icon>
                  <span>暂无图片</span>
                </div>
              </template>
            </el-image>
          </div>
          <div v-else class="detail-image placeholder">
            <el-icon :size="64"><PictureRounded /></el-icon>
            <span>暂无图例</span>
          </div>
        </div>

        <!-- 病变信息 -->
        <div class="detail-info">
          <div class="detail-item">
            <span class="detail-label">所属类别</span>
            <span class="detail-value">
              <el-tag
                :color="getCategoryColor(selectedTarget.categoryId)"
                size="small"
              >
                {{ getCategoryName(selectedTarget.categoryId) }}
              </el-tag>
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">病变描述</span>
            <span class="detail-value description">{{
              selectedTarget.description
            }}</span>
          </div>
          <div class="detail-item" v-if="selectedTarget.accuracy">
            <span class="detail-label">检测精度</span>
            <span class="detail-value">
              <el-tag type="success" size="small">{{
                selectedTarget.accuracy
              }}</el-tag>
            </span>
          </div>
          <div class="detail-item" v-if="selectedTarget.features">
            <span class="detail-label">主要特征</span>
            <span class="detail-value features">{{
              selectedTarget.features
            }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Search,
  Aim,
  Grid,
  CircleCheck,
  Help,
  PictureRounded,
  Sunny,
  Setting,
  InfoFilled,
} from "@element-plus/icons-vue";

const searchQuery = ref("");
const showDialog = ref(false);
const selectedTarget = ref(null);

// 图片放在 /frontend/images/ 目录下
const lesionsImages = {
  1: "/images/光化性角化病.jpg",
  2: "/images/基底细胞癌.jpg",
  3: "/images/良性角化病.jpg",
  4: "/images/皮肤纤维瘤.jpg",
  5: "/images/黑色素瘤.jpg",
  6: "/images/黑色素细胞痣.jpg",
  7: "/images/血管性病变.jpg",
};

const categories = ref([
  {
    id: 1,
    name: "良性病变",
    icon: PictureRounded,
    color: "#10b981",
    targets: [
      {
        id: 1,
        name: "光化性角化病",
        categoryId: 1,
        description: "...",
        image: lesionsImages[1],
      },
      {
        id: 3,
        name: "良性角化病",
        categoryId: 1,
        description: "...",
        image: lesionsImages[3],
      },
      {
        id: 4,
        name: "皮肤纤维瘤",
        categoryId: 1,
        description: "...",
        image: lesionsImages[4],
      },
      {
        id: 6,
        name: "黑色素细胞痣",
        categoryId: 1,
        description: "...",
        image: lesionsImages[6],
      },
    ],
  },
  {
    id: 2,
    name: "恶性病变",
    icon: PictureRounded,
    color: "#f59e42",
    targets: [
      {
        id: 2,
        name: "基底细胞癌",
        categoryId: 2,
        description: "...",
        image: lesionsImages[2],
      },
      {
        id: 5,
        name: "黑色素瘤",
        categoryId: 2,
        description: "...",
        image: lesionsImages[5],
      },
    ],
  },
  {
    id: 3,
    name: "血管性病变",
    icon: PictureRounded,
    color: "#3b82f6",
    targets: [
      {
        id: 7,
        name: "血管性病变",
        categoryId: 3,
        description: "...",
        image: lesionsImages[7],
      },
    ],
  },
]);

const filteredCategories = computed(() => {
  if (!searchQuery.value) {
    return categories.value;
  }
  const query = searchQuery.value.toLowerCase();
  return categories.value
    .map((category) => ({
      ...category,
      targets: category.targets.filter(
        (target) =>
          target.name.toLowerCase().includes(query) ||
          target.description.toLowerCase().includes(query),
      ),
    }))
    .filter(
      (category) =>
        category.name.toLowerCase().includes(query) ||
        category.targets.length > 0,
    );
});

const totalTargets = computed(() => {
  return categories.value.reduce(
    (sum, category) => sum + category.targets.length,
    0,
  );
});

const getCategoryColor = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.color : "#6b7280";
};

const getCategoryName = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.name : "未知";
};

const showTargetDetail = (target) => {
  selectedTarget.value = target;
  showDialog.value = true;
};
</script>

<style scoped lang="scss">
.targets-page {
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

  .search-container {
    margin-bottom: 24px;

    .search-input {
      max-width: 300px;
    }
  }

  .stats-cards {
    display: flex;
    gap: 20px;
    margin-bottom: 24px;

    .stat-card {
      flex: 1;
      max-width: 200px;
      background: var(--card-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 18px;
      padding: 22px;
      gap: 16px;

      .stat-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;

        &.target-icon {
          background-color: #27ae60;
        }

        &.category-icon {
          background-color: #3b82f6;
        }
      }

      .stat-info {
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--text-primary);
        }

        .stat-label {
          font-size: 13px;
          color: var(--text-secondary);
        }
      }
    }
  }

  .target-categories {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;

    .category-card {
      background: var(--card-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      padding: 22px;
      box-shadow: var(--card-shadow);
      transition: all 0.2s ease;
      &:hover {
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
      }

      .category-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;

        .category-icon {
          width: 50px;
          height: 50px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 24px;
          margin-right: 16px;
        }

        .category-info {
          .category-name {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
          }

          .category-count {
            font-size: 13px;
            color: var(--text-secondary);
          }
        }
      }

      .target-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .target-item {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 16px;
          background: rgba(255, 255, 255, 0.04);
          border-radius: 20px;
          font-size: 14px;
          color: var(--text-primary);
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            background: rgba(124, 92, 255, 0.16);
            color: var(--primary-color);
          }

          .target-item-icon {
            color: var(--primary-color);
          }
        }
      }
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
    }
  }
}

// 弹窗样式
.target-detail-dialog {
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 12px;
  }
}

.target-detail {
  .detail-image-container {
    margin-bottom: 24px;
    display: flex;
    justify-content: center;
  }

  .detail-image {
    width: 100%;
    max-width: 400px;
    height: 300px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

    &.placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #f5f7fa;
      color: #909399;

      span {
        margin-top: 12px;
        font-size: 14px;
      }
    }

    .lesion-image {
      width: 100%;
      height: 100%;
    }

    .image-error {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #909399;

      span {
        margin-top: 8px;
        font-size: 14px;
      }
    }
  }

  .detail-info {
    .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 14px 0;
      border-bottom: 1px solid #f3f4f6;

      &:last-child {
        border-bottom: none;
      }

      .detail-label {
        font-size: 14px;
        color: var(--text-secondary);
        font-weight: 500;
        min-width: 80px;
      }

      .detail-value {
        font-size: 14px;
        color: var(--text-primary);
        font-weight: 500;
        flex: 1;
        text-align: right;

        &.description {
          text-align: left;
          line-height: 1.8;
          color: var(--text-regular);
        }

        &.features {
          text-align: left;
          line-height: 1.6;
          color: var(--text-regular);
        }
      }
    }
  }
}
</style>
