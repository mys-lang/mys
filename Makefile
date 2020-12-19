test: test-python
	$(MAKE) -C examples all
	python3 -m mys --version | wc -l | grep -c 1

test-python:
	env MYS="PYTHONPATH=$$(readlink -f .) coverage run -p --source=mys --omit=\"**/mys/parser/**\" -m mys" coverage run -p --source=mys --omit="**/mys/parser/**" setup.py test $(ARGS)
	coverage combine -a $$(find -name ".coverage.*")
	coverage html
