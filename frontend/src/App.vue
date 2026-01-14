<template>
  <v-app>
    <!-- Modern App Bar -->
    <v-app-bar v-if="$route.path !== '/login'" flat class="app-bar" elevation="0">
      <!-- Mobile Menu Button -->
      <v-btn icon class="mobile-menu-btn" @click="drawer = !drawer">
        <v-icon>mdi-dots-grid</v-icon>
      </v-btn>

      <!-- Logo & Brand -->
      <router-link to="/code" class="brand-link">
        <div class="brand">
          <div class="brand-icon">
            <v-icon size="20" color="white">mdi-cube-scan</v-icon>
          </div>
          <span class="brand-name">LLM Sec Guard</span>
        </div>
      </router-link>

      <!-- Navigation Pills (Desktop) -->
      <div class="nav-pills desktop-nav">
        <v-btn v-for="nav in navItems" :key="nav.path" :to="nav.path" exact variant="text" class="nav-pill" :class="{ active: isActive(nav) }">
          <v-icon start size="18">{{ nav.icon }}</v-icon>
          {{ nav.label }}
        </v-btn>
      </div>

      <v-spacer></v-spacer>

      <!-- User Menu (Desktop Only) -->
      <v-menu v-if="user.id" offset-y>
        <template v-slot:activator="{ props }">
          <div class="user-menu desktop-only" v-bind="props">
            <v-avatar class="user-avatar" size="36">
              <span class="avatar-text">{{ user.username ? user.username[0].toUpperCase() : '?' }}</span>
            </v-avatar>
            <v-icon size="16" class="dropdown-icon">mdi-chevron-down</v-icon>
          </div>
        </template>

        <v-list class="dropdown" rounded="lg">
          <!-- User Info -->
          <div class="user-info">
            <v-avatar size="48" class="user-avatar-large">
              <span class="avatar-text">{{ user.username ? user.username[0].toUpperCase() : '?' }}</span>
            </v-avatar>
            <div class="username">{{ user.username }}</div>
          </div>

          <v-divider class="my-2"></v-divider>

          <!-- Menu Items -->
          <v-list-item v-for="item in menuItems" :key="item.path" :to="item.path" exact class="menu-item">
            <template v-slot:prepend>
              <v-icon size="18">{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.label }}</v-list-item-title>
          </v-list-item>

          <v-divider class="my-2"></v-divider>

          <div class="logout-section">
            <v-btn color="error" variant="flat" block class="logout-btn" @click="$store.dispatch('logout')">
              <v-icon start size="18">mdi-logout</v-icon>
              Đăng Xuất
            </v-btn>
          </div>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Mobile Sidebar Navigation -->
    <v-navigation-drawer v-if="$route.path !== '/login'" v-model="drawer" temporary location="left" class="mobile-drawer">
      <!-- User Info Section (Mobile - when logged in) -->
      <div v-if="user.id" class="mobile-user-section">
        <div class="mobile-user-info">
          <v-avatar size="52" class="user-avatar-large">
            <span class="avatar-text">{{ user.username ? user.username[0].toUpperCase() : '?' }}</span>
          </v-avatar>
          <div class="username">{{ user.username }}</div>
        </div>
      </div>

      <!-- Guest Info Section (Mobile - when not logged in) -->
      <div v-else class="mobile-guest-section">
        <div class="guest-message">
          <v-icon size="40" color="#94a3b8">mdi-account-circle-outline</v-icon>
          <div class="guest-text">Chào mừng bạn đến với LLM Sec Guard</div>
        </div>
      </div>

      <v-divider></v-divider>

      <!-- Navigation Items -->
      <v-list class="drawer-list">
        <v-list-item v-for="nav in navItems" :key="nav.path" :to="nav.path" exact class="drawer-item" :class="{ active: isActive(nav) }" @click="drawer = false">
          <template v-slot:prepend>
            <v-icon size="20">{{ nav.icon }}</v-icon>
          </template>
          <v-list-item-title>{{ nav.label }}</v-list-item-title>
        </v-list-item>

        <v-divider class="my-2" v-if="user.id"></v-divider>

        <!-- User Menu Items (when logged in) -->
        <template v-if="user.id">
          <v-list-item v-for="item in menuItems" :key="item.path" :to="item.path" exact class="drawer-item" @click="drawer = false">
            <template v-slot:prepend>
              <v-icon size="20">{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.label }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>

      <!-- Drawer Footer -->
      <template v-slot:append>
        <div v-if="user.id" class="drawer-footer">
          <v-btn color="error" variant="flat" block class="drawer-logout-btn" @click="$store.dispatch('logout'); drawer = false">
            <v-icon start size="18">mdi-logout</v-icon>
            Đăng Xuất
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="main-content">
      <RouterView></RouterView>
    </v-main>

    <!-- Modern Snackbar Container -->
    <div class="snackbar-container">
      <v-snackbar v-for="(msg, i) in messages" :key="msg.id" :model-value="!isClosing(msg.id)" :color="msg.type || 'primary'" location="top right" class="snackbar" :class="`snackbar-${i}`" rounded="lg" :style="{ top: `${16 + i * 72}px` }" @mouseenter="handleMouseEnter(msg)" @mouseleave="handleMouseLeave(msg)">
        <div class="snackbar-content">
          <!-- Icon with Circular Progress -->
          <div class="icon-wrapper">
            <svg class="progress-ring" width="32" height="32">
              <circle class="progress-ring-bg" cx="16" cy="16" r="14" :stroke="getIconColor(msg.type)" />
              <circle class="progress-ring-circle" cx="16" cy="16" r="14" :stroke="getIconColor(msg.type)" :style="{ strokeDasharray: '88 88', strokeDashoffset: getProgressOffset(msg.id), transition: messageProgresses[msg.id]?.paused ? 'none' : 'stroke-dashoffset 0.1s linear' }" />
            </svg>
            <v-icon :color="getIconColor(msg.type)" size="18" class="progress-icon">
              {{ getIcon(msg.type) }}
            </v-icon>
          </div>
          <span class="message-text">{{ msg.text }}</span>
        </div>

        <template v-slot:actions>
          <v-btn icon size="small" variant="text" class="snackbar-close-btn" @click="closeMessage(msg.id)">
            <v-icon size="18" color="#64748b">mdi-close</v-icon>
          </v-btn>
        </template>
      </v-snackbar>
    </div>
  </v-app>
</template>

<script>
import { mapState } from "vuex";

export default {
  data: () => ({
    drawer: false,
    hoveredMessages: {},
    messageProgresses: {},
    navItems: [
      { path: '/code', label: 'Soạn Mã', icon: 'mdi-code-json', query: null },
      { path: '/code?prompt=true', label: 'Yêu Cầu', icon: 'mdi-creation', query: 'true' },
      { path: '/overview', label: 'Tổng Quan', icon: 'mdi-view-dashboard-outline', query: null }
    ],
    menuItems: [
      { path: '/models', label: 'Mô Hình', icon: 'mdi-robot-outline' },
      { path: '/analyzers', label: 'Phân Tích', icon: 'mdi-chart-timeline-variant-shimmer' },
      { path: '/vulnerability', label: 'Lỗ Hổng', icon: 'mdi-bug-outline' },
      { path: '/rule', label: 'Quy Tắc', icon: 'mdi-file-document-outline' }
    ]
  }),
  computed: mapState({
    user: (state) => state.user || {},
    messages: (state) => state.messages || [],
    closingMessages: (state) => state.closingMessages || {}
  }),
  watch: {
    messages: {
      handler(newMessages) {
        newMessages.forEach(msg => {
          if (!this.messageProgresses[msg.id]) {
            this.messageProgresses[msg.id] = { progress: 0, timeout: msg.timeout || 5000, startTime: Date.now(), paused: false };
            this.startProgress(msg.id);
          }
        });

        Object.keys(this.messageProgresses).forEach(id => {
          if (!newMessages.find(m => m.id === id)) delete this.messageProgresses[id];
        });
      },
      deep: true
    }
  },
  methods: {
    isActive(nav) {
      return nav.query ? this.$route.query.prompt === nav.query : this.$route.path === nav.path && !this.$route.query.prompt;
    },
    isClosing(messageId) {
      return this.closingMessages[messageId] === true;
    },
    closeMessage(messageId) {
      this.$store.commit('setClosingMessage', messageId);
      setTimeout(() => this.$store.commit('removeMessage', messageId), 300);
    },
    getIcon(type) {
      const icons = { success: 'mdi-check-circle', error: 'mdi-close-circle', warning: 'mdi-alert-circle', info: 'mdi-information' };
      return icons[type] || 'mdi-information';
    },
    getIconColor(type) {
      const colors = { success: '#10b981', error: '#ef4444', warning: '#f59e0b', info: '#3b82f6' };
      return colors[type] || '#3b82f6';
    },
    getProgressOffset(messageId) {
      const progress = this.messageProgresses[messageId];
      if (!progress) return 88;
      return 88 - (progress.progress / 100) * 88;
    },
    startProgress(messageId) {
      const progress = this.messageProgresses[messageId];
      if (!progress || progress.paused) return;
  
      const animate = () => {
        if (!this.messageProgresses[messageId] || this.messageProgresses[messageId].paused) return;
        
        const elapsed = Date.now() - progress.startTime;
        const totalTimeout = this.messages.find(m => m.id === messageId)?.timeout || 5000;
        const percentage = Math.min((elapsed / totalTimeout) * 100, 100);
        
        this.messageProgresses[messageId].progress = percentage;
        
        if (percentage < 100) {
          requestAnimationFrame(animate);
        }
      };
  
      requestAnimationFrame(animate);
    },
    handleMouseEnter(msg) {
      this.hoveredMessages[msg.id] = { 
        hoveredAt: Date.now() 
      };
      
      if (this.messageProgresses[msg.id]) {
        this.messageProgresses[msg.id].paused = true;
        this.messageProgresses[msg.id].pausedAt = Date.now();
      }
      
      this.$store.dispatch('pauseMessageTimer', msg.id);
    },
    handleMouseLeave(msg) {
      if (this.hoveredMessages[msg.id]) {
        const progress = this.messageProgresses[msg.id];
        
        if (progress) {
          const remainingPercentage = 100 - progress.progress;
          const totalTimeout = msg.timeout || 5000;
          const remainingTimeout = Math.max((remainingPercentage / 100) * totalTimeout, 1000);
          
          progress.paused = false;
          progress.startTime = Date.now() - (progress.progress / 100) * totalTimeout;
          
          this.startProgress(msg.id);
          
          this.$store.dispatch('resumeMessageTimer', { 
            messageId: msg.id, 
            timeout: remainingTimeout 
          });
        }
        
        delete this.hoveredMessages[msg.id];
      }
    }
  }
};
</script>

<style scoped>
/* App Bar */
.app-bar { background: #ffffff !important; border-bottom: 1px solid #e2e8f0; padding: 0 28px; height: 64px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

/* Mobile Menu Button */
.mobile-menu-btn { display: none; margin-right: 12px; }

/* Brand Link */
.brand-link { text-decoration: none; display: flex; align-items: center; }

/* Brand */
.brand { display: flex; align-items: center; gap: 12px; margin-right: 32px; cursor: pointer; }
.brand-icon { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 10px; box-shadow: 0 4px 16px rgba(99,102,241,0.25); }
.brand-name { font-size: 16px; font-weight: 700; color: #0f172a; letter-spacing: -0.3px; }

/* Navigation */
.nav-pills { display: flex; gap: 6px; padding: 4px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }
.nav-pill { color: #64748b !important; text-transform: none; font-weight: 500; font-size: 14px; padding: 0 16px !important; height: 36px !important; border-radius: 8px !important; transition: all 0.2s ease; }
.nav-pill:hover { background: #f1f5f9 !important; color: #334155 !important; }
.nav-pill.active { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; box-shadow: 0 2px 8px rgba(99,102,241,0.25); }

/* User Menu */
.user-menu { display: flex; align-items: center; gap: 8px; padding: 4px 12px 4px 4px; margin-right: 28px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 24px; cursor: pointer; transition: all 0.2s ease; }
.user-menu:hover { background: #f1f5f9; border-color: #cbd5e1; }
.user-avatar { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; box-shadow: 0 2px 8px rgba(99,102,241,0.25); }
.user-avatar-large { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
.avatar-text { font-size: 14px; font-weight: 600; color: white; }
.dropdown-icon { color: #64748b; transition: transform 0.2s ease; }
.user-menu:hover .dropdown-icon { transform: translateY(1px); }

/* Dropdown */
.dropdown { background: #ffffff !important; border: 1px solid #e2e8f0; min-width: 260px; padding: 8px; margin-top: 8px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
.user-info { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8fafc; border-radius: 10px; margin-bottom: 4px; border: 1px solid #f1f5f9; }
.username { font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
.menu-item { border-radius: 8px; margin: 2px 0; transition: all 0.2s ease; }
.menu-item:hover { background: #f8fafc !important; }
.menu-item :deep(.v-list-item-title) { font-size: 14px; font-weight: 500; color: #334155; }
.menu-item :deep(.v-icon) { color: #64748b; margin-right: 12px; }
.logout-section { padding: 8px; }
.logout-btn { text-transform: none; font-weight: 600; font-size: 14px; height: 38px !important; border-radius: 8px !important; }

/* Main Content */
.main-content { background: #f8fafc; min-height: calc(100vh - 64px); }

/* Mobile Drawer */
.mobile-drawer { background: #ffffff; border-right: 1px solid #e2e8f0; }

/* Mobile User Section */
.mobile-user-section { padding: 20px 16px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-bottom: 1px solid #e2e8f0; }
.mobile-user-info { display: flex; align-items: center; gap: 14px; }

/* Mobile Guest Section */
.mobile-guest-section { padding: 24px 16px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-bottom: 1px solid #e2e8f0; }
.guest-message { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; }
.guest-text { font-size: 14px; color: #64748b; font-weight: 500; line-height: 1.5; }

/* Drawer List */
.drawer-list { padding: 8px; }
.drawer-item { border-radius: 10px; margin: 4px 0; transition: all 0.2s ease; }
.drawer-item:hover { background: #f8fafc !important; }
.drawer-item.active { background: #ede9fe !important; }
.drawer-item.active :deep(.v-list-item-title) { color: #6366f1; font-weight: 600; }
.drawer-item.active :deep(.v-icon) { color: #6366f1; }
.drawer-item :deep(.v-list-item-title) { font-size: 15px; font-weight: 500; color: #334155; }
.drawer-item :deep(.v-icon) { color: #64748b; margin-right: 12px; }
.drawer-footer { padding: 16px; border-top: 1px solid #f1f5f9; background: #fafbfc; }
.drawer-logout-btn { text-transform: none; font-weight: 600; font-size: 14px; height: 44px !important; border-radius: 10px !important; }

/* Snackbar Container */
.snackbar-container { position: fixed; top: 0; right: 0; z-index: 9999; }
.snackbar { position: fixed !important; transition: all 0.3s ease; }
.snackbar :deep(.v-snackbar__wrapper) { background: #ffffff !important; border: 1px solid #e2e8f0; box-shadow: 0 10px 40px rgba(0,0,0,0.15); border-radius: 12px; padding: 4px; min-width: 350px; cursor: pointer; }
.snackbar:hover :deep(.v-snackbar__wrapper) { box-shadow: 0 12px 48px rgba(0,0,0,0.2); border-color: #cbd5e1; }
.snackbar-content { display: flex; align-items: center; font-size: 14px; font-weight: 500; color: #0f172a; gap: 12px; }
.message-text { flex: 1; }

/* Circular Progress Icon */
.icon-wrapper { position: relative; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.progress-ring { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-90deg); }
.progress-ring-bg { fill: none; stroke-width: 2; opacity: 0.15; }
.progress-ring-circle { fill: none; stroke-width: 2.5; stroke-linecap: round; }
.progress-icon { position: relative; z-index: 1; }
.snackbar-close-btn { opacity: 0.7; transition: opacity 0.2s; }
.snackbar-close-btn:hover { opacity: 1; }

/* Responsive */
@media (max-width: 960px) {
  .app-bar { padding: 0 16px; }
  .mobile-menu-btn { display: inline-flex; }
  .desktop-nav { display: none; }
  .desktop-only { display: none !important; }
  .brand { margin-right: 0; }
  .snackbar :deep(.v-snackbar__wrapper) { min-width: 280px; }
}
</style>

<style>
/* Global Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f8fafc; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Overlay */
.v-overlay .v-overlay__scrim { background-color: rgba(0, 0, 0, 0.4) !important; backdrop-filter: blur(4px); opacity: 1 !important; }

/* Dropdown Lists */
.v-list { background: #ffffff !important; border: 1px solid #e2e8f0; }
.v-list-item { border-radius: 8px; margin: 2px 4px; }
.v-list-item:hover { background: #f8fafc !important; }
.v-list-item--active { background: #ede9fe !important; color: #6366f1 !important; }
</style>