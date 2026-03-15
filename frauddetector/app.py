import gradio as gr
from gradio.themes import Soft
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
from io import BytesIO
import hashlib

def detect_ai_image(image):
    if image is None:
        return "<h3 style='color:red'>Please upload an image!</h3>"

    try:
        # Get image properties
        width, height = image.size

        # Initialize scores
        ai_score = 0.0
        google_downloaded = False
        confidence_factors = []
        red_flags = []

        # ============================================
        # CHECK 1: CHATGPT/DALL-E SIGNATURE DETECTION
        # ============================================

        dalle3_sizes = [
            (1024, 1024), (1792, 1024), (1024, 1792),
            (1536, 1024), (1024, 1536),
        ]

        if (width, height) in dalle3_sizes or (height, width) in dalle3_sizes:
            ai_score += 0.40
            red_flags.append("&#128680; DALL-E 3 (ChatGPT) signature resolution")
            confidence_factors.append("ChatGPT image detected")

        # Gemini sizes
        gemini_sizes = [
            (1536, 1536), (2048, 2048),
            (1280, 1280), (1440, 1440),
        ]

        if (width, height) in gemini_sizes:
            ai_score += 0.40
            red_flags.append("&#128680; Gemini AI signature resolution")
            confidence_factors.append("Gemini image detected")

        # ============================================
        # CHECK 2: GOOGLE DOWNLOADED IMAGE DETECTION (NEW!)
        # ============================================

        # Common Google Images download sizes
        google_sizes = [
            # Thumbnail sizes
            (150, 150), (200, 200), (300, 300), (400, 400),
            # Common web sizes
            (640, 480), (800, 600), (1024, 768), (1280, 720),
            (1920, 1080), (1600, 1200),
            # Portrait
            (480, 640), (600, 800), (768, 1024), (720, 1280),
            # Google optimized
            (1200, 800), (800, 1200), (1000, 667), (667, 1000),
        ]

        # Check for exact Google-optimized sizes
        if (width, height) in google_sizes or (height, width) in google_sizes:
            ai_score += 0.25
            google_downloaded = True
            red_flags.append("&#9888; Common Google Images download size detected")
            confidence_factors.append("Likely downloaded from web")

        # Check for typical web aspect ratios
        aspect_ratio = width / height
        web_ratios = [
            (16/9, "16:9 - Web standard"),
            (4/3, "4:3 - Old web standard"),
            (3/2, "3:2 - Web photos"),
        ]

        for ratio_value, ratio_name in web_ratios:
            if abs(aspect_ratio - ratio_value) < 0.01:  # Very precise
                # If it matches web ratio AND has web-size dimensions
                if width in [640, 800, 1024, 1280, 1920] or height in [480, 600, 768, 720, 1080]:
                    ai_score += 0.15
                    red_flags.append(f"&#9888; Web-standard size: {width}x{height} ({ratio_name})")
                    google_downloaded = True

        # ============================================
        # CHECK 3: EXIF METADATA DEEP ANALYSIS
        # ============================================

        exif_data = {}
        exif_suspicious = False
        has_real_camera = False

        try:
            exif = image.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value

                # Check for AI signatures
                software = str(exif_data.get('Software', '')).lower()
                make = str(exif_data.get('Make', '')).lower()
                model = str(exif_data.get('Model', '')).lower()

                ai_keywords = ['dalle', 'chatgpt', 'openai', 'gemini', 'google ai',
                              'midjourney', 'stable diffusion', 'artificial', 'generated',
                              'synthesized', 'ai', 'neural']

                if any(keyword in software for keyword in ai_keywords):
                    ai_score += 0.50
                    red_flags.append(f"&#128680; AI software in EXIF: {software}")
                    exif_suspicious = True

                # Check for browser/download software (Google downloads)
                browser_keywords = ['chrome', 'firefox', 'safari', 'edge', 'browser',
                                   'paint', 'photoshop', 'gimp', 'preview', 'irfanview']

                if any(keyword in software for keyword in browser_keywords):
                    ai_score += 0.20
                    google_downloaded = True
                    red_flags.append(f"&#9888; Edited/Downloaded via: {software}")

                # Real camera indicators
                real_camera_tags = ['Make', 'Model', 'Flash', 'FocalLength', 'ExposureTime',
                                   'ISOSpeedRatings', 'FNumber', 'LensModel']
                real_tags_found = sum(1 for tag in real_camera_tags if tag in exif_data)

                if real_tags_found >= 5:
                    has_real_camera = True
                    ai_score -= 0.30
                    confidence_factors.append(f"Found {real_tags_found} camera EXIF tags")

                # Check for incomplete EXIF (downloaded images)
                if software and not make and not model:
                    ai_score += 0.15
                    google_downloaded = True
                    red_flags.append("&#9888; Has software tag but no camera info (likely downloaded)")

        except:
            pass

        # NO EXIF = Major red flag (Google strips EXIF)
        if not exif_data:
            ai_score += 0.25
            google_downloaded = True
            red_flags.append("&#128680; NO EXIF metadata (Google/browsers strip this)")

        # ============================================
        # CHECK 4: FILE COMPRESSION ANALYSIS (NEW!)
        # ============================================

        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format=image.format or 'PNG')
        file_size = len(img_byte_arr.getvalue())
        pixels = width * height
        bytes_per_pixel = file_size / pixels

        # Google heavily compresses images
        if bytes_per_pixel < 0.3:  # Very compressed
            ai_score += 0.15
            google_downloaded = True
            red_flags.append(f"&#9888; Heavy compression ({bytes_per_pixel:.2f} bytes/pixel - typical of web images)")

        # Real phone photos are larger
        if bytes_per_pixel > 2.5 and has_real_camera:
            ai_score -= 0.15
            confidence_factors.append("Large file size indicates original photo")

        # ============================================
        # CHECK 5: SCREENSHOT DETECTION (NEW!)
        # ============================================

        # Common screenshot sizes
        screenshot_sizes = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),  # PC
            (2560, 1440), (3840, 2160),  # High-res PC
            (1125, 2436), (1170, 2532), (1284, 2778),  # iPhone
            (1080, 2340), (1440, 3040), (1440, 2960),  # Android
        ]

        if (width, height) in screenshot_sizes or (height, width) in screenshot_sizes:
            ai_score += 0.30
            google_downloaded = True
            red_flags.append(f"&#128680; Screenshot size detected: {width}x{height}")
            confidence_factors.append("This is likely a screenshot, not original photo")

        # ============================================
        # CHECK 6: WATERMARK/LOGO DETECTION (NEW!)
        # ============================================

        img_array = np.array(image.convert('RGB'))

        # Check corners for watermarks (stock photos/Google images often have these)
        corner_size = 80
        if width > corner_size * 2 and height > corner_size * 2:
            corners = {
                'top-right': img_array[:corner_size, -corner_size:],
                'bottom-right': img_array[-corner_size:, -corner_size:],
                'bottom-left': img_array[-corner_size:, :corner_size],
            }

            watermark_detected = False
            for corner_name, corner in corners.items():
                # Check for text-like patterns (watermarks)
                corner_gray = np.mean(corner, axis=2)
                variance = np.var(corner_gray)

                # Watermarks have specific variance patterns
                if 100 < variance < 1000:
                    # Check for text-like edge patterns
                    edges = np.abs(np.diff(corner_gray, axis=0))
                    if np.mean(edges) > 5:
                        watermark_detected = True
                        ai_score += 0.15
                        red_flags.append(f"⚠️ Possible watermark in {corner_name} corner")
                        google_downloaded = True
                        break

        # ============================================
        # CHECK 7: PERFECT SQUARE = AI RED FLAG
        # ============================================

        if width == height:
            ai_score += 0.25
            red_flags.append("⚠️ Perfect square (1:1) - common in AI/web images")

            if width in [512, 768, 1024, 1536, 2048]:
                ai_score += 0.15
                red_flags.append(f"🚨 AI-standard size: {width}x{width}px")

        # ============================================
        # CHECK 8: COLOR HISTOGRAM ANALYSIS
        # ============================================

        color_suspicious = 0

        for channel_idx in range(3):  # R, G, B
            channel_data = img_array[:, :, channel_idx].flatten()
            hist, _ = np.histogram(channel_data, bins=256, range=(0, 256))

            max_bin = np.max(hist)
            median_bin = np.median(hist[hist > 0])

            if max_bin > median_bin * 15:
                color_suspicious += 1

        if color_suspicious >= 2:
            ai_score += 0.20
            red_flags.append("🚨 Unnatural color distribution (AI characteristic)")

        # ============================================
        # CHECK 9: EDGE SMOOTHNESS (AI = TOO PERFECT)
        # ============================================

        if img_array.shape[0] > 200 and img_array.shape[1] > 200:
            h_center = img_array.shape[0] // 2
            w_center = img_array.shape[1] // 2
            sample = img_array[h_center-100:h_center+100, w_center-100:w_center+100]

            gray = np.mean(sample, axis=2)
            edges_x = np.diff(gray, axis=1)
            edges_y = np.diff(gray, axis=0)
            edge_variance = np.var(edges_x) + np.var(edges_y)

            if edge_variance < 50:
                ai_score += 0.20
                red_flags.append("🚨 Too smooth (AI/heavily edited)")
            elif edge_variance > 200:
                ai_score -= 0.10
                confidence_factors.append("Natural edge roughness")

        # ============================================
        # CHECK 10: NOISE PATTERN ANALYSIS
        # ============================================

        dark_pixels = img_array[img_array < 30]

        if len(dark_pixels) > 1000:
            dark_variance = np.var(dark_pixels)

            if dark_variance < 5:
                ai_score += 0.15
                red_flags.append("🚨 Too clean shadows (no camera noise)")
            elif dark_variance > 50:
                ai_score -= 0.10
                confidence_factors.append("Natural camera noise detected")

        # ============================================
        # CHECK 11: WEB OPTIMIZATION PATTERNS (NEW!)
        # ============================================

        # Google/web images are often optimized to specific file sizes
        common_web_file_sizes = [
            (50000, 60000),    # ~50KB
            (90000, 110000),   # ~100KB
            (190000, 210000),  # ~200KB
            (490000, 510000),  # ~500KB
        ]

        for min_size, max_size in common_web_file_sizes:
            if min_size <= file_size <= max_size:
                ai_score += 0.10
                google_downloaded = True
                red_flags.append(f"⚠️ Web-optimized file size ({file_size:,} bytes)")
                break

        # ============================================
        # FINAL SCORE CALCULATION
        # ============================================

        # Clamp score
        ai_score = max(0.0, min(1.0, ai_score))
        real_score = 1.0 - ai_score

        # Determine verdict
        if ai_score >= 0.70:
            verdict = "🚨 HIGHLY LIKELY FAKE"
            if google_downloaded:
                verdict += " (AI or Downloaded from Web)"
            color = "#dc3545"
            recommendation = "⛔ REJECT REFUND — Strong evidence of fraud"
            risk = "HIGH RISK"
            action = "DENY"
        elif ai_score >= 0.50:
            verdict = "⚠️ SUSPICIOUS"
            if google_downloaded:
                verdict += " (Likely Downloaded Image)"
            color = "#ff9800"
            recommendation = "🔍 MANUAL REVIEW REQUIRED — Multiple red flags"
            risk = "MEDIUM-HIGH RISK"
            action = "REVIEW"
        elif ai_score >= 0.30:
            verdict = "❓ UNCERTAIN"
            color = "#ffc107"
            recommendation = "⚡ Quick verification recommended"
            risk = "MEDIUM RISK"
            action = "CHECK"
        else:
            verdict = "✅ LIKELY REAL PHOTO"
            color = "#28a745"
            recommendation = "✓ Appears authentic - Safe to process"
            risk = "LOW RISK"
            action = "APPROVE"

        # Add Google download warning
        if google_downloaded and ai_score >= 0.40:
            red_flags.insert(0, "🔴 HIGH PROBABILITY: Image downloaded from Google/web, not original photo")

        # Build HTML sections with improved design
        red_flags_html = ""
        if red_flags:
            red_flags_html = f"""
            <div style="background: linear-gradient(135deg, #ffeaa7, #fab1a0); border: 2px solid #e17055; padding: 20px; margin: 20px 0; border-radius: 15px; box-shadow: 0 8px 25px rgba(231, 112, 85, 0.3);">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 24px; margin-right: 10px;">&#128681;</span>
                    <strong style="color: #d63031; font-size: 18px; font-weight: 600;">Red Flags Detected ({len(red_flags)})</strong>
                </div>
                <div style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px;">
            """
            for flag in red_flags[:10]:
                red_flags_html += f"<div style='color: #2d3436; font-size: 14px; margin: 8px 0; padding: 5px 0; border-bottom: 1px solid rgba(45, 52, 54, 0.1);'>{flag}</div>"
            red_flags_html += "</div></div>"

        confidence_html = ""
        if confidence_factors:
            confidence_html = f"""
            <div style="background: linear-gradient(135deg, #55efc4, #00b894); border: 2px solid #00b894; padding: 20px; margin: 20px 0; border-radius: 15px; box-shadow: 0 8px 25px rgba(0, 184, 148, 0.3);">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 24px; margin-right: 10px;">&#9989;</span>
                    <strong style="color: #00b894; font-size: 18px; font-weight: 600;">Authenticity Indicators ({len(confidence_factors)})</strong>
                </div>
                <div style="background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px;">
            """
            for factor in confidence_factors[:5]:
                confidence_html += f"<div style='color: #2d3436; font-size: 14px; margin: 8px 0; padding: 5px 0; border-bottom: 1px solid rgba(45, 52, 54, 0.1);'>{factor}</div>"
            confidence_html += "</div></div>"

        # Determine source type
        if google_downloaded and ai_score < 0.50:
            source_type = "📥 Downloaded from Web/Google"
        elif ai_score >= 0.70:
            source_type = "🤖 AI Generated"
        elif has_real_camera:
            source_type = "📸 Camera Photo"
        else:
            source_type = "❓ Unknown Source"

        technical_details = f"""
        <div style="background: linear-gradient(135deg, #a29bfe, #6c5ce7); padding: 25px; border-radius: 15px; margin-top: 20px; color: white; box-shadow: 0 8px 25px rgba(108, 92, 231, 0.3);">
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <span style="font-size: 24px; margin-right: 10px;">&#128300;</span>
                <strong style="font-size: 20px; font-weight: 600;">Technical Analysis</strong>
            </div>
            <div style="background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 12px; color: #2d3436;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; font-family: 'Courier New', monospace; font-size: 14px;">
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>📐 Resolution:</strong> {width}x{height}px
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>📊 Aspect Ratio:</strong> {aspect_ratio:.3f}:1
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>💾 File Size:</strong> {file_size:,} bytes ({bytes_per_pixel:.2f} bytes/pixel)
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>🎨 Format:</strong> {image.format or 'Unknown'}
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>📋 EXIF Tags:</strong> {len(exif_data)}
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #6c5ce7;">
                        <strong>🔍 Source Type:</strong> {source_type}
                    </div>
                </div>
        """

        if exif_data and len(exif_data) > 0:
            technical_details += f"""
                <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #e9ecef;">
                    <strong style="font-size: 16px; color: #6c5ce7; margin-bottom: 10px; display: block;">📷 Metadata Info:</strong>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-size: 13px;">
            """
            important_tags = ['Make', 'Model', 'Software', 'DateTime']
            for tag in important_tags:
                if tag in exif_data:
                    value = str(exif_data[tag])[:50]
                    technical_details += f"<div style='margin: 5px 0;'><strong>{tag}:</strong> {value}</div>"
            technical_details += "</div></div>"

        technical_details += "</div></div>"

        result_html = f"""
        <!-- Header Section -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);">
            <h1 style="margin: 0; font-size: 2.5em; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">&#128269; Advanced Fraud Detection</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9; font-weight: 300;">11-Factor Analysis + Google Download Detection</p>
        </div>

        <!-- Main Result Card -->
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2px; border-radius: 20px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);">
            <div style="background: white; border-radius: 18px; padding: 30px;">
                <h1 style="text-align: center; color: {color}; font-size: 3em; margin: 0; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">{verdict}</h1>

                <!-- Score Cards Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);">
                        <h3 style="margin: 0 0 10px 0; color: #e84393; font-size: 0.9em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">FRAUD SCORE</h3>
                        <div style="font-size: 3em; font-weight: 700; color: #dc3545; margin: 0;">{ai_score*100:.0f}%</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(168, 237, 234, 0.3);">
                        <h3 style="margin: 0 0 10px 0; color: #00b894; font-size: 0.9em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">AUTHENTIC SCORE</h3>
                        <div style="font-size: 3em; font-weight: 700; color: #28a745; margin: 0;">{real_score*100:.0f}%</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(255, 236, 210, 0.3);">
                        <h3 style="margin: 0 0 10px 0; color: {color}; font-size: 0.9em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">ACTION</h3>
                        <div style="font-size: 2.5em; font-weight: 700; color: {color}; margin: 0;">{action}</div>
                    </div>
                </div>

                <!-- Recommendation Card -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                    <h3 style="margin: 0 0 10px 0; color: white; font-size: 1.5em; font-weight: 600;">&#128203; {recommendation}</h3>
                    <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 1.1em; font-weight: 300;">Risk Level: <strong>{risk}</strong></p>
                </div>

                {red_flags_html}
                {confidence_html}
                {technical_details}
            </div>
        </div>
        """

        return result_html

    except Exception as e:
        return f"""
        <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);'>
            <h2 style="color: #e84393; margin: 0 0 15px 0;">&#9888; Analysis Error</h2>
            <p style="color: #2d3436; margin: 0; font-size: 1.1em;">{str(e)}</p>
        </div>
        """

demo = gr.Interface(
    fn=detect_ai_image,
    inputs=gr.Image(type="pil", label="&#128248; Upload Product / Receipt Image"),
    outputs=gr.HTML(label="Detection Result"),
    title="&#128737; Ultimate Fraud Detector v3.0",
    description="AI-powered image fraud detection system",
    theme=Soft(),
    article="Test article"
)

if __name__ == "__main__":
    demo.launch(share=True)