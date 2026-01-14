<template>
  <v-container fluid class="overview-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <v-icon size="20" color="white">mdi-chart-box-outline</v-icon>
        </div>
        <div>
          <h2 class="header-title">Đánh Giá Hiệu Năng</h2>
          <p class="header-subtitle">Các chỉ số hiệu năng và kết quả phân tích</p>
        </div>
      </div>
      <v-btn variant="flat" color="primary" :loading="loading" @click="getData" class="refresh-btn" rounded="lg">
        <v-icon start size="18">mdi-refresh</v-icon>
        Làm Mới Dữ Liệu
      </v-btn>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid" v-if="overview.length > 0">
      <div class="stat-card">
        <div class="stat-icon total">
          <v-icon size="24" color="white">mdi-database</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">Tổng Số Bài Kiểm Thử</div>
          <div class="stat-value">{{ totalTests }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon models">
          <v-icon size="24" color="white">mdi-robot</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">Mô Hình Đã Kiểm Thử</div>
          <div class="stat-value">{{ uniqueModels }}</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon score">
          <v-icon size="24" color="white">mdi-star</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">Điểm Trung Bình</div>
          <div class="stat-value">{{ averageScore }}/100</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon branches">
          <v-icon size="24" color="white">mdi-source-branch</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">Nhánh</div>
          <div class="stat-value">{{ uniqueBranches }}</div>
        </div>
      </div>
    </div>

    <!-- Table Card -->
    <div class="table-card">
      <v-data-table
        :headers="headers"
        :items="overview"
        :loading="loading"
        item-key="id"
        class="modern-table"
        density="comfortable"
        :items-per-page="10"
        :items-per-page-options="[
          { value: 10, title: '10' },
          { value: 25, title: '25' },
          { value: 50, title: '50' },
          { value: 100, title: '100' },
          { value: -1, title: 'Tất cả' }
        ]"
        :items-per-page-text="'Số bản ghi:'"
        :page-text="'{0}-{1} trên {2}'"
      >
        <template v-slot:loading>
          <div class="loading-state">
            <v-progress-circular color="#8b5cf6" indeterminate size="48"></v-progress-circular>
            <p class="loading-text">Đang tải dữ liệu đánh giá...</p>
          </div>
        </template>

        <template v-slot:no-data>
          <div class="empty-state">
            <div class="empty-icon">
              <v-icon size="64" color="#cbd5e1">mdi-emoticon-dead-outline</v-icon>
            </div>
            <h3 class="empty-title">Chưa Có Dữ Liệu Kiểm Thử</h3>
          </div>
        </template>

        <template v-slot:item.objects.model.name="{ item }">
          <div class="model-cell">
            <div class="model-icon">
              <v-icon size="16" color="white">mdi-robot-outline</v-icon>
            </div>
            <span class="model-name">{{ item.objects.model.name }}</span>
          </div>
        </template>

        <template v-slot:item.objects.branch="{ item }">
          <div class="branch-badge">
            <v-icon size="14" class="mr-1">mdi-source-branch</v-icon>
            {{ item.objects.branch }}
          </div>
        </template>

        <template v-slot:item.totalScore="{ item }">
          <div class="score-cell">
            <div class="score-bar">
              <div class="score-fill" :style="{ 
                width: calculateTotalScore(item) + '%',
                background: getScoreGradient(calculateTotalScore(item))
              }"></div>
            </div>
            <span class="score-value">{{ calculateTotalScore(item) }}/100</span>
          </div>
        </template>

        <template v-slot:item.open="{ item }">
          <v-btn :to="`/overview/${tobase64(JSON.stringify(item))}/`" variant="flat" color="primary" size="small" class="action-btn" rounded="lg">
            <v-icon start size="16">mdi-eye-outline</v-icon>
            Xem Chi Tiết
          </v-btn>
        </template>
      </v-data-table>
    </div>
  </v-container>
</template>

<script>
import axios from "@/plugins/axios";
import { defineComponent } from "vue";

export default defineComponent({
  data: () => ({
    loading: false,
    overview: [],
    headers: [
      { title: "Mô Hình", value: "objects.model.name", sortable: true },
      { title: "Nhánh", value: "objects.branch", sortable: true },
      { title: "Tổng Điểm", value: "totalScore", sortable: true },
      { title: "Thao Tác", value: "open", align: "center", sortable: false },
    ],
  }),
  computed: {
    totalTests() {
      return this.overview.reduce((sum, item) => {
        const injectionTests = (item.injection_successful_count || 0) + (item.injection_unsuccessful_count || 0);
        const maliciousTests = (item.is_extremely_malicious || 0) + (item.is_potentially_malicious || 0) + (item.is_non_malicious || 0);
        return sum + injectionTests + maliciousTests;
      }, 0);
    },
    uniqueModels() {
      return new Set(this.overview.map(item => item.objects?.model?.name).filter(Boolean)).size;
    },
    uniqueBranches() {
      return new Set(this.overview.map(item => item.objects?.branch).filter(Boolean)).size;
    },
    averageScore() {
      if (this.overview.length === 0) return 0;
      const total = this.overview.reduce((sum, item) => sum + this.calculateTotalScore(item), 0);
      return Math.round(total / this.overview.length);
    },
  },
  mounted() {
    this.getData();
  },
  methods: {
    tobase64(str) {
      return btoa(str);
    },
    calculateInjectionResistance(item) {
      const successful = item.injection_successful_count || 0;
      const unsuccessful = item.injection_unsuccessful_count || 0;
      const total = successful + unsuccessful;
      return total === 0 ? 0 : Math.round((unsuccessful / total) * 100);
    },
    calculateSecurityScore(item) {
      const extremely = item.is_extremely_malicious || 0;
      const potentially = item.is_potentially_malicious || 0;
      const nonMalicious = item.is_non_malicious || 0;
      const total = extremely + potentially + nonMalicious;
      return total === 0 ? 0 : Math.round((nonMalicious / total) * 100);
    },
    calculateTotalScore(item) {
      const injectionResistance = this.calculateInjectionResistance(item);
      const security = this.calculateSecurityScore(item);
      const injectionTotal = (item.injection_successful_count || 0) + (item.injection_unsuccessful_count || 0);
      const maliciousTotal = (item.is_extremely_malicious || 0) + (item.is_potentially_malicious || 0) + (item.is_non_malicious || 0);
      
      if (injectionTotal === 0 && maliciousTotal === 0) return 0;
      if (injectionTotal === 0) return security;
      if (maliciousTotal === 0) return injectionResistance;
      
      return Math.min(Math.round((injectionResistance * 0.6) + (security * 0.4)), 100);
    },
    async getData() {
      this.loading = true;
      try {
        const { data } = await axios.get("/benchmark-agent/benchmark/overview/");
        this.overview = (data || []).map(item => ({
          ...item,
          totalScore: this.calculateTotalScore(item)
        }));
      } catch (err) {
        console.error(err);
      }
      this.loading = false;
    },
    getScoreGradient(score) {
      if (score >= 80) return '#10b981';
      if (score >= 60) return '#f59e0b';
      return '#ef4444';
    }
  },
});
</script>

<style scoped>
.overview-container { background: #f8fafc; min-height: 100vh; padding: 32px; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
.header-left { display: flex; align-items: center; gap: 16px; }
.header-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; box-shadow: 0 4px 16px rgba(99,102,241,0.25); }
.header-title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.5px; }
.header-subtitle { font-size: 14px; color: #64748b; margin: 4px 0 0; }
.refresh-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; padding: 0 24px !important; height: 40px !important; box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.refresh-btn:hover { box-shadow: 0 6px 20px rgba(99,102,241,0.35); transform: translateY(-1px); }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 28px; }
.stat-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; display: flex; align-items: center; gap: 16px; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.stat-card:hover { border-color: #cbd5e1; box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-2px); }
.stat-icon { width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 12px; flex-shrink: 0; }
.stat-icon.total { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); box-shadow: 0 4px 16px rgba(99,102,241,0.25); }
.stat-icon.models { background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 4px 16px rgba(16,185,129,0.25); }
.stat-icon.score { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); box-shadow: 0 4px 16px rgba(245,158,11,0.25); }
.stat-icon.branches { background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); box-shadow: 0 4px 16px rgba(236,72,153,0.25); }
.stat-content { flex: 1; }
.stat-label { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.stat-value { font-size: 28px; font-weight: 700; color: #0f172a; line-height: 1; }

/* Table Card */
.table-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.modern-table { background: transparent !important; }
.modern-table :deep(th) { background: #f8fafc !important; color: #475569 !important; font-weight: 700 !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0 !important; padding: 16px !important; }
.modern-table :deep(td) { background: transparent !important; color: #334155 !important; border-bottom: 1px solid #f1f5f9 !important; padding: 16px !important; font-size: 14px; }
.modern-table :deep(tr:hover td) { background: #f8fafc !important; }
.modern-table :deep(.v-data-table-footer) { background: #fafbfc !important; border-top: 1px solid #e2e8f0; color: #64748b !important; }
.modern-table :deep(.v-data-table-progress) { display: none !important; }

/* Loading & Empty State */
.loading-state, .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center; }
.empty-state { padding: 80px 20px; }
.loading-state { gap: 16px; }
.loading-text { font-size: 14px; color: #cbd5e1; margin: 0; }
.empty-icon { margin-bottom: 20px; opacity: 0.5; }
.empty-title { font-size: 20px; font-weight: 700; color: #cbd5e1; margin: 0 0 8px 0; }
.empty-text { font-size: 14px; color: #64748b; margin: 0; }

/* Model Cell */
.model-cell { display: flex; align-items: center; gap: 10px; }
.model-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px; box-shadow: 0 2px 8px rgba(99,102,241,0.25); flex-shrink: 0; }
.model-name { font-weight: 600; color: #0f172a; }

/* Branch Badge */
.branch-badge { display: inline-flex; align-items: center; padding: 6px 12px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; color: #059669; font-size: 13px; font-weight: 600; }

/* Score Cell */
.score-cell { display: flex; align-items: center; gap: 12px; }
.score-bar { flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.score-fill { height: 100%; border-radius: 4px; transition: all 0.3s ease; }
.score-value { font-weight: 700; color: #0f172a; min-width: 60px; text-align: right; }

/* Action Button */
.action-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; transition: all 0.3s ease; }
.action-btn:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.35); transform: translateY(-1px); }

/* Responsive */
@media (max-width: 960px) {
  .overview-container { padding: 20px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
  .stat-card { padding: 16px; }
  .stat-icon { width: 48px; height: 48px; }
  .stat-value { font-size: 24px; }
}
</style>