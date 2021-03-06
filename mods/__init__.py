semester = '2018B'
local_io = '/Users/jgreco/local-io/'

log_level = 'debug'
datapath = local_io + 'LBT-' + semester + '/data'
calipath = local_io + 'MODS-cali-data'

from .log import get_logger
logger = get_logger(log_level)

from .config import LongslitReduceConfig
from . import files
from . import reduce
from . import imarith
from . import utils
