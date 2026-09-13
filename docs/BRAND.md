# Rhode Island Track Club Brand Specifications

## Overview
Rhode Island Track Club (RITC) is a competitive running organization with a focus on athletic performance, local pride, and authentic running culture.

## Color Palette
- **Primary Navy**: `#001F3F`
- **Sand Accent**: `#D2B48C` 
- **White**: `#FFFFFF`

## Typography
- Fonts are vendored in `assets/fonts/` (56KB total)
- Network-independent for reliable exports
- Auto-fitting headline system using Range client rects

## Canvas Specifications
- **Base Display**: 1080px × 1350px
- **Export Resolution**: 2160px × 2700px (2x scaling)
- **Waistband Area**: 200px height at bottom (corrected from original 56px spec)

## Visual Hierarchy
Template layering follows authentic athletic gear construction:
1. **Outer Layer**: Sand warmups
2. **Middle Layer**: Navy singlet  
3. **Detail Element**: Star column on seam
4. **Badge Placement**: In waistband area

## Template Types
### Framed Templates
- Workout announcements
- Include containing frame around content

### Frameless Templates  
- Race recaps
- Test "strip rule" - layout must work without frame
- Primary photo with scrim overlay

## Photo Treatment
- **Scrim System**: Gradient overlay for text readability over photos
- **Validation Required**: Must work over bright singlets on wet roads
- **Empty State**: When no photo provided, maintain navy negative space as deliberate brand signature

## Asset Requirements
### Logo Files
- **Format**: Transparent PNG + SVG
- **Location**: `assets/logo/{png,svg}/`
- **Variants**: Navy primary, white reverse, sand accent
- **Dimensions**: Min 1000px wide for wordmarks, 500px for icons

### Font Files  
- **Location**: `assets/fonts/`
- **Total Size**: 56KB
- **Purpose**: Eliminate network dependencies for exports

## Export Standards
- Files must be exactly 2160x2700px
- Canvas clips to exact dimensions (no viewport artifacts)
- Network-independent (all assets vendored locally)
- Optimized for Instagram social media

## Template Development Sequence
1. Workout announcement (completed)
2. Race recap (validates no-frame scenario)  
3. Remaining four templates (apply learnings from first two)

## Quality Assurance
- Visual regression testing against established templates
- Content variability testing (13-45 character headlines)
- Photo overlay validation with real race conditions
- Cross-browser compatibility for SVG assets