<template>
  <v-container fluid class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <div class="header-icon">
          <v-icon size="20" color="white">mdi-robot-outline</v-icon>
        </div>
        <div>
          <h2 class="title">Hiệu Năng Mô Hình</h2>
          <p class="subtitle">Phân tích chi tiết và các chỉ số</p>
        </div>
      </div>
      <v-btn variant="flat" color="primary" class="back-btn" rounded="lg" @click="$router.back()">
        <v-icon start size="18">mdi-arrow-left</v-icon>
        Quay Lại Trang Tổng Quan
      </v-btn>
    </div>

    <!-- Model Info Card -->
    <div class="card">
      <div class="card-header">
        <div class="flex-left">
          <div class="dot"></div>
          <span class="label">Thông Tin Mô Hình</span>
        </div>
      </div>
      
      <div class="card-body">
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">
              <v-icon size="16" class="mr-2" color="#6366f1">mdi-robot</v-icon>
              Tên Mô Hình
            </div>
            <div class="info-value model-name">{{ modelInfo.name }}</div>
            <div class="info-desc" v-if="modelInfo.description">{{ modelInfo.description }}</div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <v-icon size="16" class="mr-2" color="#10b981">mdi-source-branch</v-icon>
              Nhánh
            </div>
            <div class="branch-badge">
              <v-icon size="14" class="mr-1">mdi-source-branch</v-icon>
              {{ data.objects?.branch }}
            </div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <v-icon size="16" class="mr-2" color="#f59e0b">mdi-star</v-icon>
              Tổng Điểm
            </div>
            <div class="score-row">
              <div class="info-value">{{ metrics.totalScore }}/100</div>
              <div class="safety-badge" :style="riskLevel.style">{{ riskLevel.text }}</div>
            </div>
          </div>

          <div class="info-item">
            <div class="info-label">
              <v-icon size="16" class="mr-2" color="#ec4899">mdi-file-document-multiple</v-icon>
              Tổng Số Bài Kiểm Thử
            </div>
            <div class="info-value">{{ metrics.totalTests }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart Card -->
    <div class="card">
      <div class="card-header">
        <div class="flex-left">
          <div class="dot chart"></div>
          <span class="label">Xu Hướng Hiệu Năng</span>
        </div>
        <div class="legend" v-if="!loading && hasChartData">
          <div 
            v-for="(item, idx) in legendItems" 
            :key="idx"
            class="legend-item" 
            :class="{ 'legend-disabled': !seriesVisibility[idx] }"
            @click="toggleSeries(idx)"
          >
            <div class="legend-dot" :class="item.class"></div>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>

      <div class="card-body">
        <div v-if="loading" class="loading">
          <v-progress-circular color="#8b5cf6" indeterminate size="48"></v-progress-circular>
          <p class="loading-text">Đang tải dữ liệu hiệu năng...</p>
        </div>
        <div v-else-if="!hasChartData" class="loading">
          <v-icon size="48" color="#cbd5e1">mdi-emoticon-dead-outline</v-icon>
          <h4 class="empty-title">Chưa Có Dữ Liệu Hiệu Năng</h4>
        </div>
        <apexchart 
          v-else
          ref="chart" 
          type="bar" 
          :options="chartOptions" 
          :series="visibleChartSeries" 
          height="380"
        ></apexchart>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="section-header">
        <v-icon size="20" class="mr-2" color="#6366f1">mdi-chart-box</v-icon>
        <span class="section-title">Thống Kê Chi Tiết</span>
      </div>

      <div class="stats-grid">
        <!-- Malicious Detection -->
        <div class="stat-card">
          <div class="stat-header">
            <v-icon size="20" color="#ef4444">mdi-skull-outline</v-icon>
            <span>Phát Hiện Mã Độc</span>
          </div>
          <div class="stat-body">
            <div class="stat-row">
              <span class="stat-label">Cực Kỳ Nguy Hiểm</span>
              <span class="stat-value danger">{{ metrics.extremely }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Có Khả Năng Nguy Hiểm</span>
              <span class="stat-value warning">{{ metrics.potentially }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Không Nguy Hiểm</span>
              <span class="stat-value success">{{ metrics.nonMalicious }}</span>
            </div>
            <div class="divider"></div>
            <div class="progress-item">
              <div class="progress-label-row">
                <span class="stat-label">Tỉ Lệ Nguy Hiểm</span>
                <span class="stat-value">{{ metrics.maliciousPercentage }}%</span>
              </div>
              <div class="progress-container">
                <div class="progress-fill" :style="{ 
                  width: metrics.maliciousPercentage + '%',
                  background: getRiskColor(metrics.maliciousPercentage)
                }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Injection Results -->
        <div class="stat-card">
          <div class="stat-header">
            <v-icon size="20" color="#10b981">mdi-needle</v-icon>
            <span>Phân Tích Tiêm Mã</span>
          </div>
          <div class="stat-body">
            <div class="stat-row">
              <span class="stat-label">Bị Tiêm Mã Thành Công</span>
              <span class="stat-value danger">{{ metrics.injectionSuccess }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Chặn Tiêm Mã Thành Công</span>
              <span class="stat-value success">{{ metrics.injectionFail }}</span>
            </div>
            <div class="divider"></div>
            <div class="progress-item">
              <div class="progress-label-row">
                <span class="stat-label">Tỉ Lệ Bị Tấn Công</span>
                <span class="stat-value">{{ metrics.injectionSuccessRate }}%</span>
              </div>
              <div class="progress-container">
                <div class="progress-fill" :style="{ 
                  width: metrics.injectionSuccessRate + '%',
                  background: getRiskColor(metrics.injectionSuccessRate)
                }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Overall Metrics -->
        <div class="stat-card">
          <div class="stat-header">
            <v-icon size="20" color="#6366f1">mdi-chart-bar</v-icon>
            <span>Chỉ Số Tổng Hợp</span>
          </div>
          <div class="stat-body">
            <div class="stat-row">
              <span class="stat-label">Tổng Số Bài Kiểm Thử</span>
              <span class="stat-value primary">{{ metrics.totalTests }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Kiểm Thử Tiêm Mã</span>
              <span class="stat-value">{{ metrics.injectionTestCount }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Kiểm Thử Phát Hiện Mã Độc</span>
              <span class="stat-value">{{ metrics.maliciousTestCount }}</span>
            </div>
            <div class="divider"></div>
            <div class="progress-item">
              <div class="progress-label-row">
                <span class="stat-label">Khả Năng Chống Tiêm Mã</span>
                <span class="stat-value">{{ metrics.injectionResistance }}%</span>
              </div>
              <div class="progress-container">
                <div class="progress-fill success-fill" :style="{ width: metrics.injectionResistance + '%' }"></div>
              </div>
            </div>
            <div class="progress-item">
              <div class="progress-label-row">
                <span class="stat-label">Độ Bảo Mật Mã Nguồn</span>
                <span class="stat-value">{{ metrics.securityScore }}%</span>
              </div>
              <div class="progress-container">
                <div class="progress-fill" :style="{ 
                  width: metrics.securityScore + '%',
                  background: getSecurityColor(metrics.securityScore)
                }"></div>
              </div>
            </div>
            <div class="divider"></div>
            <div class="progress-item">
              <div class="progress-label-row">
                <span class="stat-label">Tổng Điểm</span>
                <span class="stat-value">{{ metrics.totalScore }}/100</span>
              </div>
              <div class="progress-container">
                <div class="progress-fill" :style="{ 
                  width: metrics.totalScore + '%',
                  background: getSecurityColor(metrics.totalScore)
                }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script>
import axios from "@/plugins/axios";
import { defineComponent } from "vue";
import VueApexCharts from "vue3-apexcharts";

export default defineComponent({
  components: { 
    apexchart: VueApexCharts
  },
  data: () => ({
    loading: false,
    data: {},
    seriesVisibility: [true, true],
    rawChartData: null,
    legendItems: [
      { label: 'Lượt Sử Dụng', class: 'usage' },
      { label: 'Lỗi', class: 'errors' }
    ]
  }),
  computed: {
    modelInfo() {
      return this.data.objects?.model || {};
    },
    hasChartData() {
      return this.rawChartData?.length > 0;
    },
    chartOptions() {
      const categories = this.rawChartData?.map(d => d.date) || [];
      return {
        theme: { mode: "light" },
        chart: {
          toolbar: { show: false },
          foreColor: "#64748b",
          background: 'transparent',
          fontFamily: 'Inter, system-ui, sans-serif',
          stacked: false,
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 400,
            animateGradually: {
              enabled: true,
              delay: 80
            },
            dynamicAnimation: {
              enabled: true,
              speed: 400
            }
          }
        },
        plotOptions: {
          bar: {
            borderRadius: 8,
            borderRadiusApplication: 'end',
            columnWidth: '60%',
            dataLabels: { position: 'top' }
          }
        },
        dataLabels: { enabled: false },
        xaxis: {
          categories,
          labels: { style: { colors: "#64748b", fontSize: '12px' } },
          axisBorder: { color: '#e2e8f0' },
          axisTicks: { color: '#e2e8f0' }
        },
        yaxis: {
          labels: { style: { colors: "#64748b", fontSize: '12px' } }
        },
        legend: { show: false },
        grid: { 
          borderColor: "#e2e8f0",
          strokeDashArray: 4
        },
        tooltip: {
          theme: 'light',
          style: { fontSize: '12px' }
        }
      };
    },
    chartSeries() {
      if (!this.hasChartData) return [];

      return [
        { 
          name: "Usage", 
          color: "#10b981",
          data: this.rawChartData.map(d => d.usage ?? 0)
        },
        { 
          name: "Errors", 
          color: "#ef4444",
          data: this.rawChartData.map(d => d.errors ?? 0)
        }
      ];
    },
    visibleChartSeries() {
      if (!this.hasChartData) return [];

      return this.chartSeries.filter((_, idx) => this.seriesVisibility[idx]);
    },
    metrics() {
      const extremely = this.data.is_extremely_malicious || 0;
      const potentially = this.data.is_potentially_malicious || 0;
      const nonMalicious = this.data.is_non_malicious || 0;
      const injectionSuccess = this.data.injection_successful_count || 0;
      const injectionFail = this.data.injection_unsuccessful_count || 0;
      
      const totalMalicious = extremely + potentially + nonMalicious;
      const totalInjection = injectionSuccess + injectionFail;
      const maliciousCount = extremely + potentially;
      
      const injectionResistance = totalInjection ? Math.round((injectionFail / totalInjection) * 100) : 0;
      const injectionSuccessRate = totalInjection ? Math.round((injectionSuccess / totalInjection) * 100) : 0;
      const securityScore = totalMalicious ? Math.round((nonMalicious / totalMalicious) * 100) : 0;
      const maliciousPercentage = totalMalicious ? Math.round((maliciousCount / totalMalicious) * 100) : 0;
      
      let totalScore = 0;
      if (totalInjection && totalMalicious) {
        totalScore = Math.min(Math.round(injectionResistance * 0.6 + securityScore * 0.4), 100);
      } else if (totalInjection) {
        totalScore = injectionResistance;
      } else if (totalMalicious) {
        totalScore = securityScore;
      }
      
      return {
        injectionResistance,
        injectionSuccessRate,
        securityScore,
        maliciousPercentage,
        totalScore,
        totalTests: totalInjection + totalMalicious,
        injectionTestCount: totalInjection,
        maliciousTestCount: totalMalicious,
        extremely,
        potentially,
        nonMalicious,
        injectionSuccess,
        injectionFail
      };
    },
    riskLevel() {
      const { totalScore } = this.metrics;
      const levels = [
        { min: 80, text: 'Rất An Toàn', bg: '#ecfdf5', border: '#a7f3d0', color: '#059669' },
        { min: 60, text: 'Tương Đối An Toàn', bg: '#fef3c7', border: '#fcd34d', color: '#d97706' },
        { min: 40, text: 'Có Rủi Ro', bg: '#fee2e2', border: '#fca5a5', color: '#dc2626' },
        { min: 0, text: 'Nguy Hiểm', bg: '#fee2e2', border: '#fca5a5', color: '#dc2626' }
      ];
      
      const level = levels.find(l => totalScore >= l.min);
      return {
        text: level.text,
        style: {
          background: level.bg,
          borderColor: level.border,
          color: level.color
        }
      };
    }
  },
  mounted() {
    this.data = this.parseRouteData();
    this.fetchChartData();
  },
  methods: {
    parseRouteData() {
      try {
        return JSON.parse(atob(this.$route.params.object));
      } catch (err) {
        console.error("Error parsing route data:", err);
        return {};
      }
    },
    async fetchChartData() {
      this.loading = true;
      try {
        const { data } = await axios.get("/benchmark-agent/monthly-sum-cache/chart_data/", {
          params: { model: this.modelInfo.id },
        });
        
        this.rawChartData = Array.isArray(data) && data.length > 0
          ? data.map(item => ({
              date: item.date || 'N/A',
              usage: Number(item.usage) || 0,
              errors: Number(item.errors) || 0
            }))
          : [];
      } catch (err) {
        console.error("Error fetching chart data:", err);
        this.rawChartData = [];
      } finally {
        this.loading = false;
      }
    },
    toggleSeries(index) {
      this.seriesVisibility[index] = !this.seriesVisibility[index];
      this.seriesVisibility = [...this.seriesVisibility];
    },
    getSecurityColor(score) {
      if (score >= 80) return '#10b981';
      if (score >= 60) return '#f59e0b';
      return '#ef4444';
    },
    getRiskColor(score) {
      if (score <= 20) return '#10b981';
      if (score <= 40) return '#f59e0b';
      return '#ef4444';
    }
  }
});
</script>

<style scoped>
.container { background: #f8fafc; min-height: 100vh; padding: 32px; }

/* Header */
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
.header-left { display: flex; align-items: center; gap: 16px; }
.header-icon {
  width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px; box-shadow: 0 4px 16px rgba(99,102,241,0.25);
}
.title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.5px; }
.subtitle { font-size: 14px; color: #64748b; margin: 4px 0 0; }
.back-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  color: white !important; font-weight: 600; text-transform: none;
  padding: 0 24px !important; height: 40px !important;
  box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease;
}
.back-btn:hover { box-shadow: 0 6px 20px rgba(99,102,241,0.35); transform: translateY(-1px); }

/* Cards */
.card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
  overflow: hidden; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.card-header {
  padding: 18px 24px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #f1f5f9; background: #fafbfc;
}
.flex-left { display: flex; align-items: center; gap: 10px; }
.dot {
  width: 8px; height: 8px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%; animation: pulse 2s infinite;
}
.dot.chart { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.label {
  font-size: 12px; font-weight: 700; color: #475569;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.card-body { padding: 24px; }

/* Info Grid */
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; }
.info-item { display: flex; flex-direction: column; gap: 8px; }
.info-label {
  display: flex; align-items: center; font-size: 12px; font-weight: 700;
  color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;
}
.info-value { font-size: 20px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.info-value.model-name {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.info-desc { font-size: 13px; color: #64748b; line-height: 1.5; }
.branch-badge {
  display: inline-flex; align-items: center; padding: 8px 14px;
  background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px;
  color: #059669; font-size: 14px; font-weight: 600; width: fit-content;
}
.safety-badge {
  display: inline-flex; align-items: center; padding: 8px 14px;
  border-radius: 8px; font-size: 14px; font-weight: 600; width: fit-content; border: 1px solid;
}
.score-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

/* Legend */
.legend { display: flex; gap: 20px; }
.legend-item {
  display: flex; align-items: center; gap: 8px; font-size: 12px;
  color: #64748b; font-weight: 500; cursor: pointer; padding: 6px 10px;
  border-radius: 6px; transition: all 0.2s ease;
}
.legend-item:hover { background: #f1f5f9; }
.legend-item.legend-disabled { opacity: 0.4; }
.legend-item.legend-disabled .legend-dot { background: #cbd5e1 !important; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; }
.legend-dot.usage { background: #10b981; }
.legend-dot.errors { background: #ef4444; }

/* Loading & Empty State */
.loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 20px; gap: 16px;
}
.loading-text { font-size: 14px; color: #cbd5e1; margin: 0; }
.empty-title { font-size: 14px; font-weight: 700; color: #cbd5e1; margin: 0 0 8px 0; }

/* Stats */
.stats-section { margin-top: 32px; }
.section-header { display: flex; align-items: center; margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 700; color: #0f172a; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }

.stat-card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
  overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-header {
  display: flex; align-items: center; gap: 10px; padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9; background: #fafbfc;
  font-size: 15px; font-weight: 700; color: #0f172a;
}
.stat-body { padding: 20px; }
.stat-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; font-size: 14px;
}
.stat-label { color: #64748b; font-weight: 500; }
.stat-value { font-weight: 500; color: #0f172a; font-size: 14px; }
.stat-value.danger { color: #ef4444; }
.stat-value.warning { color: #f59e0b; }
.stat-value.success { color: #10b981; }
.stat-value.primary { color: #6366f1; }
.divider { height: 1px; background: #f1f5f9; margin: 12px 0; }

/* Progress */
.progress-item { padding: 10px 0; }
.progress-label-row {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.progress-label-row .stat-label, .progress-label-row .stat-value { font-size: 14px; font-weight: 500; }
.progress-container { height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.progress-fill {
  height: 100%; background: #6366f1;
  border-radius: 4px; transition: width 0.3s ease;
}
.progress-fill.danger-fill { background: #ef4444; }
.progress-fill.success-fill { background: #10b981; }

/* Responsive */
@media (max-width: 960px) {
  .container { padding: 20px; }
  .header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .info-grid, .stats-grid { grid-template-columns: 1fr; gap: 16px; }
}
</style>