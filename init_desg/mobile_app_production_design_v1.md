# 📱 Claims-Askes Mobile App - Production Design Specifications V1.0

**Last Updated**: August 15, 2025  
**Design System**: Askes Health Design System 2.0  
**Platform**: iOS & Android (React Native)  
**Language**: Bahasa Indonesia (Primary), English (Secondary)

---

## 🎨 DESIGN SYSTEM FOUNDATION

### Color Palette
```scss
// Primary Colors
$primary-blue: #0066CC;      // Main brand color
$primary-dark: #004499;      // Pressed states
$primary-light: #E6F2FF;     // Backgrounds

// Health Status Colors  
$health-green: #00B74A;      // Active/Healthy
$health-orange: #FF9800;     // Warning/Attention
$health-red: #F44336;        // Critical/Urgent

// Semantic Colors
$success: #4CAF50;           // Success states
$warning: #FFC107;           // Warning states
$error: #E91E63;            // Error states
$info: #2196F3;             // Information

// Neutral Colors
$gray-900: #1A1A1A;         // Primary text
$gray-700: #4A4A4A;         // Secondary text
$gray-500: #9E9E9E;         // Disabled text
$gray-300: #E0E0E0;         // Borders
$gray-100: #F5F5F5;         // Backgrounds
$white: #FFFFFF;            // Pure white

// Dark Mode
$dark-bg: #121212;
$dark-surface: #1E1E1E;
$dark-primary: #4D9FFF;
```

### Typography
```scss
// Font Family
@font-face {
  font-family: 'Inter';
  // Regular, Medium, SemiBold, Bold
}

// Type Scale
$display-lg: 32px/40px;     // Headlines
$display-md: 28px/36px;     // Section headers
$title-lg: 22px/30px;       // Page titles
$title-md: 18px/26px;       // Card titles
$body-lg: 16px/24px;        // Body text
$body-md: 14px/20px;        // Default text
$caption: 12px/16px;        // Small text
$overline: 10px/14px;       // Tiny labels
```

### Spacing System
```scss
$space-xxs: 4px;
$space-xs: 8px;
$space-sm: 12px;
$space-md: 16px;
$space-lg: 24px;
$space-xl: 32px;
$space-xxl: 48px;
```

### Elevation & Shadows
```scss
$shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
$shadow-md: 0 4px 6px rgba(0,0,0,0.16);
$shadow-lg: 0 10px 20px rgba(0,0,0,0.19);
$shadow-xl: 0 14px 28px rgba(0,0,0,0.25);
```

### Border Radius
```scss
$radius-xs: 4px;
$radius-sm: 8px;
$radius-md: 12px;
$radius-lg: 16px;
$radius-xl: 24px;
$radius-full: 999px;
```

---

## 📱 MOBILE APP SCREENS

### 1. SPLASH & ONBOARDING

#### 1.1 Splash Screen
```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│                                     │
│          [Animated Logo]            │
│         💙 Claims Askes             │
│                                     │
│      "Kesehatan Anda, Prioritas"   │
│            "Kami"                   │
│                                     │
│                                     │
│         [Loading indicator]         │
│                                     │
│                                     │
│         v2.1.0 | Build 1234        │
└─────────────────────────────────────┘

Animation: Logo scales up with spring animation
Duration: 2 seconds
Transition: Fade to onboarding/home
```

#### 1.2 Onboarding Flow (First Time Users)
```
Screen 1: Welcome
┌─────────────────────────────────────┐
│ [Skip]                              │
│                                     │
│     [Illustration: Family Care]     │
│                                     │
│     Selamat Datang di Askes        │
│                                     │
│  Kelola kesehatan keluarga Anda    │
│    dengan mudah dan terpercaya     │
│                                     │
│     ○ ● ○ ○                        │
│                                     │
│        [Lanjut →]                   │
└─────────────────────────────────────┘

Screen 2: Digital Card
┌─────────────────────────────────────┐
│ [Skip]                              │
│                                     │
│    [Illustration: Digital Card]     │
│                                     │
│      Kartu Digital Anda             │
│                                     │
│   Akses kartu asuransi kapan saja  │
│      tanpa perlu kartu fisik       │
│                                     │
│     ○ ○ ● ○                        │
│                                     │
│        [Lanjut →]                   │
└─────────────────────────────────────┘

Screen 3: Quick Claims
┌─────────────────────────────────────┐
│ [Skip]                              │
│                                     │
│  [Illustration: Photo Submission]   │
│                                     │
│      Klaim Mudah & Cepat           │
│                                     │
│    Foto struk, kirim, dan terima   │
│      reimbursement otomatis        │
│                                     │
│     ○ ○ ○ ●                        │
│                                     │
│        [Mulai →]                    │
└─────────────────────────────────────┘
```

### 2. AUTHENTICATION & SECURITY

#### 2.1 Login Screen
```
┌─────────────────────────────────────┐
│                                     │
│         💙 Claims Askes             │
│                                     │
│         Masuk ke Akun               │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📱 Nomor Ponsel / Email     │   │
│  │ 08123456789                 │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🔒 Kata Sandi               │   │
│  │ ••••••••                    │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Lupa Kata Sandi?]                 │
│                                     │
│  ┌─────────────────────────────┐   │
│  │         MASUK                │   │
│  └─────────────────────────────┘   │
│                                     │
│  ──────── atau masuk dengan ────── │
│                                     │
│  [📱 OTP] [🔐 Biometrik] [🔑 PIN]  │
│                                     │
│  Belum punya akun? [Daftar]        │
│                                     │
└─────────────────────────────────────┘

Interactions:
- Phone field auto-formats: 0812-3456-789
- Show/hide password toggle
- Biometric prompt if enabled
- Loading state on submit
```

#### 2.2 OTP Verification
```
┌─────────────────────────────────────┐
│ [←]    Verifikasi OTP               │
│                                     │
│   Masukkan kode 6 digit yang       │
│   dikirim ke 0812****789           │
│                                     │
│   ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
│   │ 1 │ │ 2 │ │ 3 │ │ _ │ │   │ │   │
│   └───┘ └───┘ └───┘ └───┘ └───┘ └───┘
│                                     │
│   Kirim ulang dalam 00:45          │
│                                     │
│   [Kirim Ulang OTP]                │
│                                     │
│   ┌─────────────────────────────┐  │
│   │       VERIFIKASI            │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘

Interactions:
- Auto-focus next field
- Auto-submit on 6 digits
- Countdown timer animation
- Paste from clipboard support
```

### 3. HOME DASHBOARD

#### 3.1 Main Home Screen
```
┌─────────────────────────────────────┐
│ Status Bar (Time, Battery, Network) │
├─────────────────────────────────────┤
│                                     │
│ Selamat Pagi, Budi 👋              │
│ Keluarga Sehat, Hidup Bahagia      │
│                                     │
│ ┌─────────────────────────────┐   │
│ │  💳 KARTU DIGITAL            │   │
│ │  ┌─────────────────────┐    │   │
│ │  │  GOLD PLAN          │    │   │
│ │  │  Budi Santoso       │    │   │
│ │  │  1234 5678 9012     │    │   │
│ │  │  Valid: 12/2025     │    │   │
│ │  └─────────────────────┘    │   │
│ │  [Lihat Detail] [QR Code]   │   │
│ └─────────────────────────────┘   │
│                                     │
│ Akses Cepat                        │
│ ┌────────┐ ┌────────┐ ┌────────┐ │
│ │  📸    │ │  🏥    │ │  💊    │ │
│ │ Klaim  │ │ Dokter │ │ Obat   │ │
│ │ Foto   │ │ Terdekat│ │ Online │ │
│ └────────┘ └────────┘ └────────┘ │
│ ┌────────┐ ┌────────┐ ┌────────┐ │
│ │  📋    │ │  🏥    │ │  📞    │ │
│ │Riwayat │ │ Rawat  │ │24/7    │ │
│ │ Klaim  │ │ Inap   │ │Support │ │
│ └────────┘ └────────┘ └────────┘ │
│                                     │
│ Aktivitas Terkini                  │
│ ┌─────────────────────────────┐   │
│ │ ✅ Klaim Disetujui          │   │
│ │ CLM-2025-001234             │   │
│ │ Rp 1,250,000 • 2 hari lalu  │   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ ⏳ Menunggu Dokumen         │   │
│ │ CLM-2025-001235             │   │
│ │ Upload surat dokter          │   │
│ └─────────────────────────────┘   │
│                                     │
│ ───────────────────────────────    │
│ [🏠] [📄] [💳] [🏥] [👤]         │
│ Home  Klaim Card Provider Profile  │
└─────────────────────────────────────┘

Interactions:
- Pull to refresh with spring animation
- Card flip animation to show QR
- Haptic feedback on quick actions
- Skeleton loading for activities
```

### 4. CLAIMS SUBMISSION

#### 4.1 Claims List Screen
```
┌─────────────────────────────────────┐
│ [←] Klaim Saya           [Filter]  │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────┐   │
│ │ + Ajukan Klaim Baru         │   │
│ └─────────────────────────────┘   │
│                                     │
│ [Semua] [Diproses] [Selesai]      │
│                                     │
│ Agustus 2025                       │
│ ┌─────────────────────────────┐   │
│ │ ✅ RS Siloam                │   │
│ │ CLM-2025-001234             │   │
│ │ Konsultasi Dokter           │   │
│ │ Rp 1,250,000 • Dibayar      │   │
│ │ 14 Agt 2025                 │   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ ⏳ Klinik Medika            │   │
│ │ CLM-2025-001235             │   │
│ │ Pemeriksaan Lab             │   │
│ │ Rp 850,000 • Diproses       │   │
│ │ 12 Agt 2025                 │   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ ❌ Apotek K24               │   │
│ │ CLM-2025-001236             │   │
│ │ Pembelian Obat              │   │
│ │ Rp 450,000 • Ditolak        │   │
│ │ 10 Agt 2025 • Lihat alasan  │   │
│ └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

#### 4.2 New Claim - Smart Camera
```
┌─────────────────────────────────────┐
│ [×] Foto Struk          [💡 Tips]  │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────┐   │
│ │                               │   │
│ │                               │   │
│ │    ┌───────────────────┐     │   │
│ │    │                   │     │   │
│ │    │                   │     │   │
│ │    │  [Camera View]    │     │   │
│ │    │                   │     │   │
│ │    │                   │     │   │
│ │    │  ┌─────────────┐ │     │   │
│ │    │  │ Posisikan  │ │     │   │
│ │    │  │   struk    │ │     │   │
│ │    │  │ di dalam   │ │     │   │
│ │    │  │   kotak    │ │     │   │
│ │    │  └─────────────┘ │     │   │
│ │    │                   │     │   │
│ │    └───────────────────┘     │   │
│ │                               │   │
│ └─────────────────────────────┐   │
│                                     │
│ ✅ Pencahayaan bagus               │
│ ✅ Struk terdeteksi                │
│ ⚠️ Pastikan seluruh struk terlihat │
│                                     │
│    [Gallery]  [📸]  [Flash]        │
│                                     │
└─────────────────────────────────────┘

Smart Features:
- Auto edge detection
- Auto capture when aligned
- OCR preview overlay
- Multiple photo support
- Auto-enhancement
```

#### 4.3 Claim Review & Submit
```
┌─────────────────────────────────────┐
│ [←] Review Klaim                    │
├─────────────────────────────────────┤
│                                     │
│ Data Terdeteksi                    │
│ ┌─────────────────────────────┐   │
│ │ RS Siloam Semanggi          │   │
│ │ 14 Agustus 2025             │   │
│ │ Total: Rp 2,500,000         │   │
│ │ [✏️ Edit]                    │   │
│ └─────────────────────────────┘   │
│                                     │
│ Foto Dokumen (3)                   │
│ ┌────┐ ┌────┐ ┌────┐ [+ Tambah]  │
│ │ 📄 │ │ 📄 │ │ 📄 │             │
│ │Struk│ │Resep│ │Lab │             │
│ └────┘ └────┘ └────┘             │
│                                     │
│ Jenis Perawatan                    │
│ ┌─────────────────────────────┐   │
│ │ ▼ Rawat Jalan               │   │
│ └─────────────────────────────┘   │
│                                     │
│ Diagnosa                           │
│ ┌─────────────────────────────┐   │
│ │ Demam Berdarah (A91)        │   │
│ └─────────────────────────────┘   │
│                                     │
│ Untuk Siapa?                       │
│ ○ Saya                             │
│ ● Anggota Keluarga                 │
│ ┌─────────────────────────────┐   │
│ │ ▼ Istri - Sarah Santoso     │   │
│ └─────────────────────────────┘   │
│                                     │
│ Catatan (Opsional)                 │
│ ┌─────────────────────────────┐   │
│ │ Pemeriksaan rutin bulanan   │   │
│ └─────────────────────────────┘   │
│                                     │
│ Estimasi Benefit                   │
│ ┌─────────────────────────────┐   │
│ │ Coverage: 80%                │   │
│ │ Estimasi dibayar: Rp 2,000,000│ │
│ │ Copay Anda: Rp 500,000      │   │
│ └─────────────────────────────┘   │
│                                     │
│ ☑️ Saya menyatakan data benar      │
│                                     │
│ ┌─────────────────────────────┐   │
│ │      KIRIM KLAIM            │   │
│ └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 5. DIGITAL CARD

#### 5.1 Digital Insurance Card
```
┌─────────────────────────────────────┐
│ [←] Kartu Digital      [Share] [⋮] │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────┐   │
│ │     GOLD PLAN 2025           │   │
│ │                               │   │
│ │     Budi Santoso              │   │
│ │     1234 5678 9012 3456       │   │
│ │                               │   │
│ │     Member Since: Jan 2023    │   │
│ │     Valid Until: Dec 2025     │   │
│ │                               │   │
│ │     [QR CODE]                 │   │
│ │                               │   │
│ └─────────────────────────────┘   │
│                                     │
│ Anggota Keluarga                   │
│ ┌─────────────────────────────┐   │
│ │ 👤 Sarah Santoso (Istri)    │   │
│ │    1234 5678 9012 3457      │   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 👶 Andi Santoso (Anak)      │   │
│ │    1234 5678 9012 3458      │   │
│ └─────────────────────────────┘   │
│                                     │
│ Manfaat Anda                       │
│ ┌─────────────────────────────┐   │
│ │ Rawat Jalan: Rp 50 Juta/thn │   │
│ │ Rawat Inap: Rp 200 Juta/thn │   │
│ │ Dental: Rp 5 Juta/thn       │   │
│ │ Optik: Rp 2 Juta/thn        │   │
│ │ [Lihat Semua Manfaat]        │   │
│ └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────┐   │
│ │   TAMBAH KE APPLE WALLET    │   │
│ └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘

Interactions:
- Tap card to flip and show QR full screen
- Swipe between family members
- Add to digital wallet integration
```

### 6. PROVIDER SEARCH

#### 6.1 Provider Map View
```
┌─────────────────────────────────────┐
│ [←] Provider Terdekat    [Filter]  │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────┐   │
│ │ 🔍 Cari provider...          │   │
│ └─────────────────────────────┘   │
│                                     │
│ [Semua] [RS] [Klinik] [Lab] [Apotek]│
│                                     │
│ ┌─────────────────────────────┐   │
│ │                               │   │
│ │         [Map View]            │   │
│ │                               │   │
│ │     📍  📍    📍              │   │
│ │         📍 You                │   │
│ │     📍      📍                │   │
│ │                               │   │
│ └─────────────────────────────┘   │
│                                     │
│ Terdekat dari Anda                 │
│ ┌─────────────────────────────┐   │
│ │ 🏥 RS Siloam Semanggi       │   │
│ │ ⭐ 4.8 • 1.2 km • Buka      │   │
│ │ Cashless ✓ • Emergency ✓    │   │
│ │ [Arah] [Telp] [Detail]      │   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 🏥 Klinik Medika Prima      │   │
│ │ ⭐ 4.5 • 2.1 km • Buka      │   │
│ │ Cashless ✓ • Umum          │   │
│ │ [Arah] [Telp] [Detail]      │   │
│ └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 7. PROFILE & SETTINGS

#### 7.1 Profile Screen
```
┌─────────────────────────────────────┐
│       Profil           [Settings]  │
├─────────────────────────────────────┤
│                                     │
│        [Avatar]                    │
│      Budi Santoso                  │
│    budi.s@email.com                │
│     Member Gold Plan               │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ 📊 Penggunaan Benefit       │   │
│ │ Rp 12.5 Juta / Rp 50 Juta   │   │
│ │ ████████░░░░░░░░ 25%        │   │
│ └─────────────────────────────┘   │
│                                     │
│ Akun                               │
│ ┌─────────────────────────────┐   │
│ │ 👤 Data Pribadi            >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 👨‍👩‍👧 Anggota Keluarga      >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 📄 Dokumen                 >│   │
│ └─────────────────────────────┘   │
│                                     │
│ Bantuan                            │
│ ┌─────────────────────────────┐   │
│ │ 📞 Hubungi Kami            >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ ❓ FAQ                     >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 📚 Panduan Klaim           >│   │
│ └─────────────────────────────┘   │
│                                     │
│ Lainnya                            │
│ ┌─────────────────────────────┐   │
│ │ 🔔 Notifikasi              >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 🔒 Keamanan                >│   │
│ └─────────────────────────────┘   │
│ ┌─────────────────────────────┐   │
│ │ 📜 Syarat & Ketentuan      >│   │
│ └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────┐   │
│ │        KELUAR               │   │
│ └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎭 MICRO-INTERACTIONS & ANIMATIONS

### Touch Feedback
```javascript
// Haptic Feedback Patterns
const haptics = {
  selection: 'impactLight',      // Tab switches
  success: 'notificationSuccess', // Claim approved
  warning: 'notificationWarning', // Error states
  impact: 'impactMedium'          // Button press
};

// Touch Animations
@keyframes buttonPress {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

// Ripple Effect
@keyframes ripple {
  0% { 
    transform: scale(0);
    opacity: 0.5;
  }
  100% { 
    transform: scale(4);
    opacity: 0;
  }
}
```

### Loading States
```
// Skeleton Loading
┌─────────────────────────────┐
│ ████████████ ███            │ <- Shimmer
│ ████████████████████        │
│ ██████ ████████             │
└─────────────────────────────┘

// Progress Indicators
Linear: ━━━━━━━━━━━━━━━━━━━━━━
Circular: ◐ ◓ ◑ ◒ (rotating)
Dots: ● ○ ○ → ○ ● ○ → ○ ○ ●
```

### Transitions
```scss
// Page Transitions
.slide-in-right {
  animation: slideInRight 0.3s ease-out;
}

.fade-in {
  animation: fadeIn 0.2s ease-in;
}

.scale-up {
  animation: scaleUp 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

// Card Flip Animation
.card-flip {
  transform-style: preserve-3d;
  transition: transform 0.6s;
  &.flipped {
    transform: rotateY(180deg);
  }
}
```

---

## 🚨 EMPTY STATES & ERROR HANDLING

### Empty States
```
No Claims Yet
┌─────────────────────────────────────┐
│                                     │
│        [Illustration]               │
│      📄 No claims yet               │
│                                     │
│   Belum ada klaim yang diajukan    │
│                                     │
│   ┌─────────────────────────┐     │
│   │    AJUKAN KLAIM BARU    │     │
│   └─────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘

No Internet Connection
┌─────────────────────────────────────┐
│                                     │
│        [Illustration]               │
│      🌐 Tidak ada koneksi           │
│                                     │
│    Periksa koneksi internet Anda   │
│                                     │
│   ┌─────────────────────────┐     │
│   │      COBA LAGI          │     │
│   └─────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘
```

### Error States
```
Form Validation Error
┌─────────────────────────────────────┐
│  ┌─────────────────────────────┐   │
│  │ 📱 Nomor Ponsel             │   │
│  │ 0812abc ❌                  │   │
│  └─────────────────────────────┘   │
│  Format nomor tidak valid          │
│                                     │
└─────────────────────────────────────┘

System Error
┌─────────────────────────────────────┐
│         ⚠️ Terjadi Kesalahan        │
│                                     │
│   Maaf, terjadi kesalahan sistem.  │
│      Silakan coba lagi nanti.      │
│                                     │
│   Error: SYS_001                   │
│                                     │
│  [Hubungi Support] [Coba Lagi]     │
└─────────────────────────────────────┘
```

---

## ♿ ACCESSIBILITY

### Voice Over Support
```swift
// iOS VoiceOver Labels
button.accessibilityLabel = "Ajukan klaim baru"
button.accessibilityHint = "Ketuk dua kali untuk membuka kamera"
button.accessibilityTraits = .button

// Android TalkBack
android:contentDescription="Ajukan klaim baru"
android:importantForAccessibility="yes"
```

### Text Scaling
```scss
// Support Dynamic Type
.body-text {
  font-size: 1rem; // 16px base
  @supports (font-size: env(safe-area-inset-top)) {
    font-size: calc(1rem * var(--text-scale-ratio));
  }
}
```

### Color Contrast
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- Interactive elements: 3:1 minimum
- All colors tested for WCAG AA compliance

### Touch Targets
- Minimum size: 44x44pt (iOS) / 48x48dp (Android)
- Spacing between targets: minimum 8pt/dp
- Extended hit areas for small icons

---

## 🌏 LOCALIZATION

### Language Support
```json
{
  "id": {
    "welcome": "Selamat Datang",
    "claim_new": "Ajukan Klaim Baru",
    "provider_nearby": "Provider Terdekat",
    "profile": "Profil"
  },
  "en": {
    "welcome": "Welcome",
    "claim_new": "Submit New Claim",
    "provider_nearby": "Nearby Providers",
    "profile": "Profile"
  }
}
```

### Date & Currency Format
```javascript
// Indonesian Format
const dateID = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'long',
  year: 'numeric'
}).format(date); // "14 Agustus 2025"

const currencyID = new Intl.NumberFormat('id-ID', {
  style: 'currency',
  currency: 'IDR',
  minimumFractionDigits: 0
}).format(amount); // "Rp 1.250.000"
```

---

## 📊 PERFORMANCE METRICS

### Target Metrics
- App launch: < 2 seconds
- Screen transitions: < 300ms
- API response display: < 500ms
- Image loading: Progressive with placeholder
- Offline capability: Core features available
- Bundle size: < 30MB (Android), < 50MB (iOS)

### Optimization Strategies
```javascript
// Lazy Loading
const ClaimDetails = lazy(() => import('./ClaimDetails'));

// Image Optimization
<FastImage
  source={{uri: imageUrl}}
  style={styles.receipt}
  resizeMode={FastImage.resizeMode.contain}
  priority={FastImage.priority.high}
/>

// List Virtualization
<FlatList
  data={claims}
  renderItem={renderClaim}
  getItemLayout={getItemLayout}
  windowSize={10}
  initialNumToRender={5}
  maxToRenderPerBatch={5}
/>
```

---

## 🎯 FIGMA COMPONENT STRUCTURE

### Design Tokens
```
Colors/
├── Primary/
│   ├── primary-100
│   ├── primary-200
│   └── ...
├── Semantic/
│   ├── success
│   ├── warning
│   └── error
└── Neutral/
    ├── gray-100
    └── ...

Typography/
├── Display/
├── Title/
├── Body/
└── Caption/

Spacing/
├── space-xxs (4px)
├── space-xs (8px)
└── ...
```

### Component Library
```
Atoms/
├── Buttons/
│   ├── Primary Button
│   ├── Secondary Button
│   └── Text Button
├── Inputs/
│   ├── Text Field
│   ├── OTP Field
│   └── Search Bar
└── Icons/
    ├── Navigation Icons
    └── Action Icons

Molecules/
├── Cards/
│   ├── Claim Card
│   ├── Provider Card
│   └── Quick Action Card
├── Lists/
│   ├── Claim List Item
│   └── Provider List Item
└── Forms/
    ├── Login Form
    └── Claim Form

Organisms/
├── Headers/
├── Navigation/
├── Modals/
└── Sheets/

Templates/
├── Onboarding/
├── Authentication/
├── Dashboard/
├── Claims/
├── Providers/
└── Profile/
```

---

## 🚀 IMPLEMENTATION NOTES

### React Native Components
```tsx
// Custom Hook for Claims
const useClaimSubmission = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const submitClaim = async (data: ClaimData) => {
    setLoading(true);
    try {
      const result = await api.submitClaim(data);
      return result;
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return { submitClaim, loading, error };
};

// Animated Card Component
const InsuranceCard = ({ member }) => {
  const flipAnim = useRef(new Animated.Value(0)).current;
  
  const flipCard = () => {
    Animated.timing(flipAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true
    }).start();
  };
  
  return (
    <Animated.View style={{
      transform: [{
        rotateY: flipAnim.interpolate({
          inputRange: [0, 1],
          outputRange: ['0deg', '180deg']
        })
      }]
    }}>
      {/* Card content */}
    </Animated.View>
  );
};
```

### Platform Specific
```tsx
// iOS Specific
if (Platform.OS === 'ios') {
  // Request camera permissions
  const { status } = await Camera.requestCameraPermissionsAsync();
  // Add to Apple Wallet
  PassKit.addPass(passData);
}

// Android Specific  
if (Platform.OS === 'android') {
  // Request storage permissions
  const granted = await PermissionsAndroid.request(
    PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE
  );
  // Add to Google Pay
  GooglePay.addPass(passData);
}
```

---

## 📱 DEEP LINKING

### URL Scheme
```
askeshealth://
├── home
├── claims/
│   ├── new
│   └── :claimId
├── card/
│   └── :memberId
├── providers/
│   ├── search
│   └── :providerId
└── profile/
    └── settings
```

### Universal Links
```
https://askeshealth.com/
├── app/claims/:claimId
├── app/card/:memberId
└── app/providers/:providerId
```

---

## 📈 ANALYTICS EVENTS

### Key Events to Track
```javascript
// User Engagement
Analytics.track('app_opened');
Analytics.track('onboarding_completed');
Analytics.track('login_success');

// Claims Flow
Analytics.track('claim_started', { method: 'camera' });
Analytics.track('claim_submitted', { 
  amount: claimAmount,
  type: claimType 
});
Analytics.track('claim_approved');

// Feature Usage
Analytics.track('digital_card_viewed');
Analytics.track('provider_searched', { query });
Analytics.track('provider_called', { providerId });
```

---

## 🔄 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Aug 15, 2025 | Initial production design |
| | | - Complete mobile app flow |
| | | - Design system foundation |
| | | - Micro-interactions defined |
| | | - Accessibility compliance |
| | | - Localization support |

---

*This document represents the complete production-ready mobile app design for Claims-Askes. All specifications are final and ready for implementation in Figma and development.*