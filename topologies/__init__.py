import sys
from pathlib import Path

# Add project root to path for robust imports from anywhere
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import all topology classes
from topoResearch.topologies.HPC_topo import HPC_topo
from topoResearch.topologies.RRG import RRGtopo
from topoResearch.topologies.DDF import DDFtopo
from topoResearch.topologies.Slimfly import Slimflytopo
from topoResearch.topologies.Polarfly import Polarflytopo
from topoResearch.topologies.Equality import Equalitytopo

__all__ = ['HPC_topo', 'RRGtopo', 'DDFtopo', 'Slimflytopo', 'Polarflytopo', 'Equalitytopo', 'GDBGtopo']
