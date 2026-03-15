# 🛡️ Ultimate Fraud Detector v3.0

A powerful AI-powered web application that detects fraudulent images used in e-commerce scams, fake refunds, and product verification fraud. Built specifically for companies like Zepto, Blinkit, Swiggy, Amazon, and Flipkart to combat image-based fraud.

![Fraud Detection](https://img.shields.io/badge/Fraud--Detection-AI--Powered-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Gradio](https://img.shields.io/badge/Gradio-Web--App-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 What This Detects

**AI-Generated Images:**
- ChatGPT (DALL-E 3) - Signature resolutions like 1024×1024, 1792×1024
- Google Gemini - 1536×1536, 2048×2048 resolutions
- Midjourney, Stable Diffusion, and other AI tools

**Web-Downloaded Images:**
- Google Images downloads with stripped EXIF metadata
- Browser-saved images with compression artifacts
- Stock photos with watermarks and web optimization

**Other Fraud Types:**
- Screenshots from devices (PC, iPhone, Android)
- Heavily edited or manipulated images
- Images without authentic camera metadata

## 🚀 Features

### 🔬 11-Layer Detection System
1. **AI Signature Resolution Detection** - Identifies known AI model output sizes
2. **Deep EXIF Metadata Analysis** - Checks for camera authenticity and AI software signatures
3. **Google Download Size Patterns** - Detects web-optimized image dimensions
4. **File Compression Analysis** - Analyzes compression artifacts from web downloads
5. **Screenshot Detection** - Identifies common screen capture resolutions
6. **Watermark/Logo Detection** - Scans corners for stock photo watermarks
7. **Perfect Square Analysis** - Flags 1:1 aspect ratios common in AI/web images
8. **Color Histogram Forensics** - Detects unnatural color distributions
9. **Edge Smoothness Analysis** - Identifies overly perfect or artificial edges
10. **Noise Pattern Detection** - Checks for authentic camera sensor noise
11. **Web Optimization Patterns** - Detects files optimized for web delivery

### 📊 Risk Assessment
- **Fraud Score**: 0-100% probability of being fake
- **Authenticity Score**: Confidence in image being real
- **Actionable Recommendations**: APPROVE/REVIEW/DENY decisions
- **Detailed Red Flags**: Specific reasons for suspicion
- **Technical Analysis**: Complete forensic breakdown

### 🎨 User Interface
- Clean, professional web interface
- Drag-and-drop image upload
- Real-time analysis with progress indicators
- Comprehensive results with visual indicators
- Mobile-responsive design

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/frauddetector.git
   cd frauddetector
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r frauddetector/requirements.txt
   ```

4. **Run the application:**
   ```bash
   cd frauddetector
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://127.0.0.1:7860`

## 📖 Usage

### Basic Usage
1. Open the web application in your browser
2. Click "📸 Upload Product / Receipt Image"
3. Select or drag-and-drop an image file
4. Wait for analysis (takes 2-5 seconds)
5. Review the detailed fraud assessment

### Understanding Results

#### Risk Levels:
- **✅ LIKELY REAL PHOTO** (Fraud Score < 30%): Safe to approve
- **❓ UNCERTAIN** (30-50%): Manual verification recommended
- **⚠️ SUSPICIOUS** (50-70%): Requires manual review
- **🚨 HIGHLY LIKELY FAKE** (70%+): Strong evidence of fraud - reject

#### Key Indicators:
- **Red Flags**: Specific suspicious patterns detected
- **Authenticity Indicators**: Evidence supporting genuine origin
- **Technical Details**: Forensic analysis breakdown

## 🔍 How It Works

### Detection Methodology

The system employs multiple forensic techniques to distinguish between authentic camera photos and fraudulent images:

#### 1. Resolution Pattern Analysis
AI models produce images in specific resolutions:
- DALL-E 3: 1024×1024, 1792×1024, 1024×1792
- Gemini: 1536×1536, 2048×2048
- Common web downloads: 640×480, 800×600, 1920×1080

#### 2. EXIF Metadata Examination
Authentic photos contain:
- Camera make/model information
- Shooting parameters (ISO, aperture, focal length)
- GPS/location data (if enabled)
- Date/time stamps

AI and downloaded images often have:
- Missing or incomplete EXIF data
- Browser software signatures
- AI tool identifiers in metadata

#### 3. Compression Artifact Analysis
- Web images: Heavy JPEG compression (< 0.3 bytes/pixel)
- Camera photos: Higher quality, less compressed
- AI images: Artificial compression patterns

#### 4. Statistical Analysis
- **Color histograms**: AI images show unnatural color distributions
- **Edge detection**: AI images are often too smooth or too sharp
- **Noise patterns**: Real cameras have characteristic sensor noise

#### 5. Content-Based Detection
- Watermark scanning in image corners
- Screenshot detection via common resolutions
- Aspect ratio analysis (AI often uses perfect squares)

## 📋 Requirements

```
gradio>=4.0.0
pillow>=9.0.0
numpy>=1.21.0
torch>=1.12.0
transformers>=4.21.0
```

## 🖼️ Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Analysis Results
![Analysis Results](screenshots/analysis-results.png)

### Fraud Detection Example
![Fraud Detection](screenshots/fraud-detection.png)

## 🎯 Use Cases

### E-commerce Fraud Prevention
- **Refund Fraud**: Prevent fake product images in refund claims
- **Product Verification**: Authenticate user-submitted product photos
- **Receipt Validation**: Verify receipt authenticity for reimbursements

### Insurance Claims
- **Damage Photos**: Detect manipulated accident/damage images
- **Medical Bills**: Authenticate submitted documentation

### Social Media Moderation
- **Fake Profile Detection**: Identify AI-generated profile pictures
- **Content Moderation**: Flag suspicious user-generated content

### Digital Forensics
- **Image Authentication**: Verify photo authenticity in investigations
- **Copyright Protection**: Detect unauthorized image modifications

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gradio](https://gradio.app/) for the web interface
- Uses [Pillow](https://python-pillow.org/) for image processing
- Inspired by real-world fraud prevention needs in e-commerce

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Email: support@frauddetector.com
- Documentation: [Wiki](https://github.com/yourusernamepiyuxh.98/frauddetector/wiki)

---

**⚠️ Disclaimer**: This tool provides probabilistic analysis and should be used as part of a comprehensive fraud prevention strategy. Always combine automated detection with human review for critical decisions.

**🚀 Ready to combat image fraud?** Start protecting your business today!
