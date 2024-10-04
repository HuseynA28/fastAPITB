## Setting Up a Virtual Environment with Python's `venv`

### Creating and Activating the Virtual Environment

To isolate and manage the project dependencies, it's recommended to use Python's built-in `venv` module to create a virtual environment. Here are the steps to set it up:

1. **Create the Virtual Environment:**
   Navigate to your project directory and run the following command:
   ```bash
   python -m venv ABIAPIFAST
  ```
  ```
.\ABIAPIFAST\Scripts\activate
  ```
Installing Dependencies
With the virtual environment activated, install the project dependencies as specified in your requirements.txt file:
  ```
pip install -r requirements.txt
  ```