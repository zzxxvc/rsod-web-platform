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
      :visible.sync="showDialog"
      width="400px"
    >
      <div class="target-detail">
        <div
          class="detail-icon"
          :style="{
            backgroundColor: getCategoryColor(selectedTarget.categoryId),
          }"
        >
          <el-icon :size="48"
            ><component :is="getCategoryIcon(selectedTarget.categoryId)"
          /></el-icon>
        </div>
        <div class="detail-info">
          <div class="detail-item">
            <span class="detail-label">所属类别</span>
            <span class="detail-value">{{
              getCategoryName(selectedTarget.categoryId)
            }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">目标描述</span>
            <span class="detail-value">{{ selectedTarget.description }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">检测精度</span>
            <span class="detail-value">{{ selectedTarget.accuracy }}</span>
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
  Document,
  Ship,
  Van,
  Guide,
  Bicycle,
  OfficeBuilding,
  Shop,
  School,
  MapLocation,
  Coordinate,
  Place,
  AddLocation,
  Location,
  PictureRounded,
  Sunny,
  ArrowRight,
  Setting,
  InfoFilled,
} from "@element-plus/icons-vue";

const searchQuery = ref("");
const showDialog = ref(false);
const selectedTarget = ref(null);

const categories = ref([
  {
    id: 1,
    name: "良性病变",
    icon: PictureRounded,
    color: "#10b981",
    targets: [
      {
        id: 1,
        name: "雀斑",
        categoryId: 1,
        description: "常见色素沉着良性病变",
        accuracy: "96.8%",
      },
      {
        id: 2,
        name: "痣",
        categoryId: 1,
        description: "常见色素痣，通常为良性",
        accuracy: "97.5%",
      },
      {
        id: 3,
        name: "脂溢性角化",
        categoryId: 1,
        description: "表皮良性增生",
        accuracy: "95.9%",
      },
    ],
  },
  {
    id: 2,
    name: "炎症性病变",
    icon: Sunny,
    color: "#f59e0b",
    targets: [
      {
        id: 4,
        name: "湿疹",
        categoryId: 2,
        description: "皮肤炎症，常伴瘙痒",
        accuracy: "94.8%",
      },
      {
        id: 5,
        name: "银屑病",
        categoryId: 2,
        description: "慢性炎症性皮肤病",
        accuracy: "95.2%",
      },
      {
        id: 6,
        name: "脂溢性皮炎",
        categoryId: 2,
        description: "常见的头皮和面部炎症",
        accuracy: "94.1%",
      },
    ],
  },
  {
    id: 3,
    name: "色素异常",
    icon: InfoFilled,
    color: "#8b5cf6",
    targets: [
      {
        id: 7,
        name: "黄褐斑",
        categoryId: 3,
        description: "色素沉着性病变",
        accuracy: "96.3%",
      },
      {
        id: 8,
        name: "白癜风",
        categoryId: 3,
        description: "局部色素脱失病变",
        accuracy: "95.6%",
      },
      {
        id: 9,
        name: "色素痣",
        categoryId: 3,
        description: "色素细胞增多导致的斑点",
        accuracy: "95.9%",
      },
    ],
  },
  {
    id: 4,
    name: "肿瘤/可疑病变",
    icon: Setting,
    color: "#3b82f6",
    targets: [
      {
        id: 10,
        name: "基底细胞癌",
        categoryId: 4,
        description: "常见的皮肤恶性肿瘤",
        accuracy: "91.4%",
      },
      {
        id: 11,
        name: "鳞状细胞癌",
        categoryId: 4,
        description: "中度风险的皮肤肿瘤",
        accuracy: "92.1%",
      },
      {
        id: 12,
        name: "黑色素瘤",
        categoryId: 4,
        description: "高度恶性皮肤肿瘤",
        accuracy: "89.8%",
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
      targets: category.targets.filter((target) =>
        target.name.toLowerCase().includes(query),
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

const getCategoryIcon = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.icon : PictureRounded;
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

  .target-detail {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;

    .detail-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      margin-bottom: 20px;
    }

    .detail-info {
      width: 100%;

      .detail-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f3f4f6;

        &:last-child {
          border-bottom: none;
        }

        .detail-label {
          font-size: 14px;
          color: var(--text-secondary);
        }

        .detail-value {
          font-size: 14px;
          color: var(--text-primary);
          font-weight: 500;
        }
      }
    }
  }
}
</style>
