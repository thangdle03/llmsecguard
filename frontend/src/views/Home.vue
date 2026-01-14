<template>
  <v-container class="fill-height pa-0" fluid>
    <v-row class="fill-height ma-0">
      <!-- Code Editor -->
      <v-col cols="12" md="6" class="pa-0 editor-section">
        <MonacoEditor :value="code" language="cpp" theme="vs-light" @change="edited" />
      </v-col>

      <!-- Results -->
      <v-col cols="12" md="6" class="pa-0 d-flex flex-column results-section">
        <!-- Header -->
        <div class="header">
          <div class="header-left">
            <div class="icon-box">
              <v-icon size="20" color="#6366f1">mdi-shield-check</v-icon>
            </div>
            <div>
              <div class="title">Phân Tích Bảo Mật</div>
              <div class="subtitle">Quét và đánh giá các lỗ hổng trong mã nguồn</div>
            </div>
          </div>
          <v-btn variant="flat" :loading="analyzing" @click="postAnalyze" class="analyze-btn" rounded="lg">
            <v-icon start size="18">mdi-play-circle</v-icon>
            Phân Tích Mã
          </v-btn>
        </div>

        <!-- Content -->
        <div class="content-scroll">
          <!-- Summary Card -->
          <div class="card">
            <div class="card-header">
              <div class="flex-center">
                <div :class="['dot', summary && 'success']"></div>
                <span class="label">TÓM TẮT PHÂN TÍCH</span>
                <div v-if="summary" class="badge">
                  <v-icon size="12">mdi-check-circle</v-icon>
                  Hoàn Tất
                </div>
              </div>
              <v-btn v-if="summary" icon size="small" variant="text" @click="copySummary" class="copy-btn">
                <v-icon size="18" :color="summaryIsCopied ? '#10b981' : '#64748b'">
                  {{ summaryIsCopied ? 'mdi-check' : 'mdi-content-copy' }}
                </v-icon>
              </v-btn>
            </div>
            <div class="card-body">
              <div v-if="summary" v-html="summary" class="summary"></div>
              <div v-else class="empty">
                <v-icon size="48" color="#cbd5e1">mdi-magnify-scan</v-icon>
                <h3>Sẵn sàng phân tích</h3>
                <p>Nhấn "Phân Tích Mã" để bắt đầu quá trình phân tích bảo mật</p>
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Prompt Dialog -->
    <v-dialog v-model="promptModal" max-width="720px">
      <v-card v-if="!prompt.response" class="dialog-card">
        <div class="dialog-header">
          <div class="dialog-icon">
            <v-icon color="white" size="24">mdi-creation</v-icon>
          </div>
          <div>
            <h3>Trình Tạo Mã Bằng AI</h3>
            <p>Mô tả thứ bạn muốn tạo</p>
          </div>
        </div>

        <v-card-text class="pa-6">
          <v-textarea v-model="prompt.text" placeholder="e.g., Create a secure function that validates user input..." rows="6" variant="outlined" rounded="lg" bg-color="#f8fafc"></v-textarea>

          <v-alert v-if="top_model.loading" type="info" variant="tonal" class="mt-4" rounded="lg">
            <div class="alert-flex">
              <v-progress-circular indeterminate size="18" width="2"></v-progress-circular>
              <span>Đang chọn mô hình tối ưu...</span>
            </div>
          </v-alert>

          <v-alert v-else-if="top_model.model.id" type="success" variant="tonal" class="mt-4" rounded="lg">
            <div class="alert-flex">
              <span>Sử dụng <strong>{{ top_model.model.name }}</strong></span>
            </div>
          </v-alert>
        </v-card-text>

        <v-card-actions class="px-6 py-4 dialog-footer">
          <v-btn variant="text" color="error" rounded="lg" @click="promptModal = false">Hủy</v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="flat" :loading="prompt.loading" @click="postPrompt" rounded="lg" class="gradient-btn">Tạo Mã</v-btn>
        </v-card-actions>
      </v-card>

      <v-card v-else class="dialog-card">
        <div class="dialog-header success">
          <div class="dialog-icon success">
            <v-icon color="white">mdi-check-bold</v-icon>
          </div>
          <div>
            <h3>Mã Đã Được Tạo</h3>
            <p>Xem lại và nhập vào trình soạn mã</p>
          </div>
          <v-btn icon size="small" variant="text" @click="copyGenerated" class="copy-dialog">
            <v-icon :color="generatedIsCopied ? '#10b981' : '#64748b'">
              {{ generatedIsCopied ? 'mdi-check' : 'mdi-content-copy' }}
            </v-icon>
          </v-btn>
        </div>

        <v-card-text class="pa-6">
          <div class="code-box">
            <div class="code-info">
              <span class="lang">Đã Tạo</span>
              <span class="lines">{{ prompt.response.split('\n').length }} Dòng</span>
            </div>
            <pre><code v-text="prompt.response"></code></pre>
          </div>
        </v-card-text>

        <v-card-actions class="px-6 py-4 dialog-footer">
          <v-btn variant="text" color="error" rounded="lg" @click="prompt.response = ''">Bỏ Qua</v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="flat" rounded="lg" @click="importCode" class="gradient-btn">Nhập Vào Trình Soạn Mã</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import MonacoEditor from "monaco-editor-vue3";
import axios from "@/plugins/axios";
import MarkdownIt from "markdown-it";

export default {
  components: { MonacoEditor },
  data: () => ({
    analyzing: false,
    summaryIsCopied: false,
    fixedIsCopied: false,
    generatedIsCopied: false,
    code: `int main() {
    int x = 0;
    int y = x + 1;
    int a = y + 1;

    std::cout << x;
    return 0;
}`,
    fixed: null,
    summary: null,
    top_model: { loading: false, model: {} },
    prompt: { loading: false, text: "", response: "" },
  }),
  mounted() {
    window.mrk = new MarkdownIt();
  },
  computed: {
    promptModal: {
      get() { return this.$route.query.prompt === "true"; },
      set(val) { this.$router.push({ query: { prompt: val ? "true" : undefined } }); },
    },
  },
  methods: {
    async copySummary() {
      const div = document.createElement("div");
      div.innerHTML = this.summary;
      await navigator.clipboard.writeText(div.textContent);
      this.summaryIsCopied = true;
      setTimeout(() => (this.summaryIsCopied = false), 2000);
    },
    async copyFixed() {
      await navigator.clipboard.writeText(this.fixed);
      this.fixedIsCopied = true;
      setTimeout(() => (this.fixedIsCopied = false), 2000);
    },
    async copyGenerated() {
      await navigator.clipboard.writeText(this.prompt.response);
      this.generatedIsCopied = true;
      setTimeout(() => (this.generatedIsCopied = false), 2000);
    },
    importCode() {
      this.code = this.prompt.response;
      this.promptModal = false;
      this.prompt.response = "";
    },
    edited(code) { this.code = code; },
    async postAnalyze() {
      this.analyzing = true;
      this.fixed = null;
      this.summary = null;

      try {
        await Promise.all([
          axios.post("/security-agent/analyzer/analyze/", {
            lang: this.$store.state.language,
            code: this.code,
          }).then(({ data }) => {
            this.fixed = data.fix || data.fixed_code || null;
          }),
          this.postJudge()
        ]);
      } catch (error) {
        console.error("Analysis error:", error);
        alert("Error: " + (error.response?.data?.message || error.message));
      }
      this.analyzing = false;
    },
    async postJudge() {
      try {
        const { data } = await axios.post("/security-agent/analyzer/judge/", { code: this.code });
        this.summary = new MarkdownIt().render(data.description);
      } catch (err) {
        console.error(err);
      }
    },
    async postPrompt() {
      this.prompt.loading = true;
      try {
        this.top_model.loading = true;
        const { data: models } = await axios.get("/prompt-agent/models/");
        const selectedModel = models.results?.[0] || models[0];
        if (!selectedModel?.id) throw new Error("No model available");

        this.top_model.model = selectedModel;
        this.top_model.loading = false;

        const { data } = await axios.post(`/prompt-agent/models/${selectedModel.id}/query/`, { prompt: this.prompt.text });
        this.prompt.response = data.results;
      } catch (error) {
        console.error("Error:", error);
        alert("Error: " + error.message);
      }
      this.prompt.loading = false;
      this.top_model.loading = false;
    },
  },
};
</script>

<style scoped>
/* Layout */
.v-container { height: 100vh; overflow: hidden; background: #f8fafc; }
.editor-section { background: #fff; border-right: 1px solid #e2e8f0; height: 100vh; }
.results-section { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); height: 100vh; }

/* Header */
.header { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 20px 28px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); flex-shrink: 0; }
.header-left { display: flex; align-items: center; gap: 14px; }
.icon-box { width: 40px; height: 40px; background: linear-gradient(135deg, #ede9fe 0%, #f3e8ff 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(99,102,241,0.15); border: 1px solid #ddd6fe; }
.title { font-size: 15px; font-weight: 700; color: #0f172a; }
.subtitle { font-size: 12px; color: #64748b; margin: 2px 0 0; }
.analyze-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.analyze-btn:hover { box-shadow: 0 8px 20px rgba(99,102,241,0.35); transform: translateY(-2px); }

/* Content */
.content-scroll { flex: 1; overflow-y: auto; padding: 24px 28px; display: flex; flex-direction: column; gap: 20px; }

/* Cards */
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.3s ease; }
.card:hover { border-color: #cbd5e1; box-shadow: 0 6px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }
.card-header { padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; background: #fafbfc; }
.flex-center { display: flex; align-items: center; gap: 10px; flex: 1; }
.dot { width: 8px; height: 8px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 50%; animation: pulse 2s infinite; }
.dot.success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.label { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }
.badge { display: flex; align-items: center; gap: 4px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 10px; border-radius: 12px; font-size: 10px; font-weight: 600; color: #059669; }
.card-body { padding: 20px; max-height: 500px; overflow-y: auto; }

/* Empty State */
.empty { text-align: center; padding: 50px 20px; color: #64748b; }
.empty h3 { font-size: 16px; font-weight: 700; color: #334155; margin: 16px 0 8px; }
.empty p { font-size: 13px; color: #64748b; }

/* Summary */
.summary { line-height: 1.8; color: #334155; font-size: 14px; }
.summary >>> p { margin-bottom: 12px; }
.summary >>> h1, .summary >>> h2, .summary >>> h3 { font-size: 15px; font-weight: 700; margin: 20px 0 10px 0; color: #6366f1; }
.summary >>> ul, .summary >>> ol { margin: 12px 0 12px 20px; }
.summary >>> li { margin-bottom: 8px; }
.summary >>> strong { color: #10b981; font-weight: 700; }
.summary >>> code { background: #f1f5f9; color: #dc2626; padding: 3px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 13px; border: 1px solid #e2e8f0; }
.summary >>> em { color: #6366f1; font-style: italic; }

/* Code Box */
.code-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.code-info { display: flex; justify-content: space-between; padding: 10px 16px; background: #fafbfc; border-bottom: 1px solid #e2e8f0; }
.lang { font-size: 11px; font-weight: 700; color: #6366f1; text-transform: uppercase; }
.lines { font-size: 10px; color: #94a3b8; font-weight: 600; }
.code-box pre { margin: 0; padding: 16px; overflow-x: auto; background: #fff; }
.code-box code { font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.6; color: #1e293b; }

/* Dialog */
.dialog-card { border-radius: 16px !important; background: #fff !important; }
.dialog-header { padding: 28px 24px 20px; display: flex; align-items: center; gap: 16px; border-bottom: 1px solid #e2e8f0; background: #fff; position: relative; }
.dialog-header.success { background: #fff; border-bottom: 1px solid #d1fae5; }
.dialog-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; box-shadow: 0 6px 20px rgba(99,102,241,0.3); }
.dialog-icon.success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 6px 20px rgba(16,185,129,0.3); }
.dialog-header h3 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0; }
.dialog-header p { font-size: 12px; color: #64748b; margin: 4px 0 0; }
.copy-dialog { position: absolute; top: 24px; right: 24px; }
.dialog-footer { background: #fff; border-top: 1px solid #e2e8f0; }
.alert-flex { display: flex; align-items: center; gap: 12px; }

/* Gradient Buttons */
.gradient-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; box-shadow: 0 4px 12px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.gradient-btn:hover:not(:disabled) { box-shadow: 0 6px 20px rgba(99,102,241,0.35); transform: translateY(-2px); }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f8fafc; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Responsive */
@media (max-width: 960px) {
  .v-container { overflow: auto; }
  .editor-section { height: 50vh; border-right: none; border-bottom: 1px solid #e2e8f0; }
  .results-section { height: auto; min-height: 50vh; }
  .header { padding: 16px; flex-direction: column; gap: 12px; align-items: flex-start; }
  .header-left { width: 100%; }
  .analyze-btn { width: 100%; }
  .icon-box { width: 36px; height: 36px; }
  .title { font-size: 14px; }
  .subtitle { font-size: 11px; }
  .content-scroll { padding: 16px; }
  .card { border-radius: 12px; }
  .card-header { padding: 12px 16px; }
  .card-body { padding: 16px; max-height: 400px; }
  .label { font-size: 11px; }
  .badge { font-size: 9px; padding: 2px 8px; }
  .empty { padding: 30px 16px; }
  .empty h3 { font-size: 14px; }
  .empty p { font-size: 12px; }
  .summary { font-size: 13px; }
  .dialog-card { margin: 16px; }
  .dialog-header { padding: 20px 16px 16px; }
  .dialog-icon { width: 40px; height: 40px; }
  .dialog-header h3 { font-size: 16px; }
  .dialog-header p { font-size: 11px; }
  .copy-dialog { top: 20px; right: 16px; }
}
</style>