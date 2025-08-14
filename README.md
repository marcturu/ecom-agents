# 🛒 ECSDI-Project — E-commerce Multi-Agent Platform

<sub>🗓️ Developed in April 2024</sub>

This project implements a **platform of services and agents** capable of managing all processes of a global e-commerce company (such as Amazon).  
The platform integrates **external agents** to handle all required elements, including **clients**, **third-party sellers**, **transportation services**, and **payment services**.

---

## ✅ Features

- **Multi-agent system** for distributed e-commerce management.
- Integration of **external agents** for logistics, payments, and sellers.
- **RESTful routes** for interacting with the platform.
- Complete documentation in `/docs` including:
  - System Specification
  - Architectural Design
  - Detailed Design
  - Ontology
  - Additional resources

---

## 🛠 Installation & Setup

### 0. Prerequisites
Make sure you have installed:
- **Python 3.9+**
- **pip** (Python package manager)

You can check your versions with:
```bash
python --version
pip --version
```

### 1. Clone the repository
```bash
git clone https://github.com/marcturu/ECSDI-Project.git
cd ECSDI-Project
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install Flask
```

### 4. Activate the environment
```bash
# Windows (CMD / PowerShell)
.\.venv\Scripts\activate
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate
```

### 5. Run the platform
a) **Windows (CMD / PowerShell)** from the project root:
```bash
.\run.bat
```
The script will:
- Start the **Directory Service** in a new window.
- Start **Agent 1** in a new window.
- Start **Agent 2** in a new window.

b) **Windows (Git Bash) / macOS / Linux** from the project root:
```bash
python -m app.agents.dir &
python -m app.agents.agent1 &
python -m app.agents.agent2 &
wait
```
This will run all services in the same terminal (useful when `run.bat` is not supported).

### 6. Try it out
Test the different functionalities by visiting each route via the browser or HTTP client.  
It is recommended to start with the **client route** to register a new user.

---

## 📂 Documentation

All additional project details are available in the `/docs` folder:
- **System Specification**
- **Architectural Design**
- **Detailed Design**
- **Ontology**
- **Extras**

The original repository is hosted at:  
[https://github.com/ECSDI/ECSDI_LAB](https://github.com/ECSDI/ECSDI_LAB)

---

## ⚖️ Copyright

© 2024 Marc Turu Roca and collaborators. All rights reserved.  
This project is the joint intellectual property of its authors.  
No part may be copied, modified, distributed, or used without prior written permission from all authors.  

- Miquel García    
- Marc Turu
- Sergi Campuzano

