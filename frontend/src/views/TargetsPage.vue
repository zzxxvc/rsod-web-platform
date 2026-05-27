<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-hero">
      <div class="hero-content">
        <h1 class="hero-title">📚 皮肤病变类型库</h1>
        <p class="hero-desc">浏览常见皮肤病变类别，了解其临床特征与典型表现</p>
      </div>
    </div>

    <!-- 工具栏：搜索 + 筛选 -->
    <div class="toolbar">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索病变名称、英文名或描述..."
          size="large"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="filter-tabs">
        <span
          v-for="cat in filterOptions"
          :key="cat.value"
          class="filter-chip"
          :class="{ active: activeCategory === cat.value }"
          @click="activeCategory = cat.value"
        >
          {{ cat.label }}
          <span v-if="cat.value === 'all'" class="chip-count">{{
            totalTargets
          }}</span>
        </span>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="overview-row">
      <div class="overview-card">
        <span class="overview-num">{{ totalTargets }}</span>
        <span class="overview-text">种病变类型</span>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-card">
        <span class="overview-num">{{ categories.length }}</span>
        <span class="overview-text">个分类组别</span>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-card">
        <span class="overview-num">{{ benignCount }}</span>
        <span class="overview-text">良性病变</span>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-card">
        <span class="overview-num">{{ malignantCount }}</span>
        <span class="overview-text">恶性病变</span>
      </div>
    </div>

    <!-- 目标列表 -->
    <div class="target-grid">
      <div
        v-for="category in filteredCategories"
        :key="category.id"
        class="category-section"
      >
        <div class="section-head" @click="toggleCategory(category.id)">
          <div class="section-head-left">
            <span
              class="section-dot"
              :style="{ background: category.color }"
            ></span>
            <h2 class="section-title">{{ category.name }}</h2>
            <span class="section-count">{{ category.targets.length }} 项</span>
          </div>
          <el-icon
            class="section-arrow"
            :class="{ rotated: expandedCategories.has(category.id) }"
          >
            <ArrowDown />
          </el-icon>
        </div>

        <div
          class="section-body"
          :class="{ collapsed: !expandedCategories.has(category.id) }"
        >
          <div class="section-desc">{{ category.description }}</div>
          <div class="lesion-cards">
            <div
              v-for="target in category.targets"
              :key="target.id"
              class="lesion-card"
              @click="showTargetDetail(target)"
            >
              <div class="lesion-img">
                <img
                  v-if="target.image"
                  :src="target.image"
                  :alt="target.name"
                  @error="onImageError"
                />
                <el-icon v-else :size="28"><PictureRounded /></el-icon>
              </div>
              <div class="lesion-info">
                <div class="lesion-name">{{ target.name }}</div>
                <div class="lesion-eng">{{ target.engName }}</div>
                <div class="lesion-brief">{{ target.brief }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCategories.length === 0" class="empty-state">
      <el-icon :size="56"><Search /></el-icon>
      <p>未找到匹配的病变类型</p>
      <span>试试调整关键词或筛选条件</span>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-if="selectedTarget"
      v-model="showDialog"
      width="640px"
      class="lesion-dialog"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <template #header>
        <div class="dlg-header">
          <span class="dlg-title">{{ selectedTarget.name }}</span>
          <span
            class="dlg-badge"
            :style="{ background: getCategoryColor(selectedTarget.categoryId) }"
          >
            {{ getCategoryName(selectedTarget.categoryId) }}
          </span>
        </div>
      </template>

      <div class="dlg-body">
        <!-- 图片区 -->
        <div class="dlg-image-area">
          <div class="dlg-image">
            <el-image
              v-if="selectedTarget.image"
              :src="selectedTarget.image"
              :preview-src-list="[selectedTarget.image]"
              fit="cover"
              :preview-teleported="true"
            >
              <template #error>
                <div class="img-fallback">
                  <el-icon :size="40"><PictureRounded /></el-icon>
                  <span>暂无图片</span>
                </div>
              </template>
            </el-image>
            <div v-else class="img-fallback">
              <el-icon :size="40"><PictureRounded /></el-icon>
              <span>暂无图例</span>
            </div>
          </div>
          <span class="img-tip">点击图片可放大查看</span>
        </div>

        <!-- 信息区 -->
        <div class="dlg-info">
          <div class="dlg-info-block">
            <h4>📋 临床描述</h4>
            <p>{{ selectedTarget.description }}</p>
          </div>
          <div class="dlg-info-block">
            <h4>🔍 视觉特征</h4>
            <p>{{ selectedTarget.features }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { Search, PictureRounded, ArrowDown } from "@element-plus/icons-vue";

// ---- 状态 ----
const searchQuery = ref("");
const showDialog = ref(false);
const selectedTarget = ref(null);
const activeCategory = ref("all");
const expandedCategories = ref(new Set([1, 2, 3]));

// ---- 工具函数 ----
const toggleCategory = (id) => {
  const next = new Set(expandedCategories.value);
  next.has(id) ? next.delete(id) : next.add(id);
  expandedCategories.value = next;
};

const onImageError = (e) => {
  e.target.style.display = "none";
};

// ---- 图片 ----
const lesionsImages = {
  1: "/images/光化性角化病.jpg",
  2: "/images/基底细胞癌.jpg",
  3: "/images/良性角化病.jpg",
  4: "/images/皮肤纤维瘤.jpg",
  5: "/images/黑色素瘤.jpg",
  6: "/images/黑色素细胞痣.jpg",
  7: "/images/血管性病变.jpg",
};

// ---- 数据 ----
const categories = ref([
  {
    id: 1,
    name: "良性病变",
    description:
      "非癌性皮肤病变，通常发展缓慢、预后良好，多数无需特殊治疗，但需定期观察。",
    color: "#10b981",
    targets: [
      {
        id: 1,
        name: "光化性角化病",
        engName: "Actinic Keratosis",
        categoryId: 1,
        brief: "日光暴露部位的癌前病变，表面粗糙呈砂纸样",
        description:
          "光化性角化病是一种癌前病变，由长期日光暴露引起的表皮内角质形成细胞非典型增生。表现为干燥、粗糙、鳞屑性斑片，好发于面部、手背等日光暴露部位。若不及时治疗，部分病例可进展为鳞状细胞癌。",
        features:
          "表面粗糙呈砂纸样、边界不清的红斑或棕黄色斑片、可见鳞屑或结痂、触诊可感知粗糙感",
        image: lesionsImages[1],
      },
      {
        id: 3,
        name: "良性角化病",
        engName: "Benign Keratosis",
        categoryId: 1,
        brief: "最常见的良性表皮肿瘤，呈贴附状棕褐色斑块",
        description:
          "良性角化病（脂溢性角化病）是最常见的良性表皮肿瘤，多见于中老年人群。表现为边界清晰、呈贴附状生长的棕褐色至黑色斑块，表面呈乳头瘤样或疣状，好发于躯干和面部。通常无需治疗，属于完全良性的皮肤变化。",
        features:
          "边界清楚、贴附状生长、表面呈疣状或乳头状、颜色从淡棕到深黑不等、可见角化栓",
        image: lesionsImages[3],
      },
      {
        id: 4,
        name: "皮肤纤维瘤",
        engName: "Dermatofibroma",
        categoryId: 1,
        brief: "四肢常见的良性纤维组织增生小结节",
        description:
          "皮肤纤维瘤是一种常见的良性纤维组织细胞增生，好发于四肢，尤其是小腿部位。表现为坚硬、圆顶形丘疹或结节，直径通常小于1厘米，颜色从红棕色到紫褐色不等。侧压时可见特征性的「酒窝征」。",
        features:
          "质硬小结节、表面光滑或轻度角化、侧压呈酒窝征、颜色呈红棕至紫褐色、多见于四肢",
        image: lesionsImages[4],
      },
      {
        id: 6,
        name: "黑色素细胞痣",
        engName: "Melanocytic Nevus",
        categoryId: 1,
        brief: "几乎人人都有，由黑色素细胞聚集形成的良性痣",
        description:
          "黑色素细胞痣（俗称痣）是由黑色素细胞聚集形成的良性皮肤肿瘤，几乎人人都有。形态多样，可为扁平斑疹、隆起丘疹或乳头状结节，颜色从肤色到深黑色不等。大多数痣终生保持良性，但需定期观察是否有异常变化。",
        features:
          "边界规则对称、颜色均匀、直径多小于6mm、形态可扁平或隆起、随时间缓慢变化",
        image: lesionsImages[6],
      },
    ],
  },
  {
    id: 2,
    name: "恶性病变",
    description:
      "具有侵袭性的皮肤恶性肿瘤，需要及时诊断和干预，早期发现对预后至关重要。",
    color: "#ef4444",
    targets: [
      {
        id: 2,
        name: "基底细胞癌",
        engName: "Basal Cell Carcinoma",
        categoryId: 2,
        brief: "最常见的皮肤恶性肿瘤，呈珍珠样半透明外观",
        description:
          "基底细胞癌是最常见的皮肤恶性肿瘤，起源于表皮基底层的角质形成细胞。生长缓慢，极少转移，但具有局部侵袭性。典型表现为珍珠样半透明丘疹，表面可见毛细血管扩张，可伴有中央溃疡或结痂。好发于头面部日光暴露区域。",
        features:
          "珍珠样或蜡样外观、可见毛细血管扩张、边缘卷曲隆起、中央溃疡或凹陷、好发于面部",
        image: lesionsImages[2],
      },
      {
        id: 5,
        name: "黑色素瘤",
        engName: "Melanoma",
        categoryId: 2,
        brief: "最具侵袭性的皮肤恶性肿瘤，ABCDE 法则辅助识别",
        description:
          "黑色素瘤是最具侵袭性的皮肤恶性肿瘤，起源于黑色素细胞的恶性转化。ABCDE 法则可辅助早期识别：不对称 (Asymmetry)、边缘不规则 (Border)、颜色不均匀 (Color)、直径增大 (Diameter)、不断演变 (Evolving)。早期发现和手术切除是关键。",
        features:
          "不对称形态、边缘不规则呈锯齿状、颜色斑驳不均匀、直径常超过6mm、短期内有明显变化",
        image: lesionsImages[5],
      },
    ],
  },
  {
    id: 3,
    name: "血管性病变",
    description: "来源于血管组织的皮肤病变，大多为良性，仅少数需要治疗干预。",
    color: "#3b82f6",
    targets: [
      {
        id: 7,
        name: "血管性病变",
        engName: "Vascular Lesion",
        categoryId: 3,
        brief: "红色或紫红色外观，按压可褪色",
        description:
          "血管性病变包括血管瘤、鲜红斑痣、蜘蛛痣等多种血管来源的皮肤病变。临床表现为红色、紫红色或蓝色的斑疹、丘疹或结节，压之可褪色或部分褪色。大多数血管性病变为良性，仅少数需要治疗干预。",
        features:
          "红色或紫红色外观、按压可褪色或部分褪色、边界可清晰或模糊、可见血管纹理、表面光滑",
        image: lesionsImages[7],
      },
    ],
  },
]);

// ---- 筛选选项 ----
const filterOptions = computed(() => [
  { label: "全部", value: "all" },
  ...categories.value.map((c) => ({ label: c.name, value: c.id })),
]);

// ---- 计算属性 ----
const totalTargets = computed(() =>
  categories.value.reduce((s, c) => s + c.targets.length, 0),
);

const benignCount = computed(() => {
  const cat = categories.value.find((c) => c.id === 1);
  return cat ? cat.targets.length : 0;
});

const malignantCount = computed(() => {
  const cat = categories.value.find((c) => c.id === 2);
  return cat ? cat.targets.length : 0;
});

const filteredByCategory = computed(() =>
  activeCategory.value === "all"
    ? categories.value
    : categories.value.filter((c) => c.id === activeCategory.value),
);

const filteredCategories = computed(() => {
  let result = filteredByCategory.value;
  const q = searchQuery.value.toLowerCase().trim();
  if (!q) return result;
  return result
    .map((cat) => ({
      ...cat,
      targets: cat.targets.filter(
        (t) =>
          t.name.toLowerCase().includes(q) ||
          t.engName.toLowerCase().includes(q) ||
          t.brief.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          t.features.toLowerCase().includes(q),
      ),
    }))
    .filter(
      (cat) =>
        cat.name.toLowerCase().includes(q) ||
        cat.description.toLowerCase().includes(q) ||
        cat.targets.length > 0,
    );
});

const getCategoryColor = (id) =>
  categories.value.find((c) => c.id === id)?.color || "#6b7280";

const getCategoryName = (id) =>
  categories.value.find((c) => c.id === id)?.name || "未知";

const showTargetDetail = (target) => {
  selectedTarget.value = target;
  showDialog.value = true;
};
</script>

<style scoped lang="scss">
// ========== 变量 ==========
$radius-sm: 10px;
$radius-md: 14px;
$radius-lg: 18px;

// ========== 页面容器 ==========
.targets-page {
  width: 100%;
  padding-bottom: 48px;
}

// ========== Hero 头部 ==========
.page-hero {
  margin-bottom: 28px;

  .hero-content {
    .hero-title {
      font-size: 28px;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 8px;
    }
    .hero-desc {
      font-size: 14px;
      color: #64748b;
      margin: 0;
    }
  }
}

// ========== 工具栏 ==========
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;

  .search-box {
    flex: 1;
    min-width: 240px;
    max-width: 360px;

    :deep(.el-input__wrapper) {
      border-radius: $radius-md;
      background: #fff;
      border: 1px solid #e2e8f0;
      box-shadow: none;
      transition: border 0.2s;
      &:hover,
      &.is-focus {
        border-color: #94a3b8;
        box-shadow: none;
      }
    }
  }

  .filter-tabs {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .filter-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    font-size: 13px;
    color: #475569;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
    user-select: none;

    &:hover {
      border-color: #94a3b8;
      color: #1e293b;
    }

    &.active {
      background: #1e293b;
      color: #fff;
      border-color: #1e293b;
    }

    .chip-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 20px;
      height: 20px;
      padding: 0 5px;
      font-size: 11px;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.2);
    }
  }
}

// ========== 统计概览 ==========
.overview-row {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: $radius-lg;
  padding: 18px 28px;
  margin-bottom: 24px;

  .overview-card {
    flex: 1;
    text-align: center;

    .overview-num {
      display: block;
      font-size: 22px;
      font-weight: 700;
      color: #1e293b;
    }
    .overview-text {
      font-size: 12px;
      color: #94a3b8;
      margin-top: 2px;
    }
  }

  .overview-divider {
    width: 1px;
    height: 36px;
    background: #e2e8f0;
  }
}

// ========== 分类区块 ==========
.target-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.category-section {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: $radius-lg;
  overflow: hidden;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;

  &:hover {
    background: #f8fafc;
  }

  .section-head-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .section-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }

  .section-count {
    font-size: 12px;
    color: #94a3b8;
    background: #f1f5f9;
    padding: 2px 10px;
    border-radius: 10px;
  }

  .section-arrow {
    color: #94a3b8;
    font-size: 14px;
    transition: transform 0.3s;

    &.rotated {
      transform: rotate(180deg);
    }
  }
}

.section-body {
  transition: all 0.35s ease;
  max-height: 600px;
  opacity: 1;

  &.collapsed {
    max-height: 0;
    opacity: 0;
    overflow: hidden;
  }
}

.section-desc {
  padding: 0 20px 16px;
  font-size: 13px;
  color: #64748b;
}

.lesion-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px;
  padding: 0 20px 18px;
}

.lesion-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: $radius-sm;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  background: #f8fafc;

  &:hover {
    background: #f1f5f9;
    border-color: #e2e8f0;
  }

  .lesion-img {
    width: 56px;
    height: 56px;
    border-radius: $radius-sm;
    overflow: hidden;
    background: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    flex-shrink: 0;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .lesion-info {
    flex: 1;
    min-width: 0;

    .lesion-name {
      font-size: 15px;
      font-weight: 600;
      color: #1e293b;
    }

    .lesion-eng {
      font-size: 12px;
      color: #94a3b8;
      margin: 2px 0 4px;
    }

    .lesion-brief {
      font-size: 12px;
      color: #64748b;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

// ========== 空状态 ==========
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
  color: #94a3b8;

  .el-icon {
    margin-bottom: 14px;
    color: #cbd5e1;
  }

  p {
    font-size: 15px;
    color: #64748b;
    margin: 0 0 4px;
  }

  span {
    font-size: 13px;
  }
}

// ========== 弹窗 ==========
.lesion-dialog {
  :deep(.el-dialog) {
    border-radius: 20px;
  }
  :deep(.el-dialog__header) {
    padding: 20px 24px 0;
    margin: 0;
  }
  :deep(.el-dialog__body) {
    padding: 20px 24px 24px;
  }
}

.dlg-header {
  display: flex;
  align-items: center;
  gap: 12px;

  .dlg-title {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
  }

  .dlg-badge {
    font-size: 12px;
    color: #fff;
    padding: 3px 12px;
    border-radius: 12px;
  }
}

.dlg-body {
  .dlg-image-area {
    text-align: center;
    margin-bottom: 20px;

    .dlg-image {
      width: 100%;
      max-width: 400px;
      height: 260px;
      margin: 0 auto;
      border-radius: $radius-md;
      overflow: hidden;
      box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);

      .el-image {
        width: 100%;
        height: 100%;
      }

      .img-fallback {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f8fafc;
        color: #94a3b8;
        gap: 8px;

        span {
          font-size: 13px;
        }
      }
    }

    .img-tip {
      display: inline-block;
      margin-top: 8px;
      font-size: 12px;
      color: #94a3b8;
    }
  }

  .dlg-info {
    display: flex;
    flex-direction: column;
    gap: 14px;

    .dlg-info-block {
      background: #f8fafc;
      border-radius: $radius-md;
      padding: 16px 18px;

      h4 {
        margin: 0 0 8px;
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
      }

      p {
        margin: 0;
        font-size: 14px;
        color: #475569;
        line-height: 1.8;
      }
    }
  }
}

// ========== 响应式 ==========
@media (max-width: 768px) {
  .overview-row {
    padding: 14px 16px;
    flex-wrap: wrap;
    gap: 12px;

    .overview-divider {
      display: none;
    }
    .overview-card {
      flex: 1 1 40%;
    }
  }

  .lesion-cards {
    grid-template-columns: 1fr !important;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;

    .search-box {
      max-width: 100%;
    }
  }
}
</style>
