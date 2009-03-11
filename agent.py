'''
	Server Density
	www.serverdensity.com
	----
	A web based server resource monitoring application

	(C) Boxed Ice 2009 all rights reserved
'''

# General config
DEBUG_MODE = 0
CHECK_FREQUENCY = 60

VERSION = '1.0.0b1'

# Core modules
import ConfigParser
import logging
import sched
import time
import sys

# Custom modules
from checks import checks
from daemon import Daemon

# Config handling
try:
	config = ConfigParser.ConfigParser()
	config.read('config.cfg')
	SD_URL = config.get('Main', 'sd_url')
	AGENT_KEY = config.get('Main', 'agent_key')
except ConfigParser.NoSectionError, e:
	print 'Config file not found or incorrectly formatted'
	quit()
except ConfigParser.ParsingError, e:
	print 'Config file not found or incorrectly formatted'
	quit()

# Override the generic daemon class to run our checks
class agent(Daemon):	
	
	def run(self):	
		agentLogger = logging.getLogger('agent')		
		agentLogger.debug('Creating checks instance')
		
		# Checks instance
		c = checks(SD_URL, AGENT_KEY, CHECK_FREQUENCY)
		
		# Schedule the checks
		agentLogger.debug('Scheduling checks every ' + str(CHECK_FREQUENCY) + ' seconds')
		s = sched.scheduler(time.time, time.sleep)
		s.enter(CHECK_FREQUENCY, 1, c.doChecks, (s,))
		s.run()

# Control of daemon		
if __name__ == '__main__':	
	# Logging
	if DEBUG_MODE:
		logging.basicConfig(filename='/tmp/sd-agent.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	mainLogger = logging.getLogger('main')		
	mainLogger.debug('Agent called')
	
	# Daemon instance from agent class
	daemon = agent('/tmp/sd-agent.pid')
	
	# Control options
	if len(sys.argv) == 2:		
		if 'start' == sys.argv[1]:
			mainLogger.debug('Start daemon')
			daemon.start()
		elif 'stop' == sys.argv[1]:
			mainLogger.debug('Stop daemon')
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			mainLogger.debug('Restart daemon')
			daemon.restart()
		else:
			print 'Unknown command'
			sys.exit(2)
		sys.exit(0)
	else:
		print 'usage: %s start|stop|restart' % sys.argv[0]
		sys.exit(2)

