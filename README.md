# autobnb

AutoBnb: Making searching for a place on Airbnb a breeze

# Environment Setup

1. **Install Conda and Use Python 3.10**:
    ```bash
    conda create -n myenv python=3.10
    conda activate myenv
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Autogen Locally and Activate Virtual Environment**:
    ```bash
    git clone https://github.com/microsoft/autogen.git
    cd autogen/python
    uv sync --all-extras
    source .venv/bin/activate
    ```

4. **Install Magnetic One from Autogen**:
    ```bash
    cd packages/autogen-magentic-one
    pip install -e .
    ```

5. **Configure Environment Variables**:
    Create a `.env` file with the following content:
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    ```

6. **Setup the Backend Server**:
    ```bash
    python3 main.py
    ```

7. **Start the Application Locally** (in a different terminal window):
    ```bash
    cd autobnb-app
    npm i
    npm run start
    ```

# Instructions
1. Submit the form based on user preferences, and watch Autobnb generate your ideal Airbnb!


