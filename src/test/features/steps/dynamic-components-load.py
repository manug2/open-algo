import sys
sys.path.append('../main/')

from com.open.algo.utils import DynamicLoader
from behave import *

@given('we have a dynamic loader module')
def step_impl(context):
	assert DynamicLoader != None

@when('i say load components definition file "{component}"')
def step_impl(context, component):
	context.components = DynamicLoader().load(component)

@then('we find component "{name}" is "{component}"')
def step_impl(context, name, component):
	assert context.components.__dict__[name] == component
	
@then('we find component "{name}" is of type "{ctype}"')
def step_impl(context, name, ctype):
	item = context.myMod[name]
	assert item != None
	item.__class__.__name__ == ctype

@given('variable "{varName}" has value "{inputValue}"')
def step_impl(context, varName, inputValue):
	context.varName = varName
	context.inputValue = inputValue

@given('there exists definition file "{componentFile}" which uses variable "{varName}"')
def step_impl(context, componentFile, varName):
	context.component = componentFile
	fileHasVariable = False
	if (componentFile.endswith('.py')):
		fn = componentFile
	else:
		fn = componentFile + '.py'
	
	varLen = len(varName)
	sf = open(fn, 'r')
	for line in sf.readlines():
		location = line.find(varName) 
		commentLocation = line.find('#') 
		if location>=0 and line.find('=') < location and (commentLocation == -1 or commentLocation > location + varLen) :
			fileHasVariable = True
			break
	sf.close()
	assert fileHasVariable == True

@when('i say load given components definition file')
def step_impl(context):
	globals()[context.varName] = context.inputValue
	context.myMod = DynamicLoader().loadFromPath('.', context.component, globals())
	
@then('we find component "{name}" has value "{value}"')
def step_impl(context, name, value):
	assert context.myMod[name] == value

