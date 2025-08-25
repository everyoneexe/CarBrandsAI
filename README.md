# 🚗 CarBrandsAI

**Advanced AI-Powered Car Brand Detection System**

A sophisticated web application that uses YOLOv11 deep learning model to detect and identify car brands from images with high accuracy. Features a modern cyberpunk-themed interface and real-time AI processing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-87.4%25%20mAP50-green.svg)](https://github.com/ultralytics/ultralytics)

## ✨ Features

- **🤖 Advanced AI Model**: YOLOv11 Medium architecture with 87.4% mAP50 accuracy
- **🎯 18 Car Brands**: Supports major automotive brands including BMW, Mercedes, Toyota, Tesla, and more
- **⚡ Real-time Detection**: Lightning-fast inference (~100ms processing time)
- **🎨 Modern Interface**: Cyberpunk-themed responsive web design
- **📱 Cross-Platform**: Works on desktop, tablet, and mobile devices
- **🖼️ Advanced Features**: Drag & drop upload, bounding box visualization, full-screen viewer
- **🔧 RESTful API**: Complete backend API for integration with other applications

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser
- 4GB+ RAM recommended

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/everyoneexe/CarBrandsAI.git
   cd CarBrandsAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   ./start.sh
   ```

4. **Open in browser**
   - Web Interface: http://localhost:8080
   - API Endpoint: http://localhost:5000

## 📊 Supported Car Brands

| Luxury | Japanese | Korean | American | European | Chinese |
|--------|----------|--------|----------|----------|---------|
| Audi | Toyota | Hyundai | Ford | Volkswagen | BYD |
| BMW | Honda | KIA | Chevrolet | Mercedes-Benz | |
| Lexus | Nissan | | Tesla | | |
| Mercedes-Benz | Mazda | | | | |
| | Mitsubishi | | | | |

**Total: 18 Brands** with continuous expansion planned.

## 🔧 Usage Guide

### Web Interface

1. **Upload Image**: Drag & drop or click to select a car image
2. **Analyze**: Click "Markayı Bul" button to start AI detection
3. **View Results**: See detected brand, confidence score, and bounding box
4. **Full Screen**: Use "Tam Ekran Görüntüle" for detailed view
5. **Save Results**: Download annotated image or copy JSON data

### API Integration

#### Detection Endpoint
```http
POST /api/detect
Content-Type: multipart/form-data

{
  "image": <file>
}
```

**Response:**
```json
{
  "brand": "BMW",
  "confidence": 0.92,
  "latency": "0.15s",
  "box": {
    "x": 120,
    "y": 80,
    "w": 160,
    "h": 160
  },
  "model_info": {
    "name": "CarBrandsAI YOLOv11m",
    "version": "V5",
    "accuracy": "87.4% mAP50"
  }
}
```

#### Other Endpoints

- `GET /` - Health check
- `GET /api/brands` - List supported brands
- `GET /api/model-info` - Model specifications

## 🏗️ Architecture

### Frontend
- **Framework**: Vanilla JavaScript (ES6+)
- **Styling**: Advanced CSS3 with animations
- **Features**: Canvas API for visualization, Fetch API for backend communication
- **Theme**: Cyberpunk-inspired design with particle effects

### Backend
- **Framework**: Flask (Python)
- **AI Model**: YOLOv11 Medium (Ultralytics)
- **Computer Vision**: OpenCV for image processing
- **APIs**: RESTful design with CORS support

### AI Model Specifications
- **Architecture**: YOLOv11 Medium
- **Training Dataset**: 12,000+ labeled car images
- **Accuracy**: 87.4% mAP50
- **Input Resolution**: 640x640 pixels
- **Training Epochs**: 35 epochs with optimized hyperparameters
- **Inference Time**: ~100ms (CPU), ~50ms (GPU)

## 📁 Project Structure

```
CarBrandsAI/
├── 🌐 Frontend
│   ├── index.html          # Main web interface
│   └── app.js              # JavaScript application logic
├── 🤖 Backend
│   ├── backend.py          # Flask API server
│   ├── requirements.txt    # Python dependencies
│   └── start.sh            # Quick start script
├── 🧠 AI Model
│   └── model/
│       └── best.pt         # Trained YOLOv11 model
└── 📚 Documentation
    ├── README.md           # This file
    └── START.md            # Quick start guide
```

## 🔬 Technical Details

### Performance Metrics
- **mAP50**: 87.4% (Mean Average Precision at IoU 0.5)
- **Precision**: 89%
- **Recall**: 85%
- **Model Size**: ~45MB
- **Memory Usage**: ~2GB RAM during inference

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- Maximum file size: 16MB

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🛠️ Development

### Setup Development Environment

1. **Clone and enter directory**
   ```bash
   git clone https://github.com/everyoneexe/CarBrandsAI.git
   cd CarBrandsAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run backend only**
   ```bash
   python3 backend.py
   ```

4. **Run frontend only**
   ```bash
   python3 -m http.server 8080
   ```

### API Testing

```bash
# Test health endpoint
curl http://localhost:5000/

# Test brand detection
curl -X POST -F "image=@test_car.jpg" http://localhost:5000/api/detect

# Get supported brands
curl http://localhost:5000/api/brands
```

## 🐛 Troubleshooting

### Common Issues

**Backend fails to start**
```bash
# Check if model file exists
ls -la model/best.pt

# Verify Python dependencies
pip install -r requirements.txt --force-reinstall
```

**Port already in use**
```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>
```

**Model loading errors**
- Ensure `model/best.pt` exists and is not corrupted
- Check available memory (requires 2GB+ RAM)
- Verify PyTorch installation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ultralytics** for the YOLOv11 framework
- **OpenCV** for computer vision utilities
- **Flask** for the lightweight web framework
- **Car manufacturers** for inspiring this project

## 📈 Future Roadmap

- [ ] **Mobile App**: React Native application
- [ ] **Video Processing**: Real-time video analysis
- [ ] **More Brands**: Expand to 50+ car brands
- [ ] **Cloud Deployment**: AWS/Azure integration
- [ ] **API Authentication**: Secure API access
- [ ] **Batch Processing**: Multiple image analysis

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/everyoneexe/CarBrandsAI/issues)
- **Discussions**: [Community discussions](https://github.com/everyoneexe/CarBrandsAI/discussions)

---

**Made with ❤️ and AI by [everyoneexe](https://github.com/everyoneexe)**

*"Advancing automotive AI, one detection at a time."*