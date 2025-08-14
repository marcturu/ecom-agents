# 🛒 ECSDI-Project — E-commerce Multi-Agent Platform

<sub>🗓️ Developed in April 2024</sub>

This project implements a **platform of services and agents** capable of managing all processes of a global e-commerce company (such as Amazon).  
The platform integrates **external agents** to handle all required elements, including **clients**, **third-party sellers**, **transportation services**, and **payment services**.

---

## ✅ Features

- **Multi-agent system** for distributed e-commerce management with **Flask**, **Jinja2** and **RDFLib**.
- Centralized ontology shared across all agents for product data, orders, and communications.  
- Integration of **external agents** for logistics, payments, and sellers.
- **RESTful routes** for interacting with the platform.
- Basic workflow:
  1. Product search based on user constraints.
  2. Order creation and processing.
  3. Shipment from the nearest logistics center.
  4. Invoices, recomnedations and reviews.

---

## 🛠 Installation & Setup

### 0. Prerequisites

Make sure you have installed:

- **Python 3.9+**
- **pip** (Python package manager)

You can check your versions with:

```cmd
python --version
pip --version
```

### 1. Clone the repository

Open **CMD** and run:

```cmd
git clone https://github.com/marcturu/ECSDI-Project.git
cd ECSDI-Project
```

### 2. Create a virtual environment

```cmd
python -m venv .venv
```

### 3. Activate the environment

```cmd
.\.venv\Scripts\activate
```

> Make sure you are using **CMD or PowerShell** on Windows.\
> You should see `(.venv)` at the start of the command line.

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Run the platform

From the **project root** in CMD:

```cmd
.\run.bat
```

What this script does:

- Starts the **Directory Service** in a new CMD window.
- Starts all **Agents** in separate CMD windows with their assigned ports.
- Starts the **Client** in its own window.
- Each agent’s terminal shows logs of its execution.

> ⚠️ Make sure to keep the root CMD window open so the virtual environment stays active.

### 6. Test the platform

- Access the services in your browser or via HTTP requests:
  - Directory Service: `http://localhost:5000`
  - Agent 1: `http://localhost:5001`
  - Agent 2: `http://localhost:5002`
  - ...and so on, following the ports specified in the `run.bat`.
- It is recommended to start with the **Client route** to register a new user.

### 7. Notes

- If you do **not use CMD / PowerShell**, you can run the agents individually using:

```cmd
python -m app.agents.dir
python -m app.agents.agent1
python -m app.agents.agent2
```

PowerShell can show script limitations. To solve them, use:  
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```
---

## 📂 Files

All additional project details are available in the `/docs` folder:
- **System Specification**
- **Architectural Design**
- **Detailed Design**
- **Ontology**
- **Extras**

The original repository is hosted at:  
[https://github.com/ECSDI/ECSDI_LAB](https://github.com/ECSDI/ECSDI_LAB)

---

## 📷 Screenshots  

---

## ⚖️ Copyright

© 2024 Marc Turu Roca and collaborators. All rights reserved.  
This project is the joint intellectual property of its authors.  
No part may be copied, modified, distributed, or used without prior written permission from all authors.  

- Miquel García    
- Marc Turu
- Sergi Campuzano

