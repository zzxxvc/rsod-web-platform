<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">皮肤病变问答</h1>
      <p class="page-subtitle">
        询问病变类型、诊断指标与复诊建议，AI 助手随时响应。
      </p>
    </div>

    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="chat-messages" ref="messageContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="[
            'message',
            msg.role === 'user' ? 'user-message' : 'ai-message',
          ]"
        >
          <div class="message-avatar">
            <el-icon>
              <component :is="msg.role === 'user' ? 'User' : 'ChatDotRound'" />
            </el-icon>
          </div>
          <div class="message-content">
            <!-- 支持简单 Markdown 换行 -->
            <span v-html="formatMessage(msg.content)" />
          </div>
        </div>

        <!-- 加载中提示 -->
        <div v-if="sending" class="message ai-message">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <el-skeleton :rows="3" animated />
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="chat-input">
        <el-input
          v-model="question"
          placeholder="请输入您的皮肤诊断问题..."
          :rows="3"
          type="textarea"
          @keydown.enter.prevent="sendMessage"
          :disabled="sending"
        />
        <el-button
          type="primary"
          class="send-btn"
          :loading="sending"
          @click="sendMessage"
          :disabled="!question.trim() || sending"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { ChatDotRound, User } from "@element-plus/icons-vue";
import axios from "axios";

// 🔑 配置后端基础地址（按你实际部署修改）
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

const question = ref("");
const sending = ref(false);
const messageContainer = ref(null);

// 💬 消息列表：每条消息包含 role('user'/'ai') 和 content
const messages = ref([
  {
    role: "ai",
    content:
      "你好！我是皮肤病变诊断助手。请描述你的病变图像、症状或诊断疑问，我会帮你分析常见类型与参考建议。",
  },
]);

// 📝 格式化消息：支持简单换行
const formatMessage = (text) => {
  return text?.replace(/\n/g, "<br/>") || "";
};

// 🚀 发送消息核心函数
const sendMessage = async () => {
  const content = question.value.trim();
  if (!content || sending.value) return;

  // 1️⃣ 添加用户消息到界面
  messages.value.push({ role: "user", content });
  question.value = "";
  sending.value = true;

  // 2️⃣ 滚动到底部
  await scrollToBottom();

  try {
    // 3️⃣ 调用后端 API
    const res = await axios.post(
      `${API_BASE}/qa/ask`,
      { question: content },
      {
        headers: { "Content-Type": "application/json" },
        timeout: 60000, // 60 秒超时，防止大模型响应慢
      },
    );

    // 4️⃣ 添加 AI 回复
    messages.value.push({
      role: "ai",
      content: res.data.answer || "抱歉，未收到有效回复",
    });
  } catch (err) {
    console.error("❌ 请求失败:", err);
    // 🔥 友好错误提示
    let errorMsg = "请求失败";
    if (err.code === "ERR_NETWORK" || err.response?.status === 0) {
      errorMsg = "❌ 无法连接后端，请确认服务正在运行（端口 8000）";
    } else if (err.response?.data?.detail) {
      errorMsg = `❌ ${err.response.data.detail}`;
    } else if (err.message) {
      errorMsg = `❌ ${err.message}`;
    }
    messages.value.push({ role: "ai", content: errorMsg });
  } finally {
    sending.value = false;
    await scrollToBottom();
  }
};

// 📜 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};
</script>

<style scoped lang="scss">
.qa-page {
  width: 100%;
  display: flex;
  flex-direction: column;
  height: 100%;

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
    min-height: 0; // 🔑 关键：让 flex 子元素能滚动

    .chat-messages {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      scroll-behavior: smooth;

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
          word-wrap: break-word;

          :deep(br) {
            line-height: 1.75;
          }
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

      :deep(.el-input__wrapper) {
        background: rgba(255, 255, 255, 0.04);
      }

      .send-btn {
        width: 120px;
      }
    }
  }
}
</style>
