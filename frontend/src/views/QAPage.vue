<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">皮肤病变问答</h1>
      <p class="page-subtitle">
        询问病变类型、诊断指标与复诊建议，AI 助手随时响应。
      </p>
    </div>

    <div class="chat-container">
      <div class="chat-messages">
        <div class="message ai-message">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            你好！我是皮肤病变诊断助手。请描述你的病变图像、症状或诊断疑问，我会帮你分析常见类型与参考建议。
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="question"
          placeholder="请输入您的皮肤诊断问题..."
          :rows="3"
        />
        <el-button type="primary" class="send-btn" :loading="sending">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const question = ref("");
const sending = ref(false);
</script>

<style scoped lang="scss">
.qa-page {
  width: 100%;
  display: flex;
  flex-direction: column;

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
      max-width: 720px;
    }
  }

  .chat-container {
    flex: 1;
    background: var(--card-bg);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 22px;
    box-shadow: var(--card-shadow);
    display: flex;
    flex-direction: column;

    .chat-messages {
      flex: 1;
      padding: 24px;
      overflow-y: auto;

      .message {
        display: flex;
        margin-bottom: 20px;

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background-color: var(--primary-color);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 14px;
          flex-shrink: 0;
        }

        .message-content {
          background: rgba(255, 255, 255, 0.06);
          padding: 14px 18px;
          border-radius: 0 18px 18px 18px;
          max-width: 70%;
          line-height: 1.75;
          font-size: 14px;
          color: var(--text-secondary);
        }

        &.user-message {
          flex-direction: row-reverse;

          .message-avatar {
            margin-right: 0;
            margin-left: 14px;
            background-color: #60a5fa;
          }

          .message-content {
            background: rgba(124, 92, 255, 0.18);
            border-radius: 18px 0 18px 18px;
            color: var(--text-primary);
          }
        }
      }
    }

    .chat-input {
      padding: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      gap: 12px;

      .send-btn {
        width: 120px;
      }
    }
  }
}
</style>
