# RITC Template Development Prompt

## Context
Rhode Island Track Club needs six social media templates for Instagram posts. First template (workout announcement) is complete and validated. Now building race recap template as priority #2.

## Brand Requirements
- **Canvas**: 2160x2700px (exports at 2x, displays at 1080x1350)
- **Color palette**: Navy (#001F3F) primary, sand (#D2B48C) accents, white typography
- **Typography**: Vendored fonts in assets/fonts/ (56KB total)
- **Logo**: Transparent PNG/SVG required in assets/logo/ (currently missing - use placeholder)
- **Layout hierarchy**: Sand warmups (outer layer), navy singlet (middle), star column (seam detail)

## Template Specifications - Race Recap
- **Frame**: NO frame (this is the key differentiator from workout announcement)
- **Strip Rule**: Must validate that layout works without containing frame
- **Photo Treatment**: Primary photo with scrim overlay (gradient math validated against bright singlets on wet roads)
- **Copy Block**: Headline auto-fitter using Range client rects (96px → 90px for long names)
- **Badge**: Positioned in 200px waistband (corrected from original 56px spec)
- **Empty State**: If no photo provided, maintain navy negative space with centered copy block

## Technical Requirements
- Network-independent: All assets vendored locally
- Export-ready: Canvas clips exactly to 2160x2700, no viewport artifacts
- Responsive typography: Auto-fits headlines 13-45 characters
- Robust image handling: No broken image icons, proper fallback states

## Validation Criteria
- Passes visual regression against workout announcement template
- Maintains brand consistency while demonstrating no-frame capability  
- Photo scrim works over bright colors (validate with sample race photos)
- All text remains readable with proper contrast ratios
- Exports clean files ready for social media upload

## Deliverables
1. Complete race recap template HTML/CSS/JS
2. Updated BRAND.md documenting no-frame specifications
3. Test cases covering edge scenarios (long names, missing photos, etc.)
4. Validation report confirming strip rule implementation

## Next Steps After Race Recap
- Apply learnings to remaining four templates
- Implement shared component library
- Establish batch processing workflow