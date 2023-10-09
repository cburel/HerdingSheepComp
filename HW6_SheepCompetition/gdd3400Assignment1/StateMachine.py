from asyncio.windows_events import NULL
from Constants import *
from pygame import *
from random import *
from Vector import *
from Agent import *
from Sheep import *
from Dog import *
from Graph import *
from Node import *
from GameState import *

class StateMachine:
	""" Machine that manages the set of states and their transitions """

	def __init__(self, startState):
		""" Initialize the state machine and its start state"""
		self.__currentState = startState
		self.__currentState.enter()

	def getCurrentState(self):
		""" Get the current state """
		return self.__currentState

	def update(self, gameState):
		""" Run the update on the current state and determine if we should transition """
		nextState = self.__currentState.update(gameState)

		# If the nextState that is returned by current state's update is not the same
		# state, then transition to that new state
		if nextState != None and type(nextState) != type(self.__currentState):
			self.transitionTo(nextState)

	def transitionTo(self, nextState):
		""" Transition to the next state """
		self.__currentState.exit()
		self.__currentState = nextState
		self.__currentState.enter()

	def draw(self, screen):
		""" Draw any debugging information associated with the states """
		self.__currentState.draw(screen)

class State:
	def enter(self):
		""" Enter this state, perform any setup required """
		print("Entering " + self.__class__.__name__)
		
	def exit(self):
		""" Exit this state, perform any shutdown or cleanup required """
		print("Exiting " + self.__class__.__name__)

	def update(self, gameState):
		""" Update this state, before leaving update, return the next state """
		print("Updating " + self.__class__.__name__)

	def draw(self, screen):
		""" Draw any debugging info required by this state """
		pass

			   
class FindSheepState(State):
	""" This is an example state that simply picks the first sheep to target """

	def update(self, gameState):
		""" Update this state using the current gameState """
		super().update(gameState)
		dog = gameState.getDog()
		
		#pick the closest sheep
		herd = gameState.getHerd()
		dog.setTargetSheep(min([s for s in herd], key=lambda s: dog.center.distance_to(Vector(s.center.x, s.center.y))))

		# You could add some logic here to pick which state to go to next
		# depending on the gameState

		#dog.calculatePathToNewTarget(dog.getTargetSheep().center)

		if dog.center.x < Constants.WORLD_WIDTH / 2 and dog.center.y < Constants.WORLD_HEIGHT / 2:
			return InUpperLeftQuadrant()
		if dog.center.x < Constants.WORLD_WIDTH / 2 and dog.center.y > Constants.WORLD_HEIGHT / 2:
			return InLowerLeftQuadrant()
		if dog.center.x > Constants.WORLD_WIDTH / 2 and dog.center.y < Constants.WORLD_HEIGHT / 2:
			return InUpperRightQuadrant()
		if dog.center.x > Constants.WORLD_WIDTH / 2 and dog.center.y > Constants.WORLD_HEIGHT / 2:
			return InLowerRightQuadrant()

class InUpperLeftQuadrant(State):

	def enter(self):
		super().enter()

	def update(self, gameState):
		super().update(gameState)
		
		dog = gameState.getDog()
		sheep = dog.getTargetSheep()
		graph = gameState.getGraph()

		if sheep.center.y > dog.center.y:
			print("sheep y > dog y. sheep is below dog.")
			dog.calculatePathToNewTarget(sheep.center)
			
		if sheep.center.y < dog.center.y:
			print ("sheep y < dog y. sheep is above dog.")
			#move dog to above sheep
			targetPoint = Vector(sheep.center.x, sheep.center.y - Constants.GRID_SIZE)
			#dog.targetNode = graph.getNodeFromPoint(targetPoint)
			dog.calculatePathToNewTarget(targetPoint)
		
		return Idle()

	def exit(self):
		super().exit()

class InLowerLeftQuadrant(State):

	def enter(self):
		super().enter()

	def update(self, gameState):
		super().update(gameState)

		dog = gameState.getDog()
		sheep = dog.getTargetSheep()
		graph = gameState.getGraph()

		if sheep.center.y > dog.center.y:
			print("sheep y > dog y. sheep is below dog.")
			#move dog to below sheep
			targetPoint = Vector(sheep.center.x, sheep.center.y + Constants.GRID_SIZE)
			#dog.targetNode = graph.getNodeFromPoint(targetPoint)
			dog.calculatePathToNewTarget(targetPoint)

		if sheep.center.y < dog.center.y:
			print ("sheep y < dog y. sheep is above dog.")
			dog.calculatePathToNewTarget(sheep.center)

		return Idle()

	def exit(self):
		super().exit()

class InUpperRightQuadrant(State):

	def enter(self):
		super().enter()

	def update(self, gameState):
		super().update(gameState)

		dog = gameState.getDog()
		sheep = dog.getTargetSheep()
		graph = gameState.getGraph()

		if sheep.center.y > dog.center.y:
			print("sheep y > dog y. sheep is below dog.")
			dog.calculatePathToNewTarget(sheep.center)

		if sheep.center.y < dog.center.y:
			print ("sheep y < dog y. sheep is above dog.")
			#move dog to above sheep
			targetPoint = Vector(sheep.center.x, sheep.center.y - Constants.GRID_SIZE)
			#dog.targetNode = graph.getNodeFromPoint(targetPoint)
			dog.calculatePathToNewTarget(targetPoint)

		return Idle()

	def exit(self):
		super().exit()

class InLowerRightQuadrant(State):

	def enter(self):
		super().enter()

	def update(self, gameState):
		super().update(gameState)

		dog = gameState.getDog()
		sheep = dog.getTargetSheep()
		graph = gameState.getGraph()

		if sheep.center.y > dog.center.y:
			print("sheep y > dog y. sheep is below dog.")
			#move dog to below sheep
			targetPoint = Vector(sheep.center.x, sheep.center.y + Constants.GRID_SIZE)
			#dog.targetNode = graph.getNodeFromPoint(targetPoint)
			dog.calculatePathToNewTarget(targetPoint)

		if sheep.center.y < dog.center.y:
			print ("sheep y < dog y. sheep is above dog.")
			dog.calculatePathToNewTarget(sheep.center)

		return Idle()

	def exit(self):
		super().exit()

class Idle(State):
	""" This is an idle state where the dog does nothing """

	def update(self, gameState):
		super().update(gameState)
		
		# Do nothing
		if len(gameState.getHerd()) > 0:
			return FindSheepState()
		else:
			return Idle()