<template>
  <div class="header-container">
    <div class="top-nav">
      <el-menu
        mode="horizontal"
        :default-active="activePath"
        @select="onSelect"
        class="top-menu"
      >
        <el-menu-item index="/detection">智能检测</el-menu-item>
        <el-menu-item index="/history">历史记录</el-menu-item>
        <el-menu-item index="/qa">AI问答</el-menu-item>
        <el-menu-item index="/targets">目标库</el-menu-item>
        <el-menu-item index="/profile">个人中心</el-menu-item>
      </el-menu>
    </div>

    <div class="header-actions">
      <div class="action-icons">
        <el-icon class="action-icon"><Bell /></el-icon>
      </div>

      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <el-avatar class="user-avatar" size="32">
            <img
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              alt="用户头像"
            />
          </el-avatar>
          <div class="user-info">
            <div class="user-name">{{ userName }}</div>
            <div class="user-role">普通用户</div>
          </div>
          <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              账号设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Bell,
  CaretBottom,
  User,
  Setting,
  SwitchButton,
} from "@element-plus/icons-vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const activePath = route.path;

// 从 localStorage 读取用户名（登录时保存）
const userName = ref(localStorage.getItem("username") || "用户");

const onSelect = (index) => {
  if (index) router.push(index);
};

const handleCommand = (command) => {
  if (command === "profile") {
    router.push("/profile");
  } else if (command === "settings") {
    router.push("/profile");
  } else if (command === "logout") {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    router.push("/login");
  }
};
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.top-nav .el-menu {
  display: flex;
  align-items: center;
  gap: 18px;
}

.top-nav .el-menu-item {
  white-space: nowrap;
  padding: 8px 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-icons {
  display: flex;
  align-items: center;
}

.action-icon {
  font-size: 18px;
  color: var(--text-secondary);
  margin-right: 16px;
  cursor: pointer;
  transition: color 0.2s;
}

.action-icon:hover {
  color: var(--primary-color);
}

/* ====== 用户下拉 ====== */
.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 8px;
  transition: background-color 0.2s;
  outline: none;
}

.user-dropdown:hover {
  background-color: #f3f4f6;
}

.user-avatar {
  margin-right: 8px;
  flex-shrink: 0;
}

.user-info {
  margin-right: 6px;
  line-height: 1.3;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-secondary);
  transition: transform 0.2s;
}

/* 下拉菜单项样式 */
:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  padding: 10px 16px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}
</style>
