# 🎨 Figma Implementation Guide - Claims Askes Mobile App

**Version**: 1.0  
**Last Updated**: August 15, 2025  
**Figma File Structure**: Claims-Askes-Mobile-Design-System

---

## 📁 FIGMA FILE ORGANIZATION

### Page Structure
```
📄 Claims-Askes Mobile Design
├── 📑 1. Cover & Documentation
├── 📑 2. Design System
│   ├── Colors & Tokens
│   ├── Typography
│   ├── Grid & Spacing
│   ├── Icons
│   └── Effects & Shadows
├── 📑 3. Components
│   ├── Atoms
│   ├── Molecules
│   ├── Organisms
│   └── Templates
├── 📑 4. Screens - Onboarding
├── 📑 5. Screens - Authentication
├── 📑 6. Screens - Dashboard
├── 📑 7. Screens - Claims
├── 📑 8. Screens - Digital Card
├── 📑 9. Screens - Providers
├── 📑 10. Screens - Profile
├── 📑 11. Prototypes
└── 📑 12. Handoff & Specs
```

---

## 🎨 DESIGN SYSTEM SETUP

### 1. Color Styles
```
Create these color styles in Figma:

Primary/
├── primary/100 → #E6F2FF
├── primary/200 → #B3D9FF
├── primary/300 → #80BFFF
├── primary/400 → #4DA6FF
├── primary/500 → #0066CC (main)
├── primary/600 → #0052A3
├── primary/700 → #004499
├── primary/800 → #003366
├── primary/900 → #001A33

Semantic/
├── success/main → #4CAF50
├── success/light → #E8F5E9
├── warning/main → #FFC107
├── warning/light → #FFF8E1
├── error/main → #E91E63
├── error/light → #FCE4EC
├── info/main → #2196F3
├── info/light → #E3F2FD

Neutral/
├── gray/50 → #FAFAFA
├── gray/100 → #F5F5F5
├── gray/200 → #EEEEEE
├── gray/300 → #E0E0E0
├── gray/400 → #BDBDBD
├── gray/500 → #9E9E9E
├── gray/600 → #757575
├── gray/700 → #616161
├── gray/800 → #424242
├── gray/900 → #212121

Health Status/
├── health/green → #00B74A
├── health/orange → #FF9800
├── health/red → #F44336
```

### 2. Text Styles
```
Create these text styles:

Display/
├── display/large
│   Font: Inter Bold
│   Size: 32px
│   Line: 40px (125%)
│   Letter: -0.02em
│
├── display/medium
│   Font: Inter SemiBold
│   Size: 28px
│   Line: 36px (128%)
│   Letter: -0.01em

Title/
├── title/large
│   Font: Inter SemiBold
│   Size: 22px
│   Line: 30px (136%)
│   Letter: 0
│
├── title/medium
│   Font: Inter Medium
│   Size: 18px
│   Line: 26px (144%)
│   Letter: 0.01em
│
├── title/small
│   Font: Inter Medium
│   Size: 16px
│   Line: 24px (150%)
│   Letter: 0.01em

Body/
├── body/large
│   Font: Inter Regular
│   Size: 16px
│   Line: 24px (150%)
│   Letter: 0.005em
│
├── body/medium
│   Font: Inter Regular
│   Size: 14px
│   Line: 20px (143%)
│   Letter: 0.01em
│
├── body/small
│   Font: Inter Regular
│   Size: 12px
│   Line: 16px (133%)
│   Letter: 0.01em

Caption/
├── caption
│   Font: Inter Regular
│   Size: 12px
│   Line: 16px (133%)
│   Letter: 0.02em
│
└── overline
    Font: Inter Medium
    Size: 10px
    Line: 14px (140%)
    Letter: 0.05em
    Transform: UPPERCASE
```

### 3. Effect Styles
```
Shadows/
├── elevation/1
│   Shadow: 0px 1px 3px rgba(0,0,0,0.12)
│   Shadow: 0px 1px 2px rgba(0,0,0,0.24)
│
├── elevation/2
│   Shadow: 0px 3px 6px rgba(0,0,0,0.16)
│   Shadow: 0px 3px 6px rgba(0,0,0,0.23)
│
├── elevation/3
│   Shadow: 0px 10px 20px rgba(0,0,0,0.19)
│   Shadow: 0px 6px 6px rgba(0,0,0,0.23)
│
└── elevation/4
    Shadow: 0px 14px 28px rgba(0,0,0,0.25)
    Shadow: 0px 10px 10px rgba(0,0,0,0.22)

Blur Effects/
├── background/blur
│   Background Blur: 20px
│   Fill: rgba(255,255,255,0.8)
│
└── overlay/blur
    Background Blur: 10px
    Fill: rgba(0,0,0,0.5)
```

### 4. Grid & Layout
```
Mobile Grid/
├── Columns: 4
├── Gutter: 16px
├── Margin: 16px
├── Max Width: 375px (iPhone)

Spacing Tokens/
├── space-xxs: 4px
├── space-xs: 8px
├── space-sm: 12px
├── space-md: 16px
├── space-lg: 24px
├── space-xl: 32px
├── space-xxl: 48px

Corner Radius/
├── radius-xs: 4px
├── radius-sm: 8px
├── radius-md: 12px
├── radius-lg: 16px
├── radius-xl: 24px
├── radius-full: 999px
```

---

## 🧩 COMPONENT LIBRARY

### Atoms

#### Button Component
```
Component Set: Button
Variants:
├── Type: Primary | Secondary | Text | Ghost
├── Size: Large | Medium | Small
├── State: Default | Hover | Pressed | Disabled
├── Icon: None | Leading | Trailing | Only

Properties:
├── Text (string)
├── Show Icon (boolean)
├── Icon Instance (swap)

Structure:
Frame [Auto Layout]
├── Icon (16x16) [optional]
├── Text Layer
└── Icon (16x16) [optional]

Styles:
Primary/Large/Default:
- Fill: primary/500
- Corner: radius-md
- Padding: 16px 24px
- Text: button/large (white)

Interactive Components:
Default → Hover: Fill primary/600
Hover → Pressed: Fill primary/700, Scale 0.98
```

#### Input Field Component
```
Component Set: Input
Variants:
├── Type: Text | Password | Search | Number
├── State: Default | Focus | Filled | Error | Disabled
├── Helper: None | Helper | Error

Properties:
├── Label (string)
├── Placeholder (string)
├── Value (string)
├── Helper Text (string)
├── Show Icon (boolean)

Structure:
Frame [Auto Layout, Vertical]
├── Label Row
│   ├── Label Text
│   └── Required Indicator (*)
├── Input Container
│   ├── Leading Icon [optional]
│   ├── Input Text / Placeholder
│   ├── Trailing Icon [optional]
│   └── Border [stroke]
└── Helper Row
    ├── Helper Icon
    └── Helper Text

States:
Default: Border gray/300, 1px
Focus: Border primary/500, 2px
Error: Border error/main, 1px
```

#### Card Component
```
Component Set: Card
Variants:
├── Type: Elevated | Outlined | Filled
├── Padding: None | Small | Medium | Large

Structure:
Frame [Auto Layout]
├── Card Content (slot)
└── Effects/Shadows

Elevated:
- Fill: white
- Shadow: elevation/2
- Corner: radius-md

Outlined:
- Fill: white
- Stroke: gray/200, 1px
- Corner: radius-md
```

### Molecules

#### Claim Card Component
```
Component: ClaimCard
Properties:
├── Status (Approved | Pending | Rejected)
├── Provider Name (string)
├── Claim ID (string)
├── Service Type (string)
├── Amount (string)
├── Date (string)

Structure:
Card [Base Card Component]
├── Status Row [Auto Layout]
│   ├── Status Icon (12x12)
│   └── Provider Name
├── Content [Auto Layout]
│   ├── Claim ID
│   ├── Service Type
│   └── Amount
└── Footer [Auto Layout]
    ├── Date
    └── Action Button

Status Styles:
Approved: Icon & Text success/main
Pending: Icon & Text warning/main
Rejected: Icon & Text error/main
```

#### Bottom Navigation
```
Component: BottomNav
Properties:
├── Active Tab (Home | Claims | Card | Provider | Profile)

Structure:
Frame [Fixed Bottom]
├── Tab Item [Component]
│   ├── Icon (24x24)
│   ├── Label
│   └── Badge [optional]
└── (repeat for 5 tabs)

Tab States:
Active: Icon primary/500, Text primary/500
Inactive: Icon gray/500, Text gray/500

Interactions:
- Tap to switch active state
- Micro animation on selection
```

### Organisms

#### Insurance Card Component
```
Component: InsuranceCard
Properties:
├── Plan Type (Gold | Silver | Bronze)
├── Member Name (string)
├── Member ID (string)
├── Valid Until (string)

Structure:
Frame [Fixed: 343x216] // Card ratio
├── Background Gradient
├── Plan Badge
├── Member Info [Auto Layout]
│   ├── Name
│   └── ID
├── Validity Info
└── QR Code Placeholder

Variants:
├── Front View
└── Back View (QR Code)

Interactions:
- Tap to flip animation
- Component variant switching
```

#### Claim Camera Viewfinder
```
Component: CameraViewfinder
Properties:
├── Detection Status (Ready | Scanning | Success)
├── Guidelines (Show/Hide)

Structure:
Frame [Full Screen]
├── Camera Feed [Image Fill]
├── Overlay [Absolute]
│   ├── Corner Guides
│   ├── Center Frame
│   └── Status Messages
├── Bottom Controls
│   ├── Gallery Button
│   ├── Capture Button
│   └── Flash Toggle
└── Top Bar
    ├── Close Button
    └── Tips Button

States:
Ready: White guides, "Position document"
Scanning: Animated guides, "Hold steady"
Success: Green guides, "Document captured"
```

---

## 📱 SCREEN TEMPLATES

### Screen Template Structure
```
Each screen should follow:

Frame: iPhone 14 (390x844)
├── Status Bar (System)
├── Navigation Bar / Header
├── Content Area [Scroll]
│   └── Safe Area Padding
└── Bottom Navigation / CTA
```

### Creating Responsive Screens
```
Use Constraints:
- Status Bar: Fixed Top
- Nav Bar: Fixed Top, Stretch H
- Content: Stretch Both
- Bottom Nav: Fixed Bottom, Stretch H

Auto Layout Settings:
- Direction: Vertical
- Spacing: Between items
- Padding: 16px horizontal
- Alignment: Center or Stretch
```

---

## 🎬 PROTOTYPING

### Navigation Flows
```
1. Main Tab Navigation
Home → Claims → Card → Provider → Profile
Trigger: On Tap
Animation: Smart Animate, 300ms

2. Claim Submission Flow
Claims List → New Claim → Camera → Review → Success
Trigger: On Tap
Animation: Slide in from Right, 300ms

3. Authentication Flow
Splash → Login → OTP → Home
Trigger: After Delay / On Tap
Animation: Dissolve, 200ms
```

### Micro-interactions
```
Button Press:
Trigger: While Pressing
Action: Scale 0.95
Animation: Spring, 200ms

Card Flip:
Trigger: On Tap
Action: Swap Variant
Animation: Smart Animate, 600ms

Loading State:
Trigger: After Delay
Action: Show Overlay
Animation: Dissolve, 200ms
```

### Prototype Settings
```
Device: iPhone 14 Pro
Starting Frame: Splash Screen
Background: System Gray
Show Prototype Settings: On
```

---

## 🔄 COMPONENT INSTANCES & OVERRIDES

### Creating Instances
```
1. Select master component
2. Copy (Cmd/Ctrl + C)
3. Paste in screen (Cmd/Ctrl + V)
4. Override properties as needed

Best Practices:
- Never detach instances
- Use component properties
- Maintain naming convention
- Group related instances
```

### Managing Variants
```
Button Example:
Default Instance: Button/Primary/Large/Default
Override Type → Secondary
Override Size → Medium
Result: Button/Secondary/Medium/Default

Auto-updates when master changes
```

---

## 📐 DESIGN TOKENS IN FIGMA

### Setting Up Variables (Figma Variables)
```
Collections:
├── Primitives
│   ├── Colors
│   ├── Numbers
│   └── Strings
├── Semantic
│   ├── Colors
│   ├── Spacing
│   └── Radius
└── Component
    ├── Button
    ├── Input
    └── Card

Variable Modes:
├── Light Mode (Default)
└── Dark Mode

Example:
color.primary = #0066CC (Light)
color.primary = #4D9FFF (Dark)
```

### Token Application
```
Instead of hard-coded values:
Fill: #0066CC ❌

Use variables:
Fill: {color.primary} ✅

Benefits:
- Single source of truth
- Easy theme switching
- Consistent updates
```

---

## 🤝 DEVELOPER HANDOFF

### Inspect Panel Setup
```
Settings:
├── Code Syntax: CSS/iOS/Android
├── Unit: PX/PT/DP
├── Color Format: HEX/RGB/HSL
└── Include: Styles & Variables

Export Settings:
├── iOS: @1x, @2x, @3x
├── Android: mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi
└── Web: SVG, PNG @1x, @2x
```

### Documentation Layers
```
Add these frames for specs:

Redlines:
├── Spacing measurements
├── Component dimensions
├── Touch targets (44x44 minimum)
└── Safe areas

Annotations:
├── Interaction notes
├── Animation specs
├── State changes
└── Edge cases
```

### Asset Export
```
Icons:
- Format: SVG
- Naming: ic_[name]_[size]
- Example: ic_home_24

Images:
- Format: PNG/JPG
- Naming: img_[description]_[size]
- Example: img_onboarding_1_375

Logos:
- Format: SVG + PNG
- Variations: Full, Icon only
```

---

## 🎯 FIGMA PLUGINS RECOMMENDED

### Essential Plugins
```
1. Figma Tokens
   - Manage design tokens
   - Sync with code

2. Stark
   - Accessibility checking
   - Color contrast validation

3. Content Reel
   - Realistic data population
   - Indonesian names/addresses

4. Figmotion
   - Animation specifications
   - Micro-interaction details

5. Design Lint
   - Find design inconsistencies
   - Missing styles detection

6. Able
   - Color blind simulation
   - WCAG compliance check

7. Lorem Ipsum
   - Indonesian placeholder text
   - Realistic content

8. Unsplash
   - Stock photos for avatars
   - Medical imagery
```

---

## 📋 QUALITY CHECKLIST

### Before Handoff
```
□ All colors use color styles
□ All text uses text styles
□ Components properly named
□ Variants cover all states
□ Auto-layout implemented
□ Constraints set correctly
□ Interactions prototyped
□ Accessibility checked
□ Content is realistic
□ Export settings configured
□ Documentation complete
□ Edge cases designed
□ Error states included
□ Loading states included
□ Empty states included
```

### Component Checklist
```
□ Named following convention
□ Description added
□ Properties configured
□ Variants complete
□ States designed
□ Documentation linked
□ Used consistently
□ Responsive behavior set
```

---

## 🚀 FIGMA BEST PRACTICES

### Naming Conventions
```
Frames: Screen Name / State
Components: Component/Variant/Size/State
Layers: Descriptive names (no "Frame 123")
Styles: category/variant/shade
```

### Organization
```
- Use pages for major sections
- Group related components
- Maintain consistent spacing
- Use consistent grid
- Keep master components separate
- Version control with branches
```

### Performance
```
- Limit effects per layer
- Optimize images before import
- Use instances not copies
- Clean up hidden layers
- Merge unnecessary groups
- Archive old iterations
```

---

## 📦 DELIVERY STRUCTURE

### Figma Links
```
View Only Link: [For stakeholders]
figma.com/file/xxx/view

Dev Mode Link: [For developers]
figma.com/file/xxx/dev

Prototype Link: [For testing]
figma.com/proto/xxx
```

### Export Package
```
📁 Claims-Askes-Mobile-Design/
├── 📁 Design Files/
│   ├── Figma File (.fig)
│   └── Sketch Backup (.sketch)
├── 📁 Assets/
│   ├── 📁 Icons/
│   ├── 📁 Images/
│   └── 📁 Logos/
├── 📁 Documentation/
│   ├── Design System.pdf
│   ├── Component Specs.pdf
│   └── Interaction Guide.pdf
└── 📁 Tokens/
    ├── tokens.json
    └── variables.css
```

---

## 🔄 VERSION CONTROL

### Figma Branching
```
main (Protected)
├── feature/claims-flow
├── feature/new-dashboard
└── experiment/dark-mode

Merge Process:
1. Create branch for feature
2. Design and iterate
3. Review with team
4. Merge to main
5. Archive branch
```

---

*This implementation guide provides complete instructions for creating the Claims-Askes mobile app design in Figma. Follow these specifications to ensure consistency and production readiness.*