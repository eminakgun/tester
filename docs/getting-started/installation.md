# Installation

This guide will help you install and set up the Tester tool for your environment.

## Prerequisites

Before installing Tester, ensure you have the following:

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Access to UVM simulators (VCS, Questa, or Xcelium)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/tester.git
cd tester
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Verify Installation

To verify that the installation was successful, run:

```bash     
python tester.py --help
```

You should see the help message displaying available commands and options.

## Next Steps
- Quick Start Guide - Learn how to run your first test
- Configuration Guide - Learn how to configure the tool for your project