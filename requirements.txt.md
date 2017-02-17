### requirements.txt

安装依赖，可以虚拟环境下利用 `(venv) $ pip freeze >requirements.txt`  来生成

### MANIFEST.in

1. 当你在 setup.py 中包含了所有的文件时，MANIFEST.IN 文件可以不创建；
2. 若是你想增加或者删除某些文件，那么需要创建 MANIFEST.IN 文件；
3. MANIFEST.IN 里面通常包含一些 LICENSE、tests\*/\*py 文件；
4. 随着 [**qbr **](https://docs.openstack.org/developer/pbr/)的开发，setup.py 仅需要写三行代码，所有的信息都在 setup.cfg 和 requirements.txt 文件中维护。
5. neutron Juno（2014.02） 版本中的 MANIFEST.IN 的实例为：

```py
include AUTHORS
include README.rst
include ChangeLog
include LICENSE
include neutron/db/migration/README
include neutron/db/migration/alembic.ini
include neutron/db/migration/alembic_migrations/script.py.mako
include neutron/db/migration/alembic_migrations/versions/README
recursive-include neutron/locale *

exclude .gitignore
exclude .gitreview

global-exclude *.pyc
```

参考： [I don't understand python MANIFEST.in](http://stackoverflow.com/questions/24727709/i-dont-understand-python-manifest-in)

MAINFEST.IN 格式请参考： [The manifest template commands](https://docs.python.org/2/distutils/sourcedist.html#commands)

