<template>
  <v-container class="auth-container" fluid>
    <v-row class="fill-height">
      <!-- Left Side - Brand Section -->
      <v-col cols="12" md="6" class="brand-section">
        <div class="brand-content">
          <div class="brand-icon-large">
            <v-icon size="64" color="white">mdi-cube-scan</v-icon>
          </div>
          <h1 class="brand-title">LLM Sec Guard</h1>
          <p class="brand-subtitle">Kiểm tra an toàn trên mã sinh bởi LLM</p>
          
          <div class="features-list">
            <div v-for="f in features" :key="f.icon" class="feature-item">
              <div class="feature-icon">
                <v-icon size="20" color="white">{{ f.icon }}</v-icon>
              </div>
              <div class="feature-text">
                <h3>{{ f.title }}</h3>
                <p>{{ f.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </v-col>

      <!-- Right Side - Auth Form -->
      <v-col cols="12" md="6" class="form-section">
        <div class="form-container">
          <!-- Tab Headers -->
          <div class="auth-tabs">
            <div v-for="t in tabs" :key="t.value" class="auth-tab" :class="{ active: tab === t.value }" @click="tab = t.value">
              <v-icon size="20" class="mr-2">{{ t.icon }}</v-icon>
              {{ t.label }}
            </div>
          </div>

          <!-- Login Form -->
          <div v-if="tab === 'login'" class="auth-form">
            <h2 class="form-title">Chào Mừng Trở Lại</h2>
            <p class="form-subtitle">Nhập thông tin đăng nhập để tiếp tục</p>

            <!-- Lock Alert -->
            <v-alert v-if="isLocked" type="error" variant="tonal" class="lock-alert" rounded="lg" :icon="false">
              <div class="lock-content">
                <v-icon size="24" color="error" class="mr-2">mdi-lock-alert</v-icon>
                <div>
                  <div class="lock-title">Tài khoản tạm thời bị khóa</div>
                  <div class="lock-message">Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau.</div>
                </div>
              </div>
            </v-alert>

            <v-form v-model="login.valid" @submit.prevent="postLogin">
              <div v-for="field in loginFields" :key="field.key" class="form-field">
                <label class="field-label">{{ field.label }}</label>
                <v-text-field v-model="login[field.key]" :type="field.type === 'password' && !login.showPassword ? 'password' : 'text'" :rules="field.rules" :placeholder="field.placeholder" :disabled="isLocked" :error="!!login.error" :error-messages="login.error ? [login.error] : []" variant="outlined" hide-details="auto" density="comfortable" class="modern-input" @input="login.error = ''">
                  <template v-slot:prepend-inner>
                    <v-icon size="20" color="#64748b">{{ field.icon }}</v-icon>
                  </template>
                  <template v-if="field.type === 'password'" v-slot:append-inner>
                    <v-icon size="20" color="#64748b" style="cursor: pointer;" @click="login.showPassword = !login.showPassword">
                      {{ login.showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
                    </v-icon>
                  </template>
                </v-text-field>
              </div>

              <v-btn type="submit" class="auth-submit-btn" block rounded="lg" size="large" :disabled="!login.valid || isLocked" :loading="loading">
                <v-icon start size="20">mdi-login</v-icon>
                Đăng Nhập Vào Tài Khoản
              </v-btn>
            </v-form>
          </div>

          <!-- Signup Form -->
          <div v-else class="auth-form">
            <h2 class="form-title">Tạo Tài Khoản</h2>
            <p class="form-subtitle">Đăng ký để bắt đầu</p>

            <v-form v-model="signUp.valid" @submit.prevent="postSignup">
              <div class="form-row">
                <div v-for="field in ['firstName', 'lastName']" :key="field" class="form-field">
                  <label class="field-label">{{ field === 'firstName' ? 'Họ' : 'Tên' }}</label>
                  <v-text-field v-model="signUp[field]" :placeholder="field === 'firstName' ? 'John' : 'Doe'" variant="outlined" hide-details="auto" density="comfortable" class="modern-input">
                    <template v-slot:prepend-inner>
                      <v-icon size="20" color="#64748b">mdi-card-account-details</v-icon>
                    </template>
                  </v-text-field>
                </div>
              </div>

              <div v-for="field in signupFields" :key="field.key" class="form-field">
                <label class="field-label">{{ field.label }}</label>
                <v-text-field v-model="signUp[field.key]" :type="field.type === 'password' && !signUp.showPassword ? 'password' : 'text'" :rules="field.rules" :placeholder="field.placeholder" :error-messages="field.key === 'username' && signUp.error ? signUp.error : []" variant="outlined" hide-details="auto" density="comfortable" class="modern-input" @input="signUp.error = ''">
                  <template v-slot:prepend-inner>
                    <v-icon size="20" color="#64748b">{{ field.icon }}</v-icon>
                  </template>
                  <template v-if="field.type === 'password'" v-slot:append-inner>
                    <v-icon size="20" color="#64748b" style="cursor: pointer;" @click="signUp.showPassword = !signUp.showPassword">
                      {{ signUp.showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
                    </v-icon>
                  </template>
                </v-text-field>
                
                <!-- Password Strength Indicator -->
                <div v-if="field.key === 'password' && signUp.password" class="password-strength">
                  <div class="strength-bars" :data-strength="passwordStrength">
                    <div v-for="i in 4" :key="i" class="strength-bar" :class="{ active: i <= passwordStrength }"></div>
                  </div>
                  <div class="strength-requirements">
                    <div v-for="req in passwordRequirements" :key="req.key" class="requirement-item" :class="{ met: req.met }">
                      <v-icon size="14" :color="req.met ? '#10b981' : '#ef4444'">
                        {{ req.met ? 'mdi-check-circle' : 'mdi-close-circle' }}
                      </v-icon>
                      <span>{{ req.label }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-field">
                <label class="field-label">Xác Nhận Mật Khẩu</label>
                <v-text-field v-model="signUp.confirmPassword" :type="!signUp.showPassword ? 'password' : 'text'" :rules="[validators.required, validators.passwordMatch]" placeholder="Nhập lại mật khẩu" variant="outlined" hide-details="auto" density="comfortable" class="modern-input">
                  <template v-slot:prepend-inner>
                    <v-icon size="20" color="#64748b">mdi-lock-check</v-icon>
                  </template>
                  <template v-slot:append-inner>
                    <v-icon size="20" color="#64748b" style="cursor: pointer;" @click="signUp.showPassword = !signUp.showPassword">
                      {{ signUp.showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
                    </v-icon>
                  </template>
                </v-text-field>
              </div>

              <v-btn type="submit" class="auth-submit-btn" block rounded="lg" size="large" :disabled="!signUp.valid" :loading="loading">
                <v-icon start size="20">mdi-account-plus</v-icon>
                Tạo Tài Khoản
              </v-btn>
            </v-form>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "@/plugins/axios";

export default {
  data: () => ({
    tab: "login",
    loading: false,
    login: { valid: false, showPassword: false, username: "", password: "", error: "" },
    signUp: { valid: false, showPassword: false, username: "", email: "", firstName: "", lastName: "", password: "", confirmPassword: "", error: "" },
    loginAttempts: { count: 0, lockUntil: null },
    remainingTime: "",
    lockTimer: null,
    tabs: [
      { value: 'login', label: 'Đăng Nhập', icon: 'mdi-login' },
      { value: 'signup', label: 'Đăng Ký', icon: 'mdi-account-plus' }
    ],
    features: [
      { icon: 'mdi-shield-check', title: 'Phân Tích Bảo Mật', desc: 'Phát hiện lỗ hổng mã nguồn bằng AI tiên tiến' },
      { icon: 'mdi-creation', title: 'Sinh Mã Bằng AI', desc: 'Tạo mã an toàn với sự hỗ trợ thông minh' },
      { icon: 'mdi-poll', title: 'Theo Dõi Hiệu Suất', desc: 'Giám sát và đánh giá các chỉ số bảo mật' }
    ]
  }),
  computed: {
    validators() {
      const req = v => !!v || "Trường này là bắt buộc";
      const email = v => /.+@.+\..+/.test(v) || "Email không hợp lệ";
      const minUsername = v => !v || v.length >= 2 || "Tên đăng nhập phải có ít nhất 2 ký tự";
      const strongPassword = v => {
        if (!v) return "Trường này là bắt buộc";
        const p = v, checks = [p.length >= 8, /[a-z]/.test(p), /[A-Z]/.test(p), /[0-9]/.test(p), /[!@#$%^&*(),.?":{}|<>]/.test(p)];
        return checks.every(c => c);
      };
      const passwordMatch = v => v === this.signUp.password || "Mật khẩu không khớp";
      return { required: req, email, minUsername, strongPassword, passwordMatch };
    },
    loginFields() {
      return [
        { key: 'username', label: 'Tên Đăng Nhập', type: 'text', icon: 'mdi-account', placeholder: 'Nhập tên đăng nhập của bạn', rules: [this.validators.required] },
        { key: 'password', label: 'Mật Khẩu', type: 'password', icon: 'mdi-lock', placeholder: 'Nhập mật khẩu của bạn', rules: [this.validators.required] }
      ];
    },
    signupFields() {
      return [
        { key: 'email', label: 'Email', type: 'email', icon: 'mdi-at', placeholder: 'you@example.com', rules: [this.validators.required, this.validators.email] },
        { key: 'username', label: 'Tên Đăng Nhập', type: 'text', icon: 'mdi-account', placeholder: 'Chọn tên đăng nhập', rules: [this.validators.required, this.validators.minUsername] },
        { key: 'password', label: 'Mật Khẩu', type: 'password', icon: 'mdi-lock', placeholder: 'Tạo mật khẩu mạnh', rules: [this.validators.required, this.validators.strongPassword] }
      ];
    },
    passwordRequirements() {
      const p = this.signUp.password || '';
      return [
        { key: 'length', label: 'Ít nhất 8 ký tự', met: p.length >= 8 },
        { key: 'lowercase', label: 'Chữ in thường (a-z)', met: /[a-z]/.test(p) },
        { key: 'uppercase', label: 'Chữ in hoa (A-Z)', met: /[A-Z]/.test(p) },
        { key: 'number', label: 'Số (0-9)', met: /[0-9]/.test(p) },
        { key: 'special', label: 'Ký tự đặc biệt (!@#$...)', met: /[!@#$%^&*(),.?":{}|<>]/.test(p) }
      ];
    },
    passwordStrength() {
      const met = this.passwordRequirements.filter(r => r.met).length;
      return met <= 2 ? 1 : met === 3 ? 2 : met === 4 ? 3 : 4;
    },
    isLocked() {
      if (!this.loginAttempts.lockUntil) return false;
      return Date.now() < this.loginAttempts.lockUntil;
    }
  },
  mounted() {
    this.loadLoginAttempts();
    if (this.isLocked) this.startLockTimer();
  },
  beforeUnmount() {
    if (this.lockTimer) clearInterval(this.lockTimer);
  },
  methods: {
    loadLoginAttempts() {
      const stored = localStorage.getItem("loginAttempts");
      if (stored) {
        this.loginAttempts = JSON.parse(stored);
        if (this.loginAttempts.lockUntil && Date.now() >= this.loginAttempts.lockUntil) {
          this.loginAttempts = { count: 0, lockUntil: null };
          this.saveLoginAttempts();
        }
      }
    },
    saveLoginAttempts() {
      localStorage.setItem("loginAttempts", JSON.stringify(this.loginAttempts));
    },
    startLockTimer() {
      this.updateRemainingTime();
      this.lockTimer = setInterval(() => {
        const now = Date.now();
        if (this.loginAttempts.lockUntil && now >= this.loginAttempts.lockUntil) {
          clearInterval(this.lockTimer);
          this.lockTimer = null;
          this.loginAttempts = Object.assign({}, { count: 0, lockUntil: null });
          this.saveLoginAttempts();
        } else {
          this.updateRemainingTime();
        }
      }, 1000);
    },
    updateRemainingTime() {
      if (!this.loginAttempts.lockUntil) return;
      const diff = Math.max(0, this.loginAttempts.lockUntil - Date.now());
      const mins = Math.floor(diff / 60000);
      const secs = Math.floor((diff % 60000) / 1000);
      this.remainingTime = `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    async postLogin() {
      if (this.isLocked) return;
      this.loading = true;
      this.login.error = "";
      try {
        const { data } = await axios.post("/auth/token/", { username: this.login.username, password: this.login.password }, { isPublic: true });
        localStorage.setItem("LLMAccess", data.access);
        localStorage.setItem("LLMRefresh", data.refresh);
        this.loginAttempts = { count: 0, lockUntil: null };
        this.saveLoginAttempts();
        this.$store.dispatch("getUser");
        this.$router.push("/");
      } catch (err) {
        this.login.error = "Tên đăng nhập hoặc mật khẩu không chính xác";
        this.loginAttempts.count++;
        if (this.loginAttempts.count >= 10) {
          this.loginAttempts.lockUntil = Date.now() + 1 * 60 * 1000;
          this.startLockTimer();
        }
        this.saveLoginAttempts();
      }
      this.loading = false;
    },
    async postSignup() {
      this.loading = true;
      this.signUp.error = "";
      try {
        await axios.post("/auth/sign-up/", {
          username: this.signUp.username,
          email: this.signUp.email,
          first_name: this.signUp.firstName,
          last_name: this.signUp.lastName,
          password: this.signUp.password
        }, { isPublic: true });
        this.tab = "login";
      } catch (err) {
        if (err.response?.data?.username) {
          this.signUp.error = "Tên đăng nhập đã tồn tại";
        } else if (err.response?.data?.email) {
          this.signUp.error = "Email đã được sử dụng";
        } else {
          this.signUp.error = "Đăng ký thất bại. Vui lòng thử lại";
        }
      }
      this.loading = false;
    }
  }
};
</script>

<style scoped>
/* Layout */
.auth-container { background: #f8fafc; min-height: 100vh; padding: 0; }
.fill-height { min-height: 100vh; }

/* Brand Section */
.brand-section { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); display: flex; align-items: center; justify-content: center; padding: 60px 40px; position: relative; overflow: hidden; }
.brand-section::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 50px 50px; animation: moveBackground 20s linear infinite; }
@keyframes moveBackground { 0% { transform: translate(0, 0); } 100% { transform: translate(50px, 50px); } }
.brand-content { position: relative; z-index: 1; max-width: 500px; text-align: center; }
.brand-icon-large { width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.2); backdrop-filter: blur(20px); border-radius: 24px; margin: 0 auto 32px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
.brand-title { font-size: 48px; font-weight: 800; color: white; margin-bottom: 12px; letter-spacing: -1px; }
.brand-subtitle { font-size: 18px; color: rgba(255,255,255,0.95); margin-bottom: 48px; font-weight: 500; }
.features-list { display: flex; flex-direction: column; gap: 24px; text-align: left; }
.feature-item { display: flex; gap: 16px; background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.25); transition: all 0.3s ease; }
.feature-item:hover { background: rgba(255,255,255,0.2); transform: translateX(8px); }
.feature-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.2); border-radius: 12px; flex-shrink: 0; }
.feature-text h3 { font-size: 16px; font-weight: 600; color: white; margin: 0 0 4px 0; }
.feature-text p { font-size: 14px; color: rgba(255,255,255,0.9); margin: 0; line-height: 1.5; }

/* Form Section */
.form-section { display: flex; align-items: center; justify-content: center; padding: 40px; background: #fff; }
.form-container { width: 100%; max-width: 480px; }
.auth-tabs { display: flex; gap: 8px; margin-bottom: 40px; background: #f8fafc; padding: 6px; border-radius: 12px; border: 1px solid #e2e8f0; }
.auth-tab { flex: 1; display: flex; align-items: center; justify-content: center; padding: 12px 20px; font-size: 15px; font-weight: 600; color: #64748b; border-radius: 8px; cursor: pointer; transition: all 0.2s ease; }
.auth-tab:hover { color: #334155; background: #f1f5f9; }
.auth-tab.active { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; box-shadow: 0 4px 12px rgba(99,102,241,0.25); }

.auth-form { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.form-title { font-size: 28px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; letter-spacing: -0.5px; }
.form-subtitle { font-size: 14px; color: #64748b; margin: 0 0 32px 0; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-field { margin-bottom: 20px; }
.field-label { display: block; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }

.modern-input :deep(.v-field) { background: #fff !important; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; transition: all 0.2s ease; }
.modern-input :deep(.v-field--variant-outlined) .v-field__outline { display: none; }
.modern-input :deep(.v-field:hover) { border-color: #cbd5e1; }
.modern-input :deep(.v-field--focused) { background: #fff !important; border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
.modern-input :deep(.v-field--focused.v-field--error) { border-color: #ef4444 !important; box-shadow: 0 0 0 3px rgba(239,68,68,0.1) !important; }
.modern-input :deep(.v-field--error) { border-color: #ef4444 !important; }
.modern-input :deep(.v-field--error:hover) { border-color: #dc2626 !important; }
.modern-input :deep(.v-field__input) { color: #0f172a; padding: 0 12px; }
.modern-input :deep(::placeholder) { color: #94a3b8; }
.modern-input :deep(.v-messages) { margin-top: 6px; font-size: 12px; color: #ef4444 !important; font-weight: 400; }

/* Lock Alert */
.lock-alert { margin-bottom: 20px; border: 1.5px solid #fecaca !important; }
.lock-content { display: flex; align-items: flex-start; }
.lock-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.lock-message { font-size: 13px; opacity: 0.9; }

/* Password Strength */
.password-strength { margin-top: 12px; }
.strength-bars { display: flex; gap: 6px; margin-bottom: 12px; }
.strength-bars[data-strength="1"] .strength-bar.active { background: #ef4444; }
.strength-bars[data-strength="2"] .strength-bar.active { background: #ef4444; }
.strength-bars[data-strength="3"] .strength-bar.active { background: #f59e0b; }
.strength-bars[data-strength="4"] .strength-bar.active { background: #10b981; }
.strength-bar { flex: 1; height: 4px; background: #e2e8f0; border-radius: 2px; transition: all 0.3s ease; }
.strength-requirements { display: flex; flex-direction: column; gap: 8px; }
.requirement-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #ef4444; transition: color 0.2s; }
.requirement-item.met { color: #10b981; }
.requirement-item span { line-height: 1; }

.auth-submit-btn { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: white !important; font-weight: 600; text-transform: none; margin-top: 12px; height: 48px !important; box-shadow: 0 4px 16px rgba(99,102,241,0.25); transition: all 0.3s ease; }
.auth-submit-btn:hover:not(:disabled) { box-shadow: 0 6px 24px rgba(99,102,241,0.35); transform: translateY(-2px); }
.auth-submit-btn:disabled { opacity: 0.5; }

@media (max-width: 960px) {
  .brand-section { display: none; }
  .form-section { padding: 32px 20px; }
  .form-row { grid-template-columns: 1fr; }
  .form-container { max-width: 100%; }
  .form-title { font-size: 24px; }
  .brand-title { font-size: 36px; }
}
</style>