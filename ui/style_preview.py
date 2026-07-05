"""Font and subtitle style utility functions for Gradio UI."""
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import gradio as gr

class StylePreview:
    def __init__(self, fonts_map, fonts_default):
        self.fonts_map = fonts_map
        self.fonts_default = fonts_default

    def update_style_controls(self, style):
        """Update the visibility of style controls based on the selected style."""
        # Gradio expects separate return values for each output component.
        visible_update = gr.update(visible=style != "None")
        return visible_update, visible_update

    def update_subtitle_preview(self, font_name, font_size, primary_hex, outline_w,
                              outline_hex, subtitle_style):
        """Generate a preview image of the subtitle style."""
        try:
            # Create preview image
            img = Image.new('RGB', (400, 150), color='#404040')
            draw = ImageDraw.Draw(img)
            
            # Load font
            font_path = self.fonts_map.get(font_name, self.fonts_map[self.fonts_default])
            try:
                font = ImageFont.truetype(font_path, int(font_size))
            except:
                font = ImageFont.load_default()
            
            sample_text = "Sample Subtitle Text"
            bbox = draw.textbbox((0, 0), sample_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (400 - text_width) // 2
            y = (150 - text_height) // 2
            
            # Draw background/outline based on style
            if subtitle_style == "Box":
                padding = int(outline_w) + 5
                draw.rectangle(
                    [x - padding, y - padding,
                     x + text_width + padding, y + text_height + padding],
                    fill=outline_hex
                )
            elif subtitle_style == "Outline" and outline_w:
                for offset_x in range(-int(outline_w), int(outline_w)+1):
                    for offset_y in range(-int(outline_w), int(outline_w)+1):
                        draw.text((x + offset_x, y + offset_y), sample_text,
                                font=font, fill=outline_hex)
            
            # Draw main text
            draw.text((x, y), sample_text, font=font, fill=primary_hex)
            
            return img
        except Exception as e:
            print(f"Preview generation error: {e}")
            return None