# Eisen - Productivity Boost with Simple Eisenhower Matrix

Eisen is a carefully crafted task manager that brings the power of the Eisenhower Matrix to your fingertips. It's designed to organize your tasks and give you a clear, actionable path to achieving your goals, one focused step at a time. Simple by design, focusing only on features that increase productivity without much tinkering around settings and configurations.

---

## ✨ Features

Eisen gives the structure to stay focused and the flexibility to adapt.

### 🗂️ Stay Organized with Projects
Keep your different worlds separate and organized. Whether it's for "Work," "Personal Projects," or "Home Renovation," Eisen allows you to create distinct projects. Switch between them effortlessly, ensuring your focus is always where it needs to be, without any distracting cross-contamination.

### 🎯 The Matrix at a Glance
See your priorities laid out in a color-coded dashboard. The four quadrants of the Eisenhower Matrix give you an instant and intuitive understanding of where your energy should be spent.

### 📝 Deep Dive with Tasks and Subtasks
Big goals are achieved by breaking them down. Eisen understands this. Go beyond simple to-dos and add detailed **descriptions** to your tasks. Then, truly take control by breaking any task into a checklist of manageable **subtasks**. It's the perfect way to tackle complex projects without feeling overwhelmed.

### ✏️ Effortless Editing and Refinement
Plans change. Eisen makes it easy to adapt. With a single tap, you can edit the name and description of any task or subtask. Your task list becomes a living document, always perfectly aligned with your current priorities.

### 🔄 Powerful, Flexible Management
Take control with intelligent bulk actions. Select one or many tasks to move them between quadrants as their urgency shifts. Need to clean up? Select and delete multiple completed or outdated tasks in a flash. This same power extends to subtasks, allowing you to manage your checklists with surgical precision.

### 📊 Quick Project Summary
Get a bird's-eye view of your progress in a project. The Summary screen provides hierarchical report of your entire project. See every task, every subtask, and their completion status laid out clearly. It's the perfect way to review your progress, celebrate your accomplishments, and plan your next move.

### 💾 Seamless and Reliable Saving
Eisen automatically saves everything to a local file on your device the moment you make a change. Projects, tasks, subtasks, descriptions, and completion status—it's all safely stored, ready for you the moment you reopen the app. No saving buttons, no fuss.

---

## 📱 Running on Android

Take your productivity on the go! Eisen is built with Kivy, allowing it to be packaged as a native Android application. This repository already includes a `buildozer.spec` configuration file to make the process straightforward.

### Prerequisites

1.  **Install Buildozer and its dependencies:**
    ```bash
    pip install buildozer
    pip install cython
    ```

2.  **Install Android SDK & NDK:** Buildozer will attempt to download and set these up for you on the first run, but you can also install them manually for more control.

### Building the APK

1.  **Navigate to the project directory** in your terminal where `main.py` and `buildozer.spec` are located.

2.  **Build the application:** Run the following command to compile your Python code and package it into a debug APK.
    ```bash
    buildozer -v android debug
    ```
    This process might take a while, especially the first time, as it downloads all the necessary Android dependencies. The finished APK will be located in the `bin/` directory.

### Deploying to Your Device

To install and run the app directly on a connected Android device (make sure USB debugging is enabled), use `buildozer android debug deploy run` bash command.

For more detailed information and troubleshooting, please refer to the official [Kivy Packaging for Android documentation](https://kivy.org/doc/stable/guide/packaging-android.html).

---

## 🛠️ Getting Started on Desktop

Ready to bring clarity to your chaos?

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ucukertz/eisen.git
    cd eisen
    ```

2.  **Install Kivy:**
    It's best to use a virtual environment.
    ```bash
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install Kivy
    pip install kivy
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Author

Created by **[ucukertz](https://github.com/ucukertz)**.
