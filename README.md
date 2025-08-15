# 🛒 ECSDI-Project — E-commerce Multi-Agent Platform

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

### External product addition:
![1](https://github.com/user-attachments/assets/aba9031f-4735-4337-bd07-757308bc5c05)
-
### Client registration:
![2](https://github.com/user-attachments/assets/f2bda514-3398-4544-812c-c2d572bbba5c)
-
![3](https://github.com/user-attachments/assets/a6945289-654b-4fa2-9023-aea54c444140)
-
### Main hub:
![3+1](https://github.com/user-attachments/assets/8ab4cea5-3a47-41de-a246-2ae660f890a3)
-
### Products:
![4](https://github.com/user-attachments/assets/c8b27a1e-a2ad-47fa-ac33-2a62e4289f74)
-
![7](https://github.com/user-attachments/assets/8ea3b8f4-b8e8-4eed-a438-ff69a218958b)
-
![8](https://github.com/user-attachments/assets/8900ce53-4fa4-4669-8dbd-7fd04c56330e)
-
![5](https://github.com/user-attachments/assets/cf72216e-781a-4a7b-973c-5fa46254bdf6)
-
### Buying process:
![6](https://github.com/user-attachments/assets/d77e2358-1e57-4a15-823b-52b38744d9f5)
-
![9](https://github.com/user-attachments/assets/5cb3fd28-439b-430d-ad06-224b024427b7)
-
![10](https://github.com/user-attachments/assets/e2f2c161-6263-49d4-a5ed-1748ad945494)
-
### Recommendation:
![11](https://github.com/user-attachments/assets/442d1ff5-dfb8-4e6d-b7df-13569361e06c)
-
### Review:
![12](https://github.com/user-attachments/assets/9ae51df9-b77c-4d21-af05-914a1a39ac12)
-
##### Points 13, 14, 15, 16, and 17 from `/docs/TestCases.pdf` could not be tested due to the significant amount of time that has passed, and because I no longer recall the exact procedure required to perform them.
---
### 2.1 Analysis Overview:
![13](https://github.com/user-attachments/assets/c994f994-2bc3-422c-af94-b8c71d804f38)
-
### 2.2 Scenarios:
![14](https://github.com/user-attachments/assets/e2f6baec-bdaa-4571-9406-12b6c89c7c07)
-
### 2.3 Goal Overview:
![15](https://github.com/user-attachments/assets/cec2e4e8-fb0a-487d-9dd8-d4737af2e423)
-
### 2.4 System Roles:
![16](https://github.com/user-attachments/assets/44509120-038a-454d-86fb-40af2dc36637)
-
### 3.1 Data Coupling:
![17](https://github.com/user-attachments/assets/8b932ac7-6e7d-458c-9f79-58605c840d33)
-
### 3.2 Agent-Role Grouping:
![18](https://github.com/user-attachments/assets/0eec9cb4-f0ef-4de7-bcd2-676ec2d6b287)
-
### 3.3 Agent Acquaintance:
![19](https://github.com/user-attachments/assets/4cd306ee-5684-4a8c-b3fe-a434bbe69ad7)
-
### 3.4 System Overview:
![20](https://github.com/user-attachments/assets/73d1c059-3bc5-486d-9760-36833a574a87)
-
### Logístics:
![21](https://github.com/user-attachments/assets/98d4aec9-02a1-46eb-89a1-a7cd1e50452f)
-
### Shop Assistant:
![22](https://github.com/user-attachments/assets/2827a44d-f320-4ed6-b976-a6fa6b59d558)
-
### External:
![23](https://github.com/user-attachments/assets/e18211e9-2027-481d-9054-69ffadf03f9b)
-
### Reviews Recorder:
![24](https://github.com/user-attachments/assets/d077e408-02f5-4289-92bd-70d1e006ddc1)
-
### Treasurer:
![25](https://github.com/user-attachments/assets/9fa2c685-9aee-4698-8222-77275de3974d)
-
### Recommender:
![26](https://github.com/user-attachments/assets/b0cf7c95-5d8a-4885-833f-338864eda737)
-
### Returns Manager:
![27](https://github.com/user-attachments/assets/01d1cf6a-1696-4fc5-8616-29a831a59342)
-
### Sales Manager:
![28](https://github.com/user-attachments/assets/31411fbb-e7f0-4e19-b257-334ca481189c)

---
### Ontology:
![29](https://github.com/user-attachments/assets/b0148522-1ef1-4e85-a33a-2e672412ae2f)

---

## ⚖️ Copyright

© 2024 Marc Turu Roca and collaborators. All rights reserved.  
This project is the joint intellectual property of its authors.  
No part may be copied, modified, distributed, or used without prior written permission from all authors.  

- Miquel García    
- Marc Turu
- Sergi Campuzano

