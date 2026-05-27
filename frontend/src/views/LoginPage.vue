<template>
  <div class="auth-page">
    <!-- 左侧品牌展示区 -->
    <div class="auth-panel brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <svg viewBox="0 0 60 60" class="logo-svg">
            <circle
              cx="30"
              cy="30"
              r="28"
              fill="none"
              stroke="rgba(255,255,255,0.4)"
              stroke-width="2"
            />
            <circle cx="30" cy="30" r="12" fill="rgba(255,255,255,0.25)" />
            <circle cx="30" cy="30" r="6" fill="rgba(255,255,255,0.6)" />
            <line
              x1="30"
              y1="6"
              x2="30"
              y2="18"
              stroke="rgba(255,255,255,0.5)"
              stroke-width="2"
              stroke-linecap="round"
            />
            <line
              x1="30"
              y1="42"
              x2="30"
              y2="54"
              stroke="rgba(255,255,255,0.5)"
              stroke-width="2"
              stroke-linecap="round"
            />
            <line
              x1="6"
              y1="30"
              x2="18"
              y2="30"
              stroke="rgba(255,255,255,0.5)"
              stroke-width="2"
              stroke-linecap="round"
            />
            <line
              x1="42"
              y1="30"
              x2="54"
              y2="30"
              stroke="rgba(255,255,255,0.5)"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <h1 class="brand-title">RSOD 智能检测平台</h1>
        <p class="brand-desc">
          基于深度学习的皮肤病变智能识别系统，支持多种常见皮肤病变类型的快速检测与分析。
        </p>
        <div class="brand-features">
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>精准识别 7 类皮肤病变</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>AI 智能问答辅助诊断</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>历史记录随时回溯</span>
          </div>
        </div>
      </div>
      <div class="brand-footer">
        <span>© 2026 RSOD Platform</span>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="auth-panel form-panel">
      <div class="form-wrapper">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录您的账号以继续使用</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="auth-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
              class="auth-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              class="auth-input"
              show-password
            >
              <template #prefix>
                <el-icon class="input-icon"><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-row">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <router-link to="/forgot-password" class="text-link"
              >忘记密码？</router-link
            >
          </div>

          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="text-link">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { User, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { login } from "../api/auth.js";

const router = useRouter();
const loading = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度 3-20 个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度 6-30 个字符", trigger: "blur" },
  ],
};

const loginFormRef = ref(null);

const handleLogin = async () => {
  loginFormRef.value.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      const res = await login(loginForm.username, loginForm.password);
      if (res.access_token) {
        localStorage.setItem("token", res.access_token);
        localStorage.setItem("username", loginForm.username);
        router.push("/detection");
      } else {
        alert("登录失败：" + (res.detail || "用户名或密码错误"));
      }
    } catch (error) {
      console.error(error);
      alert("登录失败：服务器连接错误");
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style scoped>
/* ========== 整体布局 ========== */
.auth-page {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

.auth-panel {
  flex: 1;
}

/* ========== 左侧品牌面板 ========== */
.brand-panel {
  background: linear-gradient(160deg, #1e3a5f 0%, #2d6a9f 40%, #3b8bc6 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px 48px;
  position: relative;
  overflow: hidden;
}

.brand-panel::before {
  content: "";
  position: absolute;
  top: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
}

.brand-panel::after {
  content: "";
  position: absolute;
  bottom: -15%;
  left: -10%;
  width: 350px;
  height: 350px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
}

.brand-content {
  max-width: 380px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 28px;
}

.logo-svg {
  width: 72px;
  height: 72px;
}

.brand-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px;
  letter-spacing: 1px;
}

.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.8;
  margin: 0 0 32px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.brand-footer {
  position: absolute;
  bottom: 28px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

/* ========== 右侧表单面板 ========== */
.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 40px;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 36px;
}

.form-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.form-header p {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

/* ========== 表单元素 ========== */
.auth-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.auth-form :deep(.el-form-item__error) {
  font-size: 12px;
}

.auth-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  transition: all 0.25s;
}

.auth-input :deep(.el-input__wrapper:hover) {
  border-color: #94a3b8;
  background: #fff;
}

.auth-input :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: #fff;
}

.input-icon {
  color: #94a3b8;
  font-size: 16px;
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-row :deep(.el-checkbox__label) {
  font-size: 13px;
  color: #64748b;
}

.text-link {
  font-size: 13px;
  color: #3b82f6;
  font-weight: 500;
  text-decoration: none;
}

.text-link:hover {
  color: #2563eb;
}

.submit-btn {
  width: 100%;
  height: 46px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
  background: #1e3a5f;
  border-color: #1e3a5f;
  transition: all 0.3s;
}

.submit-btn:hover {
  background: #2d6a9f;
  border-color: #2d6a9f;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(30, 58, 95, 0.3);
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
  margin-top: 28px;
}

.form-footer .text-link {
  margin-left: 4px;
  font-size: 14px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .brand-panel {
    display: none;
  }

  .form-panel {
    padding: 32px 24px;
  }

  .form-wrapper {
    max-width: 100%;
  }

  .form-header h2 {
    font-size: 22px;
  }
}
</style>
