# Interactive Generative Studio

Interactive Generative Studio is a web-based creative platform developed as a university term project using **Python** and **Flask**. The application combines generative art, artistic data visualization, image processing, and an interactive gallery within a modern responsive interface.

---

## Team

- Moussa El Moussaoui
- Mouad Agzennai Bakhouch
- Mohammed Lachhab
- Aimad Eddine Slimani

---

## Features

- 🎨 Procedural generative art with multiple interactive generators
- 📊 Artistic data visualizations built from CSV datasets
- 🖼️ Image processing with creative filters and transformations
- 🎨 Dominant color extraction using K-Means clustering
- 🖼️ Automatic gallery for generated artworks
- 🌐 Responsive Flask web application with a modern user interface

---

## Technologies

### Backend

- Python 3.12
- Flask
- Jinja2
- Flask-WTF

### Data Processing

- Pandas
- NumPy
- Matplotlib
- Scikit-learn

### Image Processing

- Pillow
- OpenCV

### Frontend

- HTML5
- CSS3
- JavaScript
- Canvas API

---

## Project Structure

```text
interactive-generative-studio/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── datasets/
├── modules/
├── static/
└── templates/
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/moussa7elmoussaoui/interactive-generative-studio.git
```

Move into the project directory:

```bash
cd interactive-generative-studio
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## Project Modules

- **Generative Art** – Random Geometry, Particle System, and Recursive Fractal Tree.
- **Data Visualization** – Creative visualizations generated from CSV datasets.
- **Image Studio** – Image upload, creative filters, transformations, and color extraction.
- **Gallery** – Browse, download, and manage generated artworks.

---

## Project Requirements Covered

- Flask Web Application
- Object-Oriented Programming
- Generative Art
- Data Processing with Pandas
- Artistic Data Visualization
- Image Processing
- Interactive User Interface
- Responsive Design
- Gallery System

---

Developed as part of the **Digital Creativity using Python** course.