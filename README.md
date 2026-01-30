# 🛒 ECSDI-Project — Ecom Agents

<sub>🗓️ Developed in April 2024</sub>

This project implements a **platform of services and agents** capable of managing all processes of a global e-commerce company (such as Amazon).  
The platform integrates **external agents** to handle all required elements, including **clients**, **third-party sellers**, **transportation services**, and **payment services**.

---

## ✅ Features

- **Multi-agent system** for distributed e-commerce management with **Flask**, **Jinja2** and **RDFLib**.
- System design with **Prometheus Design Tool (PDT)**.
- Centralized ontology shared across all agents for product data, orders, and communications with **Protégé**.  
- Integration of **external agents** for logistics, payments, and sellers.
- **RESTful routes** for interacting with the platform.
- Basic workflow:
  1. Product search based on user constraints.
  2. Order creation and processing.
  3. Shipment from the nearest logistics center.
  4. Invoices, recomendations and reviews.

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
git clone https://github.com/marcturu/ecommerce-multi-agent-platform.git
cd ecommerce-multi-agent-platform
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

---
### Original code at _https://github.com/ECSDI_  

---

## 📷 Screenshots  

### External product addition:
![ExternalProductAddition](screenshots/external_product_addition.jpg)
-
### Client registration:
![ClientRegistration0](screenshots/client_registration0.jpg)
-
![ClientRegistration1](screenshots/client_registration1.jpg)
-
### Main hub:
![MainHub](screenshots/main_hub.jpg)
-
### Products:
![Products0](screenshots/products0.jpg)
-
![Products1](screenshots/products1.jpg)
-
![Products2](screenshots/products2.jpg)
-
![Products3](screenshots/products3.jpg)
-
### Buying process:
![BuyingProcess0](screenshots/buying_process0.jpg)
-
![BuyingProcess1](screenshots/buying_process1.jpg)
-
![BuyingProcess2](screenshots/buying_process2.jpg)
-
### Recommendation:
![Recommendation](screenshots/recommendation.jpg)
-
### Review:
![Review](screenshots/review.jpg)
-
##### Points 13, 14, 15, 16, and 17 from `/docs/TestCases.pdf` could not be tested due to the significant amount of time that has passed, and because I no longer recall the exact procedure required to perform them.
---
### 2.1 Analysis Overview:
![AnalysisOverview](screenshots/analysis_overview.jpg)
-
### 2.2 Scenarios:
![Scenarios](screenshots/scenarios.jpg)
-
### 2.3 Goal Overview:
![GoalOverview](screenshots/goal_overview.jpg)
-
### 2.4 System Roles:
![SystemRoles](screenshots/system_roles.jpg)
-
### 3.1 Data Coupling:
![SataCoupling](screenshots/data_coupling.jpg)
-
### 3.2 Agent-Role Grouping:
![AgentRoleGrouping](screenshots/agent_role_grouping.jpg)
-
### 3.3 Agent Acquaintance:
![AgentAcquaintance](screenshots/agent_acquaintance.jpg)
-
### 3.4 System Overview:
![SystemOverview](screenshots/system_overview.jpg)
-
### Logístics:
![Logistics](screenshots/logistics.jpg)
-
### Shop Assistant:
![ShopAssistant](screenshots/shop_assistant.jpg)
-
### External:
![External](screenshots/external.jpg)
-
### Reviews Recorder:
![ReviewsRecorder](screenshots/reviews_recorder.jpg)
-
### Treasurer:
![Treasurer](screenshots/treasurer.jpg)
-
### Recommender:
![Recommender](screenshots/recommender.jpg)
-
### Returns Manager:
![ReturnsManager](screenshots/returns_manager.jpg)
-
### Sales Manager:
![SalesManager](screenshots/sales_manager.jpg)

--- 
### Ontology:
![Ontology](screenshots/ontology.jpg)

---

## ⚖️ Copyright & License

© 2024 Marc Turu Roca and collaborators. All rights reserved.  
This project is the joint intellectual property of its authors.  
No part may be copied, modified, distributed, or used without prior written permission from all authors.  

- Miquel García  
- Sergi Campuzano
- Marc Turu
