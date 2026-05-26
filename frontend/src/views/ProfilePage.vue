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
            <div class="user-name">{{ userInfo.username || "用户" }}</div>
            <div class="user-role">{{ userInfo.email || "未设置邮箱" }}</div>
            <el-button
              size="small"
              type="primary"
              plain
              style="margin-top: 8px"
            >
              编辑资料
            </el-button>
            <div class="user-meta">注册时间：{{ userInfo.create_time || "未知" }}</div>
          </div>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ userInfo.detection_count }}</div>
          <div class="stat-label">总诊断次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ userInfo.conversation_count }}</div>
          <div class="stat-label">会话数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">--</div>
          <div class="stat-label">平均准确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">--</div>
          <div class="stat-label">使用天数</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { getProfile } from "../api/auth.js"

const userInfo = ref({
  username: "",
  email: "",
  create_time: "",
  detection_count: 0,
  conversation_count: 0,
})

const loadProfile = async () => {
  try {
    const res = await getProfile()
    if (res.success && res.data) {
      userInfo.value = res.data
    }
  } catch (error) {
    console.error("加载用户信息失败:", error)
  }
}

onMounted(() => {
  loadProfile()
})
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
