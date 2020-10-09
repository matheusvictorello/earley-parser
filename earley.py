from collections import defaultdict

class Rules:
	def __init__(self):
		self.rules = defaultdict(list)

	def __getitem__(self, key):
		return self.rules[key]

	def __repr__(self):
		rules = ''

		for pre, rets in self.rules.items():
			rules += f'\t{pre} -> '
			rules += ' | '.join(rets)
			rules += '\n'

		return f'Rules(\n{rules})'

	def add(self, pre, ret):
		self.rules[pre].append(ret)

	def isPre(self, c):
		return c in self.rules.keys()

class Grammar:
	def __init__(self, text):
		self.rules = Rules()
		
		text = text.replace(' ', '')
		lines = text.split('\n')
		for line in lines:
			if len(line) == 0:
				continue
			pre, rets = line.split('->')
			rets = rets.split('|')
			for ret in rets:
				self.rules.add(pre, ret)

	def isTerminal(self, c):
		return not self.rules.isPre(c)

	def rulesFromPre(self, pre):
		return self.rules[pre]

class State:
	def __init__(self, pre, ret, point, origin, description=''):
		self.pre = pre
		self.ret = ret
		self.point = point
		self.origin = origin
		self.description = description

	def __eq__(self, o):
		return (self.pre == o.pre) and (self.ret == o.ret) and (self.point == o.point) and (self.origin == o.origin)

	def __repr__(self):
		return f'{self.pre} -> {self.ret[:self.point]}.{self.ret[self.point:]}, origin={self.origin} {self.description}'

	def next(self):
		if self.isCompleted():
			return None
		return self.ret[self.point]

	def isCompleted(self):
		return self.point == len(self.ret)

class Chart:
	def __init__(self, index):
		self.states = []
		self.index = index
	
	def __iter__(self):
		return iter(self.states)
	
	def add(self, state):
		if not any(map(lambda other : state == other, self.states)):
			state.chartIndex = self.index
			state.stateIndex = len(self.states)
			self.states.append(state)

class ChartList:
	def __init__(self, size):
		self.charts = [Chart(i) for i in range(size)]

	def __iter__(self):
		return iter(self.charts)

	def __getitem__(self, index):
		return self.charts[index]

	def add(self, index, state):
		self.charts[index].add(state)

class Parser:
	def parse(self, grammar, sentence):
		finalState = State('@', 'S', point=1, origin=0)
		chartList = ChartList(len(sentence) + 1)
		chartList.add(0, State('@', 'S', point=0, origin=0, description='Start rule'))

		def completer(state, chartIndex, stateIndex):
			chart = chartList[state.origin]
			for s in chart:
				if state.pre == s.next():
					newState = State(s.pre, s.ret, point=s.point + 1, origin=s.origin, description=f'Completed from ({stateIndex}) and S({s.chartIndex})({s.stateIndex})')
					chartList[chartIndex].add(newState)

		def scanner(state, chartIndex, stateIndex, sentence):
			if state.next() == sentence[chartIndex]:
				chart = chartList[chartIndex + 1]
				newState = State(state.pre, state.ret, point=state.point + 1, origin=state.origin, description=f'Scaned from S({chartIndex})({stateIndex})')
				chart.add(newState)

		def predictor(state, chartIndex, stateIndex):
			pre = state.next()

			for ret in grammar.rulesFromPre(pre):
				chart = chartList[chartIndex]
				newState = State(pre, ret, point=0, origin=chartIndex, description=f'Predicted from S({chartIndex})({stateIndex})')
				chart.add(newState)

		for chartIndex, chart in enumerate(chartList):
			print(f'S({chartIndex}) {sentence[:chartIndex]}.{sentence[chartIndex:]}')

			for stateIndex, state in enumerate(chart):
				print(f'{stateIndex} -    {state}')
				
				if state.isCompleted():
					completer(state, chartIndex, stateIndex)
				else:
					if grammar.isTerminal(state.next()):
						scanner(state, chartIndex, stateIndex, sentence)
					else:
						predictor(state, chartIndex, stateIndex)

		if finalState in chartList[-1]:
			print('Acepted')
		else:
			print('Rejected')

def main():
	myRules = '''
S -> A
A -> (L) | x
L -> A | L;A'''
	sentence = '(x;x);x'

	grammar = Grammar(myRules)
	parser = Parser()
	parser.parse(grammar, sentence)

if __name__ == '__main__':
	main()