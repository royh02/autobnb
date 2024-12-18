# autobnb

AutoBnb: Making searching for a place on Airbnb a breeze

# Environment Setup

1. **Install Conda and Use Python 3.10**:

   ```bash
   conda create -n autobnb python=3.10
   conda activate autobnb
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Autogen Locally**:

   ```bash
   git clone https://github.com/microsoft/autogen.git
   cd autogen/python
   ```

4. **Install Magnetic One from Autogen**:

   ```bash
   cd packages/autogen-magentic-one
   pip install -e .
   cd ../autogen-core
   pip install -e .
   cd ../autogen-ext
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
