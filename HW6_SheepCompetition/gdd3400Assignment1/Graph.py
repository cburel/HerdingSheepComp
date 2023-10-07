import Constants
import Node
import pygame
import Vector

from pygame import *
from Vector import *
from Node import *
from enum import Enum

class SearchType(Enum):
	BREADTH = 0
	DJIKSTRA = 1
	A_STAR = 2
	BEST_FIRST = 3

class Graph():
	def __init__(self):
		""" Initialize the Graph """
		self.nodes = []			# Set of nodes
		self.obstacles = []		# Set of obstacles - used for collision detection

		# Initialize the size of the graph based on the world size
		self.gridWidth = int(Constants.WORLD_WIDTH / Constants.GRID_SIZE)
		self.gridHeight = int(Constants.WORLD_HEIGHT / Constants.GRID_SIZE)

		# Create grid of nodes
		for i in range(self.gridHeight):
			row = []
			for j in range(self.gridWidth):
				node = Node(i, j, Vector(Constants.GRID_SIZE * j, Constants.GRID_SIZE * i), Vector(Constants.GRID_SIZE, Constants.GRID_SIZE))
				row.append(node)
			self.nodes.append(row)

		## Connect to Neighbors
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				# Add the top row of neighbors
				if i - 1 >= 0:
					# Add the upper left
					if j - 1 >= 0:		
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j - 1]]
					# Add the upper center
					self.nodes[i][j].neighbors += [self.nodes[i - 1][j]]
					# Add the upper right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j + 1]]

				# Add the center row of neighbors
				# Add the left center
				if j - 1 >= 0:
					self.nodes[i][j].neighbors += [self.nodes[i][j - 1]]
				# Add the right center
				if j + 1 < self.gridWidth:
					self.nodes[i][j].neighbors += [self.nodes[i][j + 1]]
				
				# Add the bottom row of neighbors
				if i + 1 < self.gridHeight:
					# Add the lower left
					if j - 1 >= 0:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j - 1]]
					# Add the lower center
					self.nodes[i][j].neighbors += [self.nodes[i + 1][j]]
					# Add the lower right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j + 1]]

	def getNodeFromPoint(self, point):
		""" Get the node in the graph that corresponds to a point in the world """
		point.x = max(0, min(point.x, Constants.WORLD_WIDTH - 1))
		point.y = max(0, min(point.y, Constants.WORLD_HEIGHT - 1))

		# Return the node that corresponds to this point
		return self.nodes[int(point.y/Constants.GRID_SIZE)][int(point.x/Constants.GRID_SIZE)]

	def placeObstacle(self, point, color):
		""" Place an obstacle on the graph """
		node = self.getNodeFromPoint(point)

		# If the node is not already an obstacle, make it one
		if node.isWalkable:
			# Indicate that this node cannot be traversed
			node.isWalkable = False		

			# Set a specific color for this obstacle
			node.color = color
			for neighbor in node.neighbors:
				neighbor.neighbors.remove(node)
			node.neighbors = []
			self.obstacles += [node]

	def reset(self):
		""" Reset all the nodes for another search """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].reset()

	def buildPath(self, endNode):
		""" Go backwards through the graph reconstructing the path """
		path = []
		node = endNode
		while node is not 0:
			node.isPath = True
			path = [node] + path
			node = node.backNode

		# If there are nodes in the path, reset the colors of start/end
		if len(path) > 0:
			path[0].isPath = False
			path[0].isStart = True
			path[-1].isPath = False
			path[-1].isEnd = True
		return path

	def distance(self, curr, neighbor):
		return math.sqrt((curr.center.x - neighbor.center.x) ** 2 + (curr.center.y - neighbor.center.y) ** 2)

	def findPath_Breadth(self, start, end):
		""" Breadth Search """
		#print("Breadth")
		self.reset()

		#set up lists
		unvisited = []
		toVisit = []
		visited = []

		#add all nodes to unvisited
		for row in self.nodes:
			for node in row:
				unvisited.append(node)
			
		#add start node to queue
		startNode = self.getNodeFromPoint(start)
		toVisit.append(startNode)
		unvisited.remove(startNode)

		while toVisit:

			#remove current node from toVisit, add to visited
			curr = toVisit.pop(0)
			visited.append(curr)
			curr.isVisited = False
			curr.isExplored = True

			#for each nextnode connected to current node
			for neighbor in curr.neighbors:

				#if next node is unvisited
				if neighbor in unvisited:

					#add nextnode to toVisit, remove nextnode from unvisited
					toVisit.append(neighbor)
					neighbor.isVisited = True
					neighbor.isExplored = False
					unvisited.remove(neighbor)

					# set next node's back to currentnode
					neighbor.backNode = curr

					#if next node is goal node
					endNode = self.getNodeFromPoint(end)
					if neighbor == endNode:
					
						# terminate with success
						return self.buildPath(endNode)

		return []

	def findPath_Djikstra(self, start, end):
		""" Djikstra's Search """
		#print("DJIKSTRA")
		self.reset()

		#set up lists
		unvisited = []
		priorityQueue = []
		visited = []

		#mark all nodes unvisited
		for row in self.nodes:
			for node in row:
				node.costToEnd = 0
				node.costFromStart = 0
				node.cost = 0
				unvisited.append(node)

		#mark start node visited
		startNode = self.getNodeFromPoint(start)
		startNode.costToEnd = 0

		#add start node to pQueue
		priorityQueue.append(startNode)
		unvisited.remove(startNode)

		#while queue is not empty
		while priorityQueue:

			#remove curr node from queue
			curr = priorityQueue.pop(0)
			visited.append(curr)
			curr.isVisited = False
			curr.isExplored = True

			#if curr node is goal, terminate with success
			endNode = self.getNodeFromPoint(end)
			if curr == endNode:
				return self.buildPath(endNode)

		# for each next node connected to curr
			for neighbor in curr.neighbors:

				#currDistance = Distance(currentNode, nextNode)
				#currDist = math.sqrt((curr.center.x - neighbor.center.x) ** 2 + (curr.center.y - neighbor.center.y) ** 2)
				currDist = self.distance(curr, neighbor)

				#if next node is not visited
				if neighbor in unvisited:

					#mark next node visited
					unvisited.remove(neighbor)
					visited.append(neighbor)
					neighbor.isVisited = True
					neighbor.isExplored = False

					#next node distance = currDistance + currentNode.dist
					neighbor.costFromStart = currDist + curr.costFromStart
					neighbor.cost = neighbor.costFromStart + neighbor.costToEnd
					neighbor.backNode = curr

					# add next node to pQueue
					priorityQueue.append(neighbor)
					
				#else node has been visited, update dist if shorter
				else:
					#if currDistance + currentNode.dist < nextNode.dist
					if currDist + curr.cost < neighbor.cost:

						#nextNode.dist = currDistance + currentNode.dist
						neighbor.costFromStart = currDist + curr.costFromStart
						neighbor.cost = neighbor.costFromStart + neighbor.costToEnd

						#nextNode.parent = curr
						neighbor.backNode = curr
				
				#sort queue by cost
				priorityQueue.sort(key=lambda x: x.cost, reverse=False)

		return []

	def findPath_AStar(self, start, end):
		""" A Star Search """
		#print("A_STAR")
		self.reset()

		#set up lists
		unvisited = []
		priorityQueue = []
		visited = []

		#mark all nodes unvisited
		for row in self.nodes:
			for node in row:
				node.costToEnd = 0
				node.costFromStart = 0
				node.cost = 0
				unvisited.append(node)

		#mark start node visited
		startNode = self.getNodeFromPoint(start)
		endNode = self.getNodeFromPoint(end)
		startNode.costToEnd = self.distance(startNode, endNode)

		#add start node to pQueue
		priorityQueue.append(startNode)
		unvisited.remove(startNode)

		#while queue is not empty
		while priorityQueue:

			#remove curr node from queue
			curr = priorityQueue.pop(0)
			visited.append(curr)
			curr.isVisited = False
			curr.isExplored = True

			#if curr node is goal, terminate with success
			if curr == endNode:
				return self.buildPath(endNode)

		# for each next node connected to curr
			for neighbor in curr.neighbors:

				#currDistance = Distance(currentNode, nextNode)
				#currDist = math.sqrt((curr.center.x - neighbor.center.x) ** 2 + (curr.center.y - neighbor.center.y) ** 2)
				currDist = self.distance(curr, neighbor)

				#if next node is not visited
				if neighbor in unvisited:

					#mark next node visited
					unvisited.remove(neighbor)
					visited.append(neighbor)
					neighbor.isVisited = True
					neighbor.isExplored = False

					#next node distance = currDistance + currentNode.dist
					neighbor.costToEnd = self.distance(neighbor, endNode)
					neighbor.costFromStart = currDist + curr.costFromStart
					neighbor.cost = neighbor.costFromStart + neighbor.costToEnd
					neighbor.backNode = curr

					# add next node to pQueue
					priorityQueue.append(neighbor)
					
				#else node has been visited, update dist if shorter
				else:
					#if currDistance + currentNode.dist < nextNode.dist
					if currDist + curr.cost < neighbor.cost:

						#nextNode.dist = currDistance + currentNode.dist
						neighbor.costFromStart = currDist + curr.costFromStart
						neighbor.cost = neighbor.costFromStart + neighbor.costToEnd

						#nextNode.parent = curr
						neighbor.backNode = curr
				
				#sort queue by cost
				priorityQueue.sort(key=lambda x: x.cost, reverse=False)

		return []

	def findPath_BestFirst(self, start, end):
		""" Best First Search """
		#print("BEST_FIRST")
		self.reset()

		#set up lists
		unvisited = []
		priorityQueue = []
		visited = []

		#mark all nodes unvisited
		for row in self.nodes:
			for node in row:
				node.costToEnd = 0
				node.costFromStart = 0
				node.cost = 0
				unvisited.append(node)

		#mark start node visited
		startNode = self.getNodeFromPoint(start)
		startNode.costToEnd = 0

		#get end node
		endNode = self.getNodeFromPoint(end)

		#add start node to pQueue
		priorityQueue.append(startNode)
		unvisited.remove(startNode)

		#while queue is not empty
		while priorityQueue:

			#remove curr node from queue
			curr = priorityQueue.pop(0)
			visited.append(curr)
			curr.isVisited = False
			curr.isExplored = True

			#if curr node is goal, terminate with success
			if curr == endNode:
				return self.buildPath(endNode)

		# for each next node connected to curr
			for neighbor in curr.neighbors:

				#currDistance = Distance(currentNode, nextNode)
				currDist = self.distance(neighbor, endNode)

				#if next node is not visited
				if neighbor in unvisited:

					#mark next node visited
					unvisited.remove(neighbor)
					visited.append(neighbor)
					neighbor.isVisited = True
					neighbor.isExplored = False

					#next node distance = currDistance + currentNode.dist
					neighbor.costToEnd = currDist
					neighbor.cost = neighbor.costFromStart + neighbor.costToEnd
					neighbor.backNode = curr

					# add next node to pQueue
					priorityQueue.append(neighbor)
									
				#sort queue by cost
				priorityQueue.sort(key=lambda x: x.cost, reverse=False)

		return []

	def draw(self, screen):
		""" Draw the graph """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].draw(screen)