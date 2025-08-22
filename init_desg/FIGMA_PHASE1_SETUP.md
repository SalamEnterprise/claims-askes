# 🎨 Figma Phase 1: Complete Setup Instructions

## Prerequisites
1. Open Figma Desktop App or Web
2. Create a new design file
3. Rename it to: **"Claims-Askes-Health-Insurance-Design-System"**

---

## Step 1: Create Page Structure

### In Figma:
1. Right-click on "Page 1" → Rename to "📄 Cover"
2. Click the "+" next to Pages
3. Add these pages in order:
   - 🎨 Design Tokens
   - 🧩 Components
   - 👤 Member Portal
   - 🏥 Provider Portal
   - 📊 Admin Dashboard
   - 📱 Mobile App
   - 🔗 Prototypes
   - 📚 Documentation

---

## Step 2: Set Up Color Styles

### Navigate to "🎨 Design Tokens" page

### Create Color Documentation Frame:
1. Press `F` (Frame tool)
2. Click and drag to create a 1920×1080 frame
3. Name it "Color System"

### Add Color Styles (Right Panel → Styles → +):

#### Primary Colors
```
Primary/100 → #E6F2FF
Primary/200 → #B3D9FF
Primary/300 → #80BFFF
Primary/400 → #4DA6FF
Primary/500 → #0080FF
Primary/600 → #0066CC (Main)
Primary/700 → #004D99
Primary/800 → #003366
Primary/900 → #001A33
```

#### Semantic Colors
```
Success/Light → #E8F5E9
Success/Base → #4CAF50
Success/Dark → #2E7D32

Warning/Light → #FFF8E1
Warning/Base → #FFC107
Warning/Dark → #F57C00

Error/Light → #FFEBEE
Error/Base → #E91E63
Error/Dark → #C2185B

Info/Light → #E0F2F1
Info/Base → #17A2B8
Info/Dark → #006064
```

#### Neutral Colors
```
Neutral/0 → #FFFFFF
Neutral/50 → #FAFAFA
Neutral/100 → #F5F5F5
Neutral/200 → #EEEEEE
Neutral/300 → #E0E0E0
Neutral/400 → #BDBDBD
Neutral/500 → #9E9E9E
Neutral/600 → #757575
Neutral/700 → #616161
Neutral/800 → #424242
Neutral/900 → #212121
Neutral/1000 → #000000
```

### How to Add Each Color Style:
1. Create a rectangle (R key)
2. Set size to 120×120px
3. Apply the color hex value
4. Select the rectangle
5. In right panel, click Style icon (four dots) next to Fill
6. Click "+" to create style
7. Name it (e.g., "Primary/600")
8. Add description (e.g., "Main brand color for primary actions")

---

## Step 3: Set Up Typography Styles

### Create Typography Documentation Frame:
1. Press `F` → Create 1920×1080 frame
2. Name it "Typography System"

### Add Text Styles:

#### Display
- **Font**: Inter
- **Weight**: Bold (700)
- **Size**: 48px
- **Line Height**: 56px
- **Letter Spacing**: -2%

#### Heading 1
- **Font**: Inter
- **Weight**: SemiBold (600)
- **Size**: 36px
- **Line Height**: 44px
- **Letter Spacing**: -1.5%

#### Heading 2
- **Font**: Inter
- **Weight**: SemiBold (600)
- **Size**: 28px
- **Line Height**: 36px
- **Letter Spacing**: -1%

#### Heading 3
- **Font**: Inter
- **Weight**: Medium (500)
- **Size**: 24px
- **Line Height**: 32px
- **Letter Spacing**: 0%

#### Heading 4
- **Font**: Inter
- **Weight**: Medium (500)
- **Size**: 20px
- **Line Height**: 28px
- **Letter Spacing**: 0%

#### Body
- **Font**: Inter
- **Weight**: Regular (400)
- **Size**: 16px
- **Line Height**: 24px
- **Letter Spacing**: 0%

#### Body Small
- **Font**: Inter
- **Weight**: Regular (400)
- **Size**: 14px
- **Line Height**: 20px
- **Letter Spacing**: 0%

#### Caption
- **Font**: Inter
- **Weight**: Regular (400)
- **Size**: 12px
- **Line Height**: 16px
- **Letter Spacing**: 0%

#### Button
- **Font**: Inter
- **Weight**: Medium (500)
- **Size**: 14px
- **Line Height**: 20px
- **Letter Spacing**: 0.5px
- **Text Transform**: None

#### Overline
- **Font**: Inter
- **Weight**: SemiBold (600)
- **Size**: 12px
- **Line Height**: 16px
- **Letter Spacing**: 1px
- **Text Transform**: UPPERCASE

### How to Add Each Text Style:
1. Press `T` (Text tool)
2. Type sample text (e.g., "Heading 1")
3. Apply the font settings above
4. Select the text
5. In right panel, click Style icon next to Text properties
6. Click "+" to create style
7. Name it (e.g., "Heading 1")

---

## Step 4: Set Up Spacing & Layout Variables

### Create Local Variables:
1. Open Local Variables panel (Resources → Local Variables)
2. Create new collection: "Spacing"
3. Add Number variables:

```
spacing/0 → 0
spacing/1 → 4
spacing/2 → 8
spacing/3 → 12
spacing/4 → 16
spacing/5 → 20
spacing/6 → 24
spacing/8 → 32
spacing/10 → 40
spacing/12 → 48
spacing/16 → 64
spacing/20 → 80
```

### Create Border Radius Variables:
1. Create collection: "Radius"
2. Add Number variables:

```
radius/none → 0
radius/sm → 4
radius/base → 8
radius/md → 12
radius/lg → 16
radius/xl → 24
radius/full → 999
```

---

## Step 5: Set Up Grid Styles

### Desktop Grid (1200px container):
1. Create frame: 1440×900px
2. Name: "Desktop Container"
3. Add Layout Grid:
   - Type: Columns
   - Count: 12
   - Gutter: 32px
   - Margin: 32px
   - Color: #E91E63 (10% opacity)

### Tablet Grid (768px):
1. Create frame: 768×1024px
2. Name: "Tablet Container"
3. Add Layout Grid:
   - Type: Columns
   - Count: 8
   - Gutter: 24px
   - Margin: 24px

### Mobile Grid (375px):
1. Create frame: 375×812px (iPhone 13 size)
2. Name: "Mobile Container"
3. Add Layout Grid:
   - Type: Columns
   - Count: 4
   - Gutter: 16px
   - Margin: 16px

### Save as Grid Styles:
1. Select frame with grid
2. In right panel → Layout Grid → Style icon
3. Click "+" to save as style
4. Name appropriately (e.g., "Grid/Desktop")

---

## Step 6: Create Effect Styles (Shadows)

### Shadow Styles:
1. Create a 100×100px rectangle
2. Apply shadow effect
3. Save as style

#### Shadow/XS
- X: 0, Y: 1
- Blur: 2
- Color: #000000 (5% opacity)

#### Shadow/SM
- X: 0, Y: 2
- Blur: 4
- Color: #000000 (8% opacity)

#### Shadow/Base
- X: 0, Y: 4
- Blur: 8
- Color: #000000 (12% opacity)

#### Shadow/MD
- X: 0, Y: 6
- Blur: 12
- Color: #000000 (15% opacity)

#### Shadow/LG
- X: 0, Y: 8
- Blur: 16
- Color: #000000 (18% opacity)

#### Shadow/XL
- X: 0, Y: 12
- Blur: 24
- Color: #000000 (20% opacity)

---

## Step 7: Create Cover Page

### Navigate to "📄 Cover" page:

1. Create frame: 1920×1080px
2. Fill: Linear gradient (Primary/600 → Primary/900)
3. Add elements:

#### Title Section:
```
Claims Askes
Health Insurance Design System
```
- Use Display text style
- Color: White
- Center aligned

#### Version Badge:
```
v1.0.0
August 2025
```
- Use Body Small style
- Background: White (20% opacity)
- Padding: 8px 16px
- Border radius: 24px

#### Sections Grid (2×2):
```
[🧩 Components]    [👤 Member Portal]
[🏥 Provider]      [📱 Mobile App]
```
- Each card: 400×200px
- Background: White (10% opacity)
- Border: 1px white (30% opacity)
- On hover: White (20% opacity)

---

## Step 8: Documentation Setup

### Navigate to "📚 Documentation" page:

Create these documentation frames:

1. **Getting Started** (1920×1080)
   - How to use the design system
   - File structure
   - Naming conventions

2. **Design Principles** (1920×1080)
   - Accessibility
   - Responsiveness
   - Indonesian context

3. **Component Guidelines** (1920×1080)
   - Usage rules
   - Do's and Don'ts
   - Examples

---

## Step 9: Set Up Auto Layout Defaults

### Configure Auto Layout Settings:
1. Preferences → Auto Layout
2. Set default spacing: 16px
3. Set default padding: 16px
4. Enable: "Nested auto layout"

---

## Step 10: Create Starter Components Frame

### Navigate to "🧩 Components" page:

1. Create frame: 1920×5000px (tall for components)
2. Name: "Component Library"
3. Add sections:

#### Section Headers (using Auto Layout):
```
[ Atoms ]
- Buttons
- Inputs  
- Icons
- Badges

[ Molecules ]
- Cards
- Form Fields
- Navigation Items

[ Organisms ]
- Headers
- Forms
- Modals
```

---

## Verification Checklist

### ✅ Pages Created:
- [ ] Cover
- [ ] Design Tokens
- [ ] Components
- [ ] Member Portal
- [ ] Provider Portal
- [ ] Admin Dashboard
- [ ] Mobile App
- [ ] Prototypes
- [ ] Documentation

### ✅ Styles Created:
- [ ] 9 Primary colors
- [ ] 12 Semantic colors
- [ ] 12 Neutral colors
- [ ] 10 Text styles
- [ ] 6 Shadow effects
- [ ] 3 Grid styles

### ✅ Variables Created:
- [ ] Spacing (12 values)
- [ ] Border radius (7 values)

### ✅ Frames Created:
- [ ] Cover design
- [ ] Color documentation
- [ ] Typography documentation
- [ ] Grid examples
- [ ] Component structure

---

## Next Steps

After completing Phase 1:
1. **Save your file** (Cmd/Ctrl + S)
2. **Share link** for collaboration
3. **Proceed to Phase 2**: Building Components

## Quick Tips

### Figma Shortcuts for Phase 1:
- `F` - Frame tool
- `R` - Rectangle
- `T` - Text
- `Shift + A` - Add Auto Layout
- `Cmd/Ctrl + D` - Duplicate
- `Cmd/Ctrl + G` - Group selection

### Organization Tips:
1. Use consistent naming
2. Group related elements
3. Lock backgrounds
4. Use frames not groups for layouts
5. Comment important decisions

---

**Phase 1 Complete! ✨**
Your design system foundation is now ready.
Time to build components in Phase 2!