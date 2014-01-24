
# Package Imports
from ..constants import State
from ..util import now

# Sibling Imports
import util

class PID (util.Looping, util.Dependent):
	interval = 0.5

	proportional = 25
	integral = 0.25
	differential = 500

	max = 3000
	min = 100

	def __init__ (self, error, response):
		util.Dependent.__init__(self)
		util.Looping.__init__(self)

		self.error = error
		self.response = response
		self._prev_error = None

	def _iterate (self):
		current = float(self.response)
		interval = float(self.interval)

		e = float(self.error)
		e_prev, self._prev_error = self._prev_error, e

		if e_prev is None:
			return

		# trapezium rule
		integral_term = \
			(min(e, e_prev) * interval) + \
			(0.5 * (e + e_prev) * interval)

		# difference rule
		differential_term = (e - e_prev) / interval

		# PID control
		change = \
			(self.proportional * e) + \
			(self.integral * integral_term) + \
			(self.differential * differential_term)

		new = current + change
		new = min(max(new, self.min), self.max)
		
		self.response.set(new)


class StateMonitor (util.Looping, util.Dependent):
	interval = 0.5

	def __init__ (self, auto_reset = True):
		util.Dependent.__init__(self)
		util.Looping.__init__(self)

		from ..sequence import Sequence

		self.tests = set()
		self.step = Sequence([])
		self._triggered = False
		self._auto_reset = auto_reset

	def add (self, test):
		self.tests.add(test)

	def remove (self, test):
		self.tests.discard(test)

	def _iterate (self):
		if self._triggered:
			if self._auto_reset and all(self.tests):
				self._triggered = False

			return

		if not all(self.tests):
			try:
				self.step.reset()
				self.step.run()
			except AlreadyRunning:
				return

			self._triggered = True

	def reset_trigger (self):
		self._triggered = False

	def _cancel (self):
		util.Looping._cancel(self)
		self.reset_trigger()