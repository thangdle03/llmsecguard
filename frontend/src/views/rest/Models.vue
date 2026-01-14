<template>
  <v-container class="page-container" fluid>
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="icon-box">
          <v-icon size="24" color="#6366f1">mdi-robot</v-icon>
        </div>
        <div>
          <h1 class="page-title">Mô Hình LLM</h1>
          <p class="page-subtitle">Quản lý các mô hình ngôn ngữ của bạn</p>
        </div>
      </div>
      <v-btn variant="flat" rounded="lg" @click="() => { model = new LlmModel(); model.id = undefined; }" class="create-btn">
        <v-icon start size="18">mdi-plus-circle</v-icon>
        Tạo Mô Hình
      </v-btn>
    </div>

    <!-- Table -->
    <div class="table-card">
      <v-data-table :headers="headers" :items="models" :items-length="count" :loading="loading" @update:options="getModels" @click:row="(event, { item }) => (model = item)" hover class="modern-table" :items-per-page-options="[{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }, { value: 100, title: '100' }, { value: -1, title: 'Tất cả' }]" :items-per-page-text="'Số bản ghi:'" :page-text="'{0}-{1} trên {2}'">
        <template v-slot:loading>
          <div class="loading-state">
            <v-progress-circular color="#8b5cf6" indeterminate size="48"></v-progress-circular>
            <p class="loading-text">Đang tải dữ liệu...</p>
          </div>
        </template>

        <template v-slot:item.name="{ item }">
          <div class="table-name">
            <div class="name-icon">
              <v-icon size="16" color="#6366f1">mdi-brain</v-icon>
            </div>
            <span>{{ item.name }}</span>
          </div>
        </template>

        <template v-slot:item.model="{ item }">
          <div class="model-badge">{{ item.model }}</div>
        </template>

        <template v-slot:no-data>
          <div class="empty-state">
            <v-icon size="64" color="#cbd5e1">mdi-emoticon-dead-outline</v-icon>
            <h3 class="empty-title">Chưa Có Mô Hình Nào</h3>
          </div>
        </template>
      </v-data-table>
    </div>
  </v-container>

  <!-- Dialog -->
  <v-dialog :model-value="model.id !== null" max-width="720px" @update:modelValue="(val) => { if (!val) model = new LlmModel(); }">
    <v-card class="dialog-card">
      <div class="dialog-header">
        <div class="dialog-icon">
          <v-icon color="white" size="24">{{ model.id ? 'mdi-pencil' : 'mdi-plus-circle' }}</v-icon>
        </div>
        <div>
          <h3>{{ model.id ? 'Chỉnh Sửa Mô Hình' : 'Tạo Mô Hình Mới' }}</h3>
          <p>{{ model.id ? 'Cập nhật cấu hình mô hình' : 'Cấu hình một mô hình LLM mới' }}</p>
        </div>
      </div>

      <v-card-text class="pa-6">
        <v-form>
          <v-text-field v-model="model.name" label="Tên" variant="outlined" rounded="lg" bg-color="#f8fafc" class="mb-3"></v-text-field>
          <v-textarea v-model="model.description" label="Mô Tả" variant="outlined" rounded="lg" bg-color="#f8fafc" rows="3" class="mb-3"></v-textarea>
          <v-select v-model="model.model" :items="modelTypes" label="Loại Mô Hình" variant="outlined" rounded="lg" bg-color="#f8fafc" class="mb-3"></v-select>
          <v-text-field v-model="model.api_key" label="Khóa API" variant="outlined" rounded="lg" bg-color="#f8fafc" type="password" class="mb-3"></v-text-field>
          <v-textarea v-model="model.summary" label="Mẫu Tóm Tắt" variant="outlined" rounded="lg" bg-color="#f8fafc" rows="3"></v-textarea>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 py-4 dialog-footer">
        <v-btn variant="text" color="error" rounded="lg" @click="model = new LlmModel()">Hủy</v-btn>
        <v-spacer></v-spacer>
        <v-btn v-if="model.id === undefined" variant="flat" :loading="posting" @click="postSave" class="gradient-btn" rounded="lg">Lưu</v-btn>
        <v-btn v-else-if="model.id" variant="flat" :loading="posting" @click="patchSave" class="gradient-btn" rounded="lg">Cập Nhật</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from "@/plugins/axios";
import { defineComponent } from "vue";

class LlmModel {
  id = null;
  name = "";
  description = "";
  model = "";
  api_key = "";
  summary = "";
}

export default defineComponent({
  data: () => ({
    loading: false,
    posting: false,
    count: 0,
    LlmModel,
    models: [],
    model: new LlmModel(),
    modelTypes: [],
    headers: [
      { title: "Tên", value: "name" },
      { title: "Loại Mô Hình", value: "model" },
    ],
  }),
  mounted() {
    this.getModels();
  },
  methods: {
    async getModels(options = { page: 1, itemsPerPage: 20 }) {
      this.loading = true;
      try {
        const { data: opts } = await axios.options("/prompt-agent/models/");
        this.modelTypes = opts.actions.POST.model.choices.map((el) => el.value);

        const { data } = await axios.get("/prompt-agent/models/", {
          params: { page: options.page, page_size: options.itemsPerPage },
        });
        this.count = data.count;
        this.models = data.results;
      } catch (err) {
        console.error(err);
      }
      this.loading = false;
    },
    async postSave() {
      this.posting = true;
      try {
        await axios.post(`/prompt-agent/models/`, this.model);
        await this.getModels();
        this.model = new LlmModel();
      } catch (err) {
        console.error(err);
      }
      this.posting = false;
    },
    async patchSave() {
      this.posting = true;
      try {
        await axios.patch(`/prompt-agent/models/${this.model.id}/`, this.model);
        await this.getModels();
        this.model = new LlmModel();
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
.model-badge { display: inline-block; padding: 4px 12px; background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; border-radius: 12px; font-size: 12px; font-weight: 600; }

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