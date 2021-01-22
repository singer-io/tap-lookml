.DEFAULT_GOAL := test

test:
	pylint tap_lookml --disable missing-module-docstring,missing-function-docstring,missing-class-docstring,line-too-long,protected-access,too-many-arguments,too-many-locals,too-many-nested-blocks,unused-variable,unused-argument,too-many-statements,redefined-builtin,inconsistent-return-statements,useless-object-inheritance,too-many-branches,no-else-raise,raise-missing-from
