import os
from com.open.algo.utils import DynamicLoader
from behave import *

RESOURCES_ROOT = 'test-resources'


@given('we have a dynamic loader module')
def step_impl(context):
    pass


@when('i say load components definition file "{component}"')
def step_impl(context, component):
    context.components = DynamicLoader().loadFromPath(RESOURCES_ROOT, component, globals())


@then('we find component "{name}" is "{component}"')
def step_impl(context, name, component):
    assert isinstance(component, object)
    assert context.components[name] == component


@then('we find component "{name}" is of type "{ctype}"')
def step_impl(context, name, ctype):
    item = context.myMod[name]
    assert item is not None
    print('asserting that the component "%s" is of type "%s", found "%s"' % (name, ctype, item.__class__.__name__))
    assert item.__class__.__name__ == ctype


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
    sf = open(os.path.join(RESOURCES_ROOT, fn), 'r')
    for line in sf.readlines():
        location = line.find(varName)
        commentLocation = line.find('#')
        if location >= 0 and line.find('=') < location and (
                commentLocation == -1 or commentLocation > location + varLen):
            fileHasVariable = True
            break
    sf.close()
    assert fileHasVariable


@when('i say load given components definition file')
def step_impl(context):
    globals()[context.varName] = context.inputValue
    context.myMod = DynamicLoader().loadFromPath(RESOURCES_ROOT, context.component, globals())


@then('we find component "{name}" has value "{value}"')
def step_impl(context, name, value):
    print('->asserting value for variable "%s" = "%s"' % (name, value))
    assert context.myMod[name] == value

