"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame. If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame import item
from libqtopensesame import qtplugin
from openexp.keyboard import keyboard

import serial

	
class serial_port_trigger(item.item):

	"""
	This class (the class with the same name as the module)
	handles the basic functionality of the item. It does
	not deal with GUI stuff.
	"""

	def __init__(self, name, experiment, string = None):
	
		"""
		Constructor
		"""
		
		# The item_typeshould match the name of the module
		self.item_type = u"serial_port_trigger"
		
		# Provide a short accurate description of the item's functionality
		self.description = u"Allows changing the serial port state, useful for sending triggers"
		
		# Set some item-specific variables
		self.value = 0
		self.duration = 500
		self.port = u"COM1"
		self.autodetect = u"no"
		self.reset = u"no"
		
		# The parent handles the rest of the contruction
		item.item.__init__(self, name, experiment, string)

	def prepare(self):
	
		"""
		Prepare the item by establishing a connection with the serial port,
		and setting its value to 0, as well as adding the closing function
		to the cleanup functions
		"""
		
		# Pass the word on to the parent
		item.item.prepare(self)
		
		# autodetect if requested
		if self.get(u"autodetect") == u"yes":
			for i in range(100):
				try:
					self.experiment.serialport = serial.Serial(u"COM%d" % i)
					self.port = i
					break
				except:
					pass

		# create a Serial instance (use default settings, only pass port)
		else:
			self.experiment.serialport = serial.Serial(self.get(u"port"))
		
		# report which port will be used
		print(u"serial port 'COM%d' initialized" % self.get(u"port"))
		
		# write a 0 to the serial port
		self.experiment.serialport.write(chr(0))
		
		# add the closing function to the cleanup functions, so we can be
		# sure that the serial port connection is closed properly, even in
		# case of a crash or an abort
		self.experiment.cleanup_functions.append(self.experiment.serialport.close)
		
		# create keyboard object
		self.kb = keyboard(self.experiment, keylist=[u"escape"])
		
		# Report success
		return True
				
	def run(self):
	
		"""
		Run the item. In this case we will write a value to the serial port,
		then wait for the specified duration, then optionally reset the
		serial port state to 0
		"""
		
		# write value to serial port
		self.experiment.serialport.write(chr(self.get(u"value")))

		# use keyboard as timeout, allowing for Escape presses to abort experiment
		self.kb.get_key(timeout=self.get(u"duration"))

		# reset to value 0 is requested
		if self.get(u"reset") == u"yes":
			self.experiment.serialport.write(chr(0))
				
		# Report success
		return True
					
class qtserial_port_trigger(serial_port_trigger, qtplugin.qtplugin):

	"""
	This class (the class named qt[name of module] handles
	the GUI part of the plugin. For more information about
	GUI programming using PyQt4, see:
	<http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>
	"""

	def __init__(self, name, experiment, string = None):
	
		"""
		Constructor
		"""
		
		# Pass the word on to the parents		
		serial_port_trigger.__init__(self, name, experiment, string)		
		qtplugin.qtplugin.__init__(self, __file__)	
		
	def init_edit_widget(self):
	
		"""
		This function creates the controls for the edit
		widget.
		"""
		
		# Lock the widget until we're doing creating it
		self.lock = True
		
		# Pass the word on to the parent		
		qtplugin.qtplugin.init_edit_widget(self, False)
		
		# Create the controls
		# 
		# A number of convenience functions are available which 
		# automatically create controls, which are also automatically
		# updated and applied. If you set the varname to None, the
		# controls will be created, but not automatically updated
		# and applied.
		#
		# qtplugin.add_combobox_control(varname, label, list_of_options)
		# - creates a QComboBox
		# qtplugin.add_line_edit_control(varname, label)
		# - creates a QLineEdit		
		# qtplugin.add_spinbox_control(varname, label, min, max, suffix = suffix, prefix = prefix)
		
		self.add_line_edit_control(u"value", u"Value", tooltip=u"Value to set port")
		self.add_line_edit_control(u"duration", u"Duration", tooltip=u"Expecting a value in milliseconds")
		self.add_line_edit_control(u"port", u"Port Address", tooltip=u"Address of the serial port, e.g. COM1")
		self.add_checkbox_control(u"autodetect", u"Auto Detect", tooltip=u"Tick to let the system look for the first available serial port")
		self.add_checkbox_control(u"reset", u"Reset", tooltip=u"Tick to write a value of 0 after the trigger")
		
		# Add a stretch to the edit_vbox, so that the controls do not
		# stretch to the bottom of the window.
		self.edit_vbox.addStretch()
		
		# Unlock
		self.lock = False		
		
	def apply_edit_changes(self):
	
		"""
		Set the variables based on the controls
		"""
		
		# Abort if the parent reports failure of if the controls are locked
		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return False
				
		# Refresh the main window, so that changes become visible everywhere
		self.experiment.main_window.refresh(self.name)		
		
		# Report success
		return True

	def edit_widget(self):
	
		"""
		Set the controls based on the variables
		"""
		
		# Lock the controls, otherwise a recursive loop might aris
		# in which updating the controls causes the variables to be
		# updated, which causes the controls to be updated, etc...
		self.lock = True
		
		# Let the parent handle everything
		qtplugin.qtplugin.edit_widget(self)				
		
		# Unlock
		self.lock = False
		
		# Return the _edit_widget
		return self._edit_widget
