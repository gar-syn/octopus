# Twisted Imports
from twisted.internet import defer
from twisted.internet.protocol import Factory

# System Imports
from time import time as now

# Sibling Imports
from data import Image

# Package Imports
from ..machine import Machine, Property, Stream, ui

def _get_centroids (count):
	def get_centroids (processed_img, min_size):
		blobs = processed_img.findBlobs(min_size)

		if blobs is not None:
			blobs = blobs.sortArea()[-count:].sortX()
			return [blob.centroid() for blob in blobs]

		else:
			return None

	return get_centroids


class SingleBlobTracker (Machine):

	protocolFactory = None
	name = "Follow Green Blobs on a webcam"
	update_frequency = 1

	def setup (self):
		# setup variables
		self.height = Stream(title = "Height", type = int)
		self.status = Property(title = "Status", type = str)
		self.image = Image(title = "Tracked", fn = self._get_image)
		self.visualisation = Image(title = "Visualisation", fn = self._get_visualisation)

		self.process_fn = lambda r, g, b: (g - r).threshold(30).erode()
		self.blob_size = 100
		self._get_centroids = _get_centroids(1)

		self.ui = ui(
			properties = [self.status, self.height, self.image, self.visualisation]
		)

	def start (self):
		def monitor ():
			img = self.protocol.image()
			img = self.process_fn(*img.splitChannels())
			pos = self._get_centroids(img, self.blob_size)

			if pos is not None:
				self.height._push(img.height - pos[0][1])
				self.status._push("ok")
			else:
				self.status._push("error")

		self._tick(monitor, self.update_frequency)

	def show (self):
		self._get_image().show()

	def _get_image (self):
		img = self.protocol.image()
		processed_img = self.process_fn(*img.splitChannels())
		pos = self._get_centroids(processed_img, self.blob_size)

		if pos is not None:
			x, y = pos[0]
			img.drawRectangle(x - 10, y - 10, 20, 20, (255,) * 3, width = 6)

		return img

	def _get_visualisation (self):
		img = self.protocol.image()
		img = self.process_fn(*img.splitChannels())

		return img

	def stop (self):
		self._stopTicks()


class MultiBlobTracker (Machine):

	protocolFactory = None
	name = "Follow Blobs on a webcam"

	x_tolerance = 30

	update_frequency = 1

	def setup (self, count = 1, fn = None):

		self._count = count
		self._heights = []
		self.blob_size = 100

		if fn is None:
			self.process_fn = lambda r, g, b: (g - r).threshold(30).erode()
		else:
			self.process_fn = fn

		# setup variables
		for i in range(count):
			stream = Stream(title = "Height %s" % (i + 1), type = int)
			setattr(self, "height%s" % (i + 1), stream)
			self._heights.append(stream)

		self.image = Image(title = "Tracked", fn = self._get_image)
		self.visualisation = Image(title = "Visualisation", fn = self._get_visualisation)
		self.status = Property(title = "Status", type = str)

		self.ui = ui(
			properties = [self.status, self.image, self.visualisation] + self._heights
		)

	def start (self):
		img = self.protocol.image()
		img = self.process_fn(*img.splitChannels())
		pos = self._get_centroids(img, self.blob_size)

		self._x = []
		if len(pos) < self._count:
			raise Exception("Could not find %s blobs" % self._count)

		for p in pos:
			self._x.append(p[0])

		def monitor ():
			img = self.protocol.image()
			img = self.process_fn(*img.splitChannels())
			pos = self._get_centroids(img, self.blob_size)

			if pos is not None:
				found = 0

				for i in range(self._count):
					_x = self._x[i]

					for x, y in pos:
						if abs(x - _x) < self.x_tolerance:
							self._heights[i]._push(img.height - y)
							found += 1

				if found < self._count:
					self.status._push("blobs-missing")
				else:
					self.status._push("ok")
			else:
				self.status._push("error")

		self._tick(monitor, self.update_frequency)

	def show (self):
		self._get_image().show()

	def _get_image (self):
		img = self.protocol.image()
		processed_img = self.process_fn(*img.splitChannels())
		pos = self._get_centroids(processed_img, self.blob_size)

		if pos is not None:
			for x, y in pos:
				x, y = pos
				img.drawRectangle(x - 10, y - 10, 20, 20, (255,) * 3, width = 6)

		return img

	def _get_visualisation (self):
		img = self.protocol.image()
		img = self.process_fn(*img.splitChannels())

		return img

	def stop (self):
		self._stopTicks()
