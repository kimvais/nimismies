setup:
	dropdb nimismies;
	createdb nimismies;
	python manage.py syncdb;
	python manage.py migrate nimismies;
	./adduser.py k@77.fi
