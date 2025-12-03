# Hevy Analyzer 🏋️‍♂️

A powerful workout data analysis tool for [Hevy](https://hevy.com/) users. Visualize your training progress with interactive charts, muscle heatmaps, and detailed statistics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 📊 **Interactive Charts** - Visualize workouts, sets, volume, and duration over time
- 🔥 **Muscle Heatmap** - See which muscle groups you're training with an anatomical SVG visualization
- 📈 **Progress Tracking** - Track your strength gains and personal records
- 🎯 **Exercise Analysis** - Detailed breakdown by exercise, muscle group, and equipment
- ⚙️ **Customizable** - Add custom exercises and configure calculation methods
- 🌐 **API Integration** - Connect directly to Hevy API or import CSV exports

## 🚀 Quick Start

### Option 1: Run from Source

1. Clone the repository:
```bash
git clone https://github.com/NOirBRight/hevy-analyzer.git
cd hevy-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

### Option 2: Windows Executable

Download the latest release from the [Releases](https://github.com/NOirBRight/hevy-analyzer/releases) page and run `HevyAnalyzer.exe`.

## 📦 Requirements

- Python 3.8+
- See `requirements.txt` for full dependencies

## 🔧 Configuration

### Data Sources

1. **Hevy API** - Enter your Hevy API key in Settings to sync directly
2. **CSV Import** - Export your data from Hevy app and upload the CSV file

### Custom Exercises

Add your own exercises with muscle group mappings in the Settings page.

## 📸 Screenshots

### Dashboard
Interactive charts showing your workout trends over time.

### Muscle Heatmap
Anatomical visualization showing muscle activation frequency.

### Exercise Analysis
Detailed breakdown of each exercise with volume and progression.

## 🛠️ Building from Source

To create a Windows executable:

```bash
pip install pyinstaller
pyinstaller HevyAnalyzer.spec --noconfirm
```

The executable will be in `dist/HevyAnalyzer/`.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For issues and feature requests, please use the [GitHub Issues](https://github.com/NOirBRight/hevy-analyzer/issues) page.

---

Made with ❤️ for the fitness community
