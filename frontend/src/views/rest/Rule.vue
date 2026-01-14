<template>
  <v-container class="page-container" fluid>
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="icon-box">
          <v-icon size="24" color="#6366f1">mdi-file-document-outline</v-icon>
        </div>
        <div>
          <h1 class="page-title">Quy Tắc Bảo Mật</h1>
          <p class="page-subtitle">Quản lý các quy tắc phân tích mã nguồn</p>
        </div>
      </div>
      <v-btn variant="flat" rounded="lg" @click="() => { rule = new Rule(); rule.id = undefined; }" class="create-btn">
        <v-icon start size="18">mdi-plus-circle</v-icon>
        Tạo Quy Tắc
      </v-btn>
    </div>

    <!-- Table -->
    <div class="table-card">
      <v-data-table :headers="headers" :items="rules" :items-length="count" :loading="loading" @update:options="getRules" @click:row="(event, { item }) => (rule = item)" hover class="modern-table" :items-per-page-options="[{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }, { value: 100, title: '100' }, { value: -1, title: 'Tất cả' }]" :items-per-page-text="'Số bản ghi:'" :page-text="'{0}-{1} trên {2}'">
        <template v-slot:loading>
          <div class="loading-state">
            <v-progress-circular color="#8b5cf6" indeterminate size="48"></v-progress-circular>
            <p class="loading-text">Đang tải dữ liệu...</p>
          </div>
        </template>

        <template v-slot:item.name="{ item }">
          <div class="table-name">
            <div class="name-icon">
              <v-icon size="16" color="#6366f1">mdi-file-code</v-icon>
            </div>
            <span>{{ item.name }}</span>
          </div>
        </template>

        <template v-slot:item.language="{ item }">
          <div class="lang-badge">
            {{ languageTypes.find((c) => c.value == item.language)?.title || "-" }}
          </div>
        </template>

        <template v-slot:no-data>
          <div class="empty-state">
            <v-icon size="64" color="#cbd5e1">mdi-emoticon-dead-outline</v-icon>
            <h3 class="empty-title">Chưa Có Quy Tắc Nào</h3>
          </div>
        </template>
      </v-data-table>
    </div>
  </v-container>

  <!-- Dialog -->
  <v-dialog :model-value="rule.id !== null" max-width="720px" @update:modelValue="(val) => { if (!val) rule = new Rule(); }">
    <v-card class="dialog-card">
      <div class="dialog-header">
        <div class="dialog-icon">
          <v-icon color="white" size="24">{{ rule.id ? 'mdi-pencil' : 'mdi-plus-circle' }}</v-icon>
        </div>
        <div>
          <h3>{{ rule.id ? 'Chỉnh Sửa Quy Tắc' : 'Tạo Quy Tắc Mới' }}</h3>
          <p>{{ rule.id ? 'Cập nhật cấu hình quy tắc' : 'Cấu hình một quy tắc bảo mật mới' }}</p>
        </div>
      </div>

      <v-card-text class="pa-6">
        <v-form>
          <v-text-field v-model="rule.name" label="Tên" variant="outlined" rounded="lg" bg-color="#f8fafc" class="mb-3"></v-text-field>
          <v-textarea v-model="rule.description" label="Mô Tả" variant="outlined" rounded="lg" bg-color="#f8fafc" rows="3" class="mb-3"></v-textarea>
          <v-textarea v-model="rule.rule" label="Mẫu Quy Tắc" variant="outlined" rounded="lg" bg-color="#f8fafc" rows="4" class="mb-3 monospace-field"></v-textarea>
          <v-select v-model="rule.language" :items="languageTypes" label="Ngôn Ngữ" variant="outlined" rounded="lg" bg-color="#f8fafc" class="mb-3"></v-select>
          <v-autocomplete v-model="rule.analyzer" :items="analyzers" item-title="name" item-value="id" label="Bộ Phân Tích" variant="outlined" rounded="lg" bg-color="#f8fafc" class="mb-3" :loading="analyzerTimer !== null" @update:search="getAnalyzers"></v-autocomplete>
          <v-autocomplete v-model="rule.vulnerability" :items="vulnerabilities" item-title="name" item-value="id" label="Lỗ Hổng" variant="outlined" rounded="lg" bg-color="#f8fafc" :loading="vulnerabilitiesTimer !== null" @update:search="getVulnerabilities"></v-autocomplete>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 py-4 dialog-footer">
        <v-btn variant="text" color="error" rounded="lg" @click="rule = new Rule()">Hủy</v-btn>
        <v-spacer></v-spacer>
        <v-btn v-if="rule.id === undefined" variant="flat" :loading="posting" @click="postSave" class="gradient-btn" rounded="lg">Lưu</v-btn>
        <v-btn v-else-if="rule.id" variant="flat" :loading="posting" @click="patchSave" class="gradient-btn" rounded="lg">Cập Nhật</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "@/plugins/axios";
import { defineComponent } from "vue";

class Rule {
  id = null;
  name = "";
  description = "";
  severity = "l";
  is_public = false;
}

export default defineComponent({
  data: () => ({
    loading: false,
    posting: false,
    count: 0,
    Rule,
    rules: [],
    rule: new Rule(),
    languageTypes: [],
    analyzers: [],
    analyzerTimer: null,
    vulnerabilities: [],
    vulnerabilitiesTimer: null,
    headers: [
      { title: "Tên", value: "name" },
      { title: "Ngôn Ngữ", value: "language" },
    ],
  }),
  mounted() {
    this.getRules();
  },
  methods: {
    async getRules(options = { page: 1, itemsPerPage: 20 }) {
      this.loading = true;
      try {
        const { data: opts } = await axios.options("/security-agent/rule/");
        this.languageTypes = opts.actions.POST.language.choices.map((c) => ({ title: c.display_name, value: c.value }));

        if(this.analyzers.length === 0) this.getAnalyzers(undefined);
        if(this.vulnerabilities.length === 0) this.getVulnerabilities(undefined);

        const { data } = await axios.get("/security-agent/rule/", {
          params: { page: options.page, page_size: options.itemsPerPage },
        });
        this.count = data.count;
        this.rules = data.results;
      } catch (err) {
        console.error(err);
      }
      this.loading = false;
    },
    getAnalyzers(value) {
      clearTimeout(this.analyzerTimer);
      this.analyzerTimer = setTimeout(async () => {
        try {
          const { data } = await axios.get("/security-agent/analyzer/", {
            params: { search: value, page_size: 200 },
          });
          this.analyzers = data.results;
          this.analyzerTimer = null;
        } catch (err) {
          console.error(err);
        }
      }, 500);
    },
    getVulnerabilities(value) {
      clearTimeout(this.vulnerabilitiesTimer);
      this.vulnerabilitiesTimer = setTimeout(async () => {
        try {
          const { data } = await axios.get("/vulnerabilities/vulnerability/", {
            params: { search: value, page_size: 200 },
          });
          this.vulnerabilities = data.results;
          this.vulnerabilitiesTimer = null;
        } catch (err) {
          console.error(err);
        }
      }, 500);
    },
    async postSave() {
      this.posting = true;
      try {
        await axios.post(`/analyzer/rule/`, this.rule);
        await this.getRules();
        this.rule = new Rule();
      } catch (err) {
        console.error(err);
      }
      this.posting = false;
    },
    async patchSave() {
      this.posting = true;
      try {
        await axios.patch(`/analyzer/rule/${this.rule.id}/`, this.rule);
        await this.getRules();
        this.rule = new Rule();
      } catch (err) {
        console.error(err);
      }
      this.posting = false;
    },
  },
});
</script>

<style scoped>
.page-container { min-height: 100vh; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 32px; }

/* Header */
.page-header { background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.header-content { display: flex; align-items: center; gap: 16px; }
.icon-box { width: 56px; height: 56px; background: linear-gradient(135deg, #ede9fe 0%, #f3e8ff 100%); border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99,102,241,0.15); border: 1px solid #ddd6fe; }
.page-title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0; }
.page-subtitle { font-size: 13px; color: #64748b; margin: 4px 0 0; }
.create-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.create-btn:hover { box-shadow: 0 8px 20px rgba(99,102,241,0.35); transform: translateY(-2px); }

/* Table */
.table-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.modern-table { background: transparent !important; }
.modern-table :deep(.v-data-table__tr:hover) { background: #f8fafc !important; cursor: pointer; }
.modern-table :deep(th) { background: #fafbfc !important; color: #475569 !important; text-transform: uppercase; font-weight: 700 !important; font-size: 12px !important; letter-spacing: 0.5px; padding: 16px !important; border-bottom: 1px solid #e2e8f0 !important; }
.modern-table :deep(td) { background: transparent !important; color: #334155 !important; border-bottom: 1px solid #f1f5f9 !important; padding: 16px !important; font-size: 14px; }
.modern-table :deep(.v-data-table-footer) { background: #fafbfc !important; border-top: 1px solid #e2e8f0; color: #64748b !important; }
.modern-table :deep(.v-data-table-progress) { display: none !important; }
.table-name { display: flex; align-items: center; gap: 10px; font-weight: 600; color: #0f172a; }
.name-icon { width: 28px; height: 28px; background: #ede9fe; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd6fe; }
.lang-badge { display: inline-block; padding: 4px 12px; background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; border-radius: 12px; font-size: 12px; font-weight: 600; }

/* Loading State */
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center; gap: 16px; }
.loading-text { font-size: 14px; color: #cbd5e1; margin: 0; }

/* Empty State */
.empty-state { padding: 80px 20px }
.empty-title { font-size: 18px; font-weight: 700; color: #cbd5e1; margin: 20px 0 8px; }

/* Dialog */
.dialog-card { border-radius: 16px !important; background: #fff !important; }
.dialog-header { padding: 28px 24px 20px; display: flex; align-items: center; gap: 16px; border-bottom: 1px solid #e2e8f0; background: #fff; }
.dialog-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; box-shadow: 0 6px 20px rgba(99,102,241,0.3); }
.dialog-header h3 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0; }
.dialog-header p { font-size: 12px; color: #64748b; margin: 4px 0 0; }
.dialog-footer { background: #fff; border-top: 1px solid #e2e8f0; }
.monospace-field :deep(textarea) { font-family: 'JetBrains Mono', monospace !important; }
.gradient-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.gradient-btn:hover:not(:disabled) { box-shadow: 0 6px 20px rgba(99,102,241,0.35); transform: translateY(-2px); }

/* Responsive */
@media (max-width: 960px) {
  .page-container { padding: 16px; }
  .page-header { padding: 16px; flex-direction: column; gap: 16px; align-items: flex-start; }
  .header-content { width: 100%; }
  .create-btn { width: 100%; }
  .icon-box { width: 48px; height: 48px; }
  .page-title { font-size: 20px; }
  .page-subtitle { font-size: 12px; }
  .table-card { border-radius: 12px; }
  .modern-table :deep(th), .modern-table :deep(td) { padding: 12px !important; font-size: 13px !important; }
}
</style>