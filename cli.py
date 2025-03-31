import argparse
import os
import sys
from typing import Dict, Any, List, Optional

from .config.config_manager import ConfigManager
from .simulator.vcs import VCSSimulator
from .simulator.questa import QuestaSimulator
from .simulator.xcelium import XceliumSimulator
from .simulator.makefile import MakefileSimulator
from .build_systems.simulators.adapter import SimulatorAdapter
from .build_systems.makefile.adapter import MakefileBuildSystem
from .runner.test_runner import TestRunner 