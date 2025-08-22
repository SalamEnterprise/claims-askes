# 🎨 Figma Implementation Step-by-Step Guide

## Phase 1: Setup & Foundation (Day 1)

### Step 1: Create Figma File Structure
1. **Create New Figma File**: "Claims-Askes-Health-Insurance-Design-System"
2. **Set Up Pages**:
   ```
   📁 Cover
   📁 Design Tokens
   📁 Components
   📁 Member Portal
   📁 Provider Portal
   📁 Admin Dashboard
   📁 Mobile App
   📁 Prototypes
   📁 Documentation
   ```

### Step 2: Configure Design Tokens
1. **Go to Design Tokens page**
2. **Create Color Styles**:
   ```
   Primary/100 → #E6F2FF
   Primary/500 → #0066CC
   Primary/900 → #001A33
   
   Success/500 → #4CAF50
   Warning/500 → #FFC107
   Error/500 → #E91E63
   
   Gray/100 → #FAFAFA
   Gray/300 → #E0E0E0
   Gray/600 → #666666
   Gray/900 → #212121
   ```

3. **Create Text Styles**:
   ```
   Display → Inter 48/56 Bold
   H1 → Inter 36/44 SemiBold
   H2 → Inter 28/36 SemiBold
   H3 → Inter 24/32 Medium
   Body → Inter 16/24 Regular
   Caption → Inter 14/20 Regular
   Small → Inter 12/16 Regular
   ```

4. **Set Up Spacing Variables**:
   - Create local variables for spacing (8px base unit)
   - xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48

### Step 3: Create Grid Systems
1. **Desktop Grid** (1200px max width):
   - 12 columns
   - 32px gutters
   - 32px margins

2. **Tablet Grid** (768px):
   - 8 columns
   - 24px gutters
   - 24px margins

3. **Mobile Grid** (375px):
   - 4 columns
   - 16px gutters
   - 16px margins

---

## Phase 2: Component Library (Day 2-3)

### Step 4: Build Atoms
1. **Button Component**:
   ```
   Variants:
   - Type: Primary, Secondary, Danger, Ghost
   - Size: Small (32px), Medium (40px), Large (48px)
   - State: Default, Hover, Pressed, Disabled
   - Icon: None, Left, Right, Only
   ```

2. **Input Field**:
   ```
   Variants:
   - Type: Text, Number, Currency, Date, Search
   - State: Default, Focus, Error, Disabled
   - Size: Small, Medium, Large
   ```

3. **Icons** (24x24 base):
   - Import Material Icons or create custom set
   - Categories: System, Medical, Navigation, Status

### Step 5: Build Molecules
1. **Card Component**:
   ```
   Structure:
   ┌─────────────────┐
   │ [Header]        │
   │ [Body]          │
   │ [Footer]        │
   └─────────────────┘
   
   Variants:
   - Elevation: Flat, Raised
   - Padding: None, Small, Medium, Large
   ```

2. **Claim Card**:
   ```
   ┌─────────────────────────┐
   │ Date        Status [→]  │
   │ Provider Name           │
   │ Rp 2,500,000           │
   └─────────────────────────┘
   ```

3. **Insurance Card** (Mobile):
   - Front: Member info, QR code
   - Back: Policy details, emergency contacts

### Step 6: Build Organisms
1. **Navigation Header**:
   - Logo + Navigation + User Menu
   - Mobile: Hamburger menu variant

2. **Bottom Navigation** (Mobile):
   - 5 tabs with icons and labels
   - Active state indicator

3. **Dashboard Widget**:
   - Title + Metric + Chart/Progress

---

## Phase 3: Screen Design (Day 4-6)

### Step 7: Member Portal Screens

#### Home Dashboard
1. Create 1440x900 frame
2. Add navigation header
3. Layout:
   - Welcome section with quick actions
   - Coverage summary card
   - Recent claims table
   - Quick links footer

#### Claim Submission Flow
1. **Step 1**: Service type selection (grid of cards)
2. **Step 2**: Details form
3. **Step 3**: Document upload
4. **Step 4**: Review & submit
5. **Step 5**: Confirmation

#### Coverage & Benefits
- Benefits grid with limits and usage
- Downloadable ID card
- Policy documents list

### Step 8: Provider Portal Screens

#### Provider Dashboard
1. Today's overview metrics
2. Real-time patient queue
3. Quick action buttons

#### Eligibility Check
1. Member search/scan
2. Results display
3. Coverage details card

#### Authorization Request
1. Multi-step form
2. Document attachment
3. Cost estimation

### Step 9: Mobile App Screens (30+ screens)

#### Authentication Flow
1. **Splash Screen**:
   - Logo animation
   - Loading indicator

2. **Onboarding** (3 screens):
   - Welcome
   - Key features
   - Get started

3. **Login**:
   - Phone number input
   - OTP verification
   - Biometric setup

#### Main App Screens
1. **Home**:
   - User greeting
   - Quick actions grid
   - Coverage summary
   - Recent activity

2. **Digital Insurance Card**:
   - Flippable card design
   - QR code
   - Download/share options

3. **Claims**:
   - Claims list with filters
   - Claim details
   - Submit new claim

4. **Smart Camera**:
   - Viewfinder with guides
   - Auto-capture indicators
   - Review & retake

5. **Provider Search**:
   - Map view
   - List view
   - Filter options
   - Provider details

---

## Phase 4: Prototyping (Day 7)

### Step 10: Create User Flows

1. **Member Journey**:
   ```
   Login → Home → Submit Claim → Camera → Review → Success
   ```

2. **Provider Journey**:
   ```
   Login → Dashboard → Check Eligibility → Request Auth → Approved
   ```

3. **Mobile App Flow**:
   ```
   Onboarding → Login → Home → Card → Claims → Profile
   ```

### Step 11: Add Interactions

1. **Smart Animate** between screens
2. **Overlay** for modals and sheets
3. **Scroll** for long content
4. **On Tap** for buttons and links
5. **After Delay** for auto-progression

### Step 12: Micro-interactions

1. **Button States**:
   - Hover: Slight color change
   - Press: Scale 0.95
   - Loading: Spinner replace text

2. **Card Interactions**:
   - Hover: Elevate shadow
   - Tap: Ripple effect

3. **Form Validation**:
   - Real-time error display
   - Success checkmarks

---

## Phase 5: Developer Handoff (Day 8)

### Step 13: Prepare for Development

1. **Enable Dev Mode**:
   - Set up measurement units (px)
   - Configure code snippets
   - Add implementation notes

2. **Document Components**:
   ```
   Each component should have:
   - Description
   - Props/variants
   - States
   - Usage guidelines
   ```

3. **Export Assets**:
   - Icons: SVG format
   - Images: PNG @1x, @2x, @3x
   - Logos: SVG + PNG

### Step 14: Create Documentation

1. **Component Specs**:
   ```markdown
   ## Button Component
   
   ### Variants
   - Primary: Main actions
   - Secondary: Alternative actions
   - Danger: Destructive actions
   
   ### Sizes
   - Small: 32px height
   - Medium: 40px height
   - Large: 48px height
   
   ### States
   - Default
   - Hover
   - Pressed
   - Disabled
   - Loading
   ```

2. **Design Token Reference**:
   - Color palette with hex values
   - Typography scale
   - Spacing system
   - Border radius values

### Step 15: Quality Check

#### Design Checklist
- [ ] All screens designed for mobile & desktop
- [ ] Components have all necessary variants
- [ ] Colors pass WCAG AA contrast
- [ ] Touch targets ≥ 44x44px
- [ ] Text is readable (14px minimum)

#### Prototype Checklist
- [ ] All major flows connected
- [ ] Interactions feel natural
- [ ] Loading states included
- [ ] Error states designed
- [ ] Empty states covered

#### Handoff Checklist
- [ ] Dev mode configured
- [ ] Assets exported correctly
- [ ] Documentation complete
- [ ] Naming consistent
- [ ] Specs accurate

---

## Quick Tips for Figma

### Keyboard Shortcuts
- `C` - Comment
- `K` - Scale tool
- `Shift + A` - Auto layout
- `Cmd/Ctrl + D` - Duplicate
- `Cmd/Ctrl + G` - Group
- `Option/Alt + drag` - Duplicate

### Best Practices
1. **Use Auto Layout** for responsive behavior
2. **Create Components** for reusable elements
3. **Name Layers** descriptively
4. **Group Related Elements**
5. **Use Constraints** for responsive design
6. **Apply Styles** consistently

### Performance Tips
1. Limit effects (shadows, blurs)
2. Use instances vs copies
3. Optimize images before importing
4. Clean up hidden layers
5. Use components for repeated elements

---

## Resources & References

### Figma Plugins to Install
1. **Iconify** - Icon library
2. **Unsplash** - Stock photos
3. **Lorem Ipsum** - Placeholder text
4. **Stark** - Accessibility checker
5. **Figma to Code** - HTML/CSS export

### Design Inspiration
- Dribbble: Health insurance UI
- Behance: Medical app designs
- Material Design: Component patterns
- Human Interface Guidelines: Mobile patterns

### Indonesian Context
- Use Rupiah (Rp) formatting
- Include local provider names
- Support Bahasa Indonesia labels
- Consider local color preferences
- Include WhatsApp integration

---

## Timeline Summary

| Day | Phase | Deliverables |
|-----|-------|-------------|
| 1 | Setup | File structure, tokens, grids |
| 2-3 | Components | Atoms, molecules, organisms |
| 4-6 | Screens | All portals and mobile app |
| 7 | Prototyping | User flows, interactions |
| 8 | Handoff | Dev mode, documentation |

## Final Deliverables

1. ✅ Complete Figma file with all screens
2. ✅ Component library with variants
3. ✅ Interactive prototypes
4. ✅ Design system documentation
5. ✅ Developer handoff specs
6. ✅ Exported assets

---

*Start implementing now! Open Figma and begin with Phase 1.*
*Questions? Refer to the design specifications documents.*