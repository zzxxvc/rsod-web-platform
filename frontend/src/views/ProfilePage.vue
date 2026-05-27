<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">诊断中心</h1>
      <p class="page-subtitle">
        个人诊断统计与使用概览，关注病例风险与模型表现。
      </p>
    </div>

    <div class="profile-content">
      <div class="user-info-card">
        <div class="user-avatar-section">
          <el-avatar size="80">
            <img
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              alt="用户头像"
            />
          </el-avatar>
          <div class="user-basic-info">
            <div class="user-name">{{ profile.username || "—" }}</div>
            <div class="user-role">{{ roleLabel }}</div>
            <el-button
              size="small"
              type="primary"
              plain
              style="margin-top: 8px"
            >
              编辑资料
            </el-button>
          </div>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_diagnoses }}</div>
          <div class="stat-label">总诊断次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.high_risk_cases }}</div>
          <div class="stat-label">高危病例</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ accuracyText }}</div>
          <div class="stat-label">平均准确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.usage_days }}</div>
          <div class="stat-label">使用天数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { getProfileMe, getProfileStats } from "../api/profile";

const profile = reactive({
  username: "",
  email: "",
  nickname: "",
  role: "user",
});

const stats = reactive({
  total_diagnoses: 0,
  high_risk_cases: 0,
  average_accuracy: 0,
  usage_days: 1,
});

const loading = ref(false);

const roleLabel = computed(() => {
  const map = { user: "普通用户", admin: "管理员" };
  return profile.nickname || map[profile.role] || "用户";
});

const accuracyText = computed(() => {
  if (stats.total_diagnoses === 0) return "—";
  return `${stats.average_accuracy}%`;
});

const loadProfile = async () => {
  loading.value = true;
  try {
    const [meRes, statsRes] = await Promise.all([
      getProfileMe(),
      getProfileStats(),
    ]);
    if (meRes.success && meRes.data) {
      Object.assign(profile, meRes.data);
    }
    if (statsRes.success && statsRes.data) {
      Object.assign(stats, statsRes.data);
    }
  } catch (e) {
    console.error("加载个人中心失败", e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadProfile();
});
</script>

<style scoped lang="scss">
.profile-page {
  width: 100%;

  .page-header {
    margin-bottom: 24px;

    .page-title {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .page-subtitle {
      font-size: 14px;
      color: var(--text-secondary);
      max-width: 680px;
    }
  }

  .profile-content {
    display: flex;
    flex-direction: column;
    gap: 24px;

    .user-info-card {
      background: var(--card-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 22px;
      padding: 24px;
      box-shadow: var(--card-shadow);

      .user-avatar-section {
        display: flex;
        align-items: center;

        .user-basic-info {
          margin-left: 24px;

          .user-name {
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px;
          }

          .user-role {
            font-size: 14px;
            color: var(--text-secondary);
          }
        }
      }
    }

    .stats-cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 20px;

      .stat-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: var(--card-shadow);

        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: var(--secondary-color);
          margin-bottom: 10px;
        }

        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
        }
      }
    }
  }
}
</style>
