# [oslo_middleware](https://docs.openstack.org/developer/oslo.middleware/)

## 安装

```
$ pip install oslo.middleware
```

或者你也可以在一个虚拟环境下这样子做：

```
$ mkvirtualenv oslo.middleware
$ pip install oslo.middleware
```

## API

### `class oslo_middleware.CatchErrors(application, conf=None)`

 * 提供高级错误处理的中间件。
 * 它捕获WSGI管道中后续应用程序的所有异常，隐藏 API 响应中的内部错误。

### `class oslo_middleware.CorrelationId(application, conf=None)`

 * 将相关 id 附加到 WSGI 请求的中间件

### `class oslo_middleware.CORS(application, *args, **kwargs)`

* CORS 中间件
 
* 这个中间件允许一个 WSGI 应用为多个配置域提供 CORS 头。

* 更多信息请参考：http://www.w3.org/TR/cors/

* `add_origin(allowed_origin, allow_credentials=True, expose_headers=None, max_age=None, allow_methods=None, allow_headers=None)`
 
 * 将另一个 origin 添加到此过滤器。
```
Parameters:	
    allowed_origin – Protocol, host, and port for the allowed origin.
    allow_credentials – Whether to permit credentials.
    expose_headers – A list of headers to expose.
    max_age – Maximum cache duration.
    allow_methods – List of HTTP methods to permit.
    allow_headers – List of HTTP headers to permit from the client.
Returns:
```

* `classmethod factory(global_conf, **local_conf)`
 
 * factory method for paste.deploy

* process_response(response, request=None)

 * 检查CORS标题，并在必要时进行装饰。

 * 执行两个检查。 首先，如果发出OPTIONS请求，请让应用程序处理它，并且（如果需要）使用preflight标头来装饰响应。 在这种情况下，如果底层应用程序抛出404（即如果底层应用程序不处理OPTIONS请求），则覆盖响应代码。

* `set_latent(allow_headers=None, allow_methods=None, expose_headers=None)`

 * 为这个中间件增加一个新的 latent 属性
 * latent 属性是系统需要操作的那些值。 例如，API-specific headers 可以由工程师添加，以便它们与代码库一起提供，因此不需要增加额外的文档。

```
参数：	
    allow_headers – HTTP headers permitted in client requests.
    allow_methods – HTTP methods permitted in client requests.
    expose_headers – HTTP Headers exposed to clients.
```

### `class oslo_middleware.Debug(application, conf=None)`

* 帮助类，返回调试信息。

* 可以插入到任何WSGI应用链中以获取有关请求和响应的信息。

* `static print_generator(app_iter)`
 * Prints the contents of a wrapper string iterator when iterated.

### `class oslo_middleware.Healthcheck(*args, **kwargs)`

* Healthcheck应用用于监控。

* It will respond 200 with “OK” as the body. Or a 503 with the reason as the body if one of the backends reports an application issue.

* 这是有用的，原因如下：
 * 负载平衡器可以 `ping` 此URL来确定服务可用性。
 * 提供类似于apache中的 `mod_status` 的 endpoint，可以提供有关服务器活动的详细信息（或者非详细信息，依赖配置）。
 * (and more)

* Example requests/responses (not detailed mode):

```
$ curl -i -X HEAD "http://0.0.0.0:8775/healthcheck"
HTTP/1.1 204 No Content
Content-Type: text/plain; charset=UTF-8
Content-Length: 0
Date: Fri, 11 Sep 2015 18:55:08 GMT

$ curl -i -X GET "http://0.0.0.0:8775/healthcheck"
HTTP/1.1 200 OK
Content-Type: text/plain; charset=UTF-8
Content-Length: 2
Date: Fri, 11 Sep 2015 18:55:43 GMT

OK

$ curl -X GET -i -H "Accept: application/json" "http://0.0.0.0:8775/healthcheck"
HTTP/1.0 200 OK
Date: Wed, 24 Aug 2016 06:09:58 GMT
Content-Type: application/json
Content-Length: 63

{
    "detailed": false,
    "reasons": [
        "OK"
    ]
}

$ curl -X GET -i -H "Accept: text/html" "http://0.0.0.0:8775/healthcheck"
HTTP/1.0 200 OK
Date: Wed, 24 Aug 2016 06:10:42 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 239

<HTML>
<HEAD><TITLE>Healthcheck Status</TITLE></HEAD>
<BODY>

<H2>Result of 1 checks:</H2>
<TABLE bgcolor="#ffffff" border="1">
<TBODY>
<TR>

<TH>
Reason
</TH>
</TR>
<TR>
    <TD>OK</TD>
</TR>
</TBODY>
</TABLE>
<HR></HR>

</BODY>
```

* Example requests/responses (detailed mode):

```
$ curl -X GET -i -H "Accept: application/json" "http://0.0.0.0:8775/healthcheck"
HTTP/1.0 200 OK
Date: Wed, 24 Aug 2016 06:11:59 GMT
Content-Type: application/json
Content-Length: 3480

{
    "detailed": true,
    "gc": {
        "counts": [
            293,
            10,
            5
        ],
        "threshold": [
            700,
            10,
            10
        ]
    },
    "greenthreads": [
       ...
    ],
    "now": "2016-08-24 06:11:59.419267",
    "platform": "Linux-4.2.0-27-generic-x86_64-with-Ubuntu-14.04-trusty",
    "python_version": "2.7.6 (default, Jun 22 2015, 17:58:13) \n[GCC 4.8.2]",
    "reasons": [
        {
            "class": "HealthcheckResult",
            "details": "Path '/tmp/dead' was not found",
            "reason": "OK"
        }
    ],
    "threads": [
        ...
    ]
}

$ curl -X GET -i -H "Accept: text/html" "http://0.0.0.0:8775/healthcheck"
HTTP/1.0 200 OK
Date: Wed, 24 Aug 2016 06:36:07 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 6838

<HTML>
<HEAD><TITLE>Healthcheck Status</TITLE></HEAD>
<BODY>
<H1>Server status</H1>
<B>Server hostname:</B><PRE>...</PRE>
<B>Current time:</B><PRE>2016-08-24 06:36:07.302559</PRE>
<B>Python version:</B><PRE>2.7.6 (default, Jun 22 2015, 17:58:13)
[GCC 4.8.2]</PRE>
<B>Platform:</B><PRE>Linux-4.2.0-27-generic-x86_64-with-Ubuntu-14.04-trusty</PRE>
<HR></HR>
<H2>Garbage collector:</H2>
<B>Counts:</B><PRE>(77, 1, 6)</PRE>
<B>Thresholds:</B><PRE>(700, 10, 10)</PRE>

<HR></HR>
<H2>Result of 1 checks:</H2>
<TABLE bgcolor="#ffffff" border="1">
<TBODY>
<TR>
<TH>
Kind
</TH>
<TH>
Reason
</TH>
<TH>
Details
</TH>

</TR>
<TR>
<TD>HealthcheckResult</TD>
    <TD>OK</TD>
<TD>Path &#39;/tmp/dead&#39; was not found</TD>
</TR>
</TBODY>
</TABLE>
<HR></HR>
<H2>1 greenthread(s) active:</H2>
<TABLE bgcolor="#ffffff" border="1">
<TBODY>
<TR>
    <TD><PRE>  File &#34;oslo_middleware/healthcheck/__main__.py&#34;, line 94, in &lt;module&gt;
    main()
  File &#34;oslo_middleware/healthcheck/__main__.py&#34;, line 90, in main
    server.serve_forever()
  ...
</PRE></TD>
</TR>
</TBODY>
</TABLE>
<HR></HR>
<H2>1 thread(s) active:</H2>
<TABLE bgcolor="#ffffff" border="1">
<TBODY>
<TR>
    <TD><PRE>  File &#34;oslo_middleware/healthcheck/__main__.py&#34;, line 94, in &lt;module&gt;
    main()
  File &#34;oslo_middleware/healthcheck/__main__.py&#34;, line 90, in main
    server.serve_forever()
  ....
</TR>
</TBODY>
</TABLE>
</BODY>
</HTML>
```

* Example of paste configuration:

```
[app:healthcheck]
use = egg:oslo.middleware:healthcheck
backends = disable_by_file
disable_by_file_path = /var/run/nova/healthcheck_disable

[pipeline:public_api]
pipeline = healthcheck sizelimit [...] public_service
```

* 如果想要具有不同健康检查配置的管道，可以定义多个过滤器部分，例如：

```
[composite:public_api]
use = egg:Paste#urlmap
/ = public_api_pipeline
/healthcheck = healthcheck_public

[composite:admin_api]
use = egg:Paste#urlmap
/ = admin_api_pipeline
/healthcheck = healthcheck_admin

[pipeline:public_api_pipeline]
pipeline = sizelimit [...] public_service

[pipeline:admin_api_pipeline]
pipeline = sizelimit [...] admin_service

[app:healthcheck_public]
use = egg:oslo.middleware:healthcheck
backends = disable_by_file
disable_by_file_path = /var/run/nova/healthcheck_public_disable

[filter:healthcheck_admin]
use = egg:oslo.middleware:healthcheck
backends = disable_by_file
disable_by_file_path = /var/run/nova/healthcheck_admin_disable
```

* `classmethod app_factory(global_conf, **local_conf)`
 * Factory method for paste.deploy.

```
参数：
    global_conf – dict of options for all middlewares (usually the [DEFAULT] section of the paste deploy configuration file)
    local_conf – options dedicated to this middleware (usually the option defined in the middleware section of the paste deploy configuration file)
```

## `class oslo_middleware.HTTPProxyToWSGI(application, *args, **kwargs)`

* HTTP proxy to WSGI termination middleware.

* 这个中间件使用远程HTTP反向代理提供的WSGI环境变量来重载WSGI环境变量。

## `class oslo_middleware.RequestId(application, conf=None)`

* Middleware that ensures request ID.

* 它确保为每个API请求分配请求ID并将其增加到请求的环境中。请求ID也添加到API响应中。

## `class oslo_middleware.RequestBodySizeLimiter(application, conf=None)`

* Limit the size of incoming requests.

## `class oslo_middleware.SSLMiddleware(application, *args, **kwargs)`

* SSL termination proxies middleware.

* 这个中间件重载 `secure_proxy_ssl_header` 头文件中提供的 `wsgi.url_scheme`。这在SSL终端代理的背后很有用。

## 配置选项

### RequestBodySizeLimiter

#### oslo_middleware

`max_request_body_size`
Type:	integer
Default:	114688
请求的最大消息体（字节）

已弃用的：
Group	Name
DEFAULT	osapi_max_request_body_size
DEFAULT	max_request_body_size

### SSLMiddleware

#### oslo_middleware

`secure_proxy_ssl_header`
Type:	string
Default:	X-Forwarded-Proto

HTTP头将用于确定原始请求协议方案是什么，即使它被SSL终止代理隐藏。

**Warning:** 这个选项已被弃用。它的值在将来的版本中可能会被忽略。

## Healthcheck middleware plugins

###  `class oslo_middleware.Healthcheck(*args, **kwargs)` 

### `class oslo_middleware.healthcheck.disable_by_file.DisableByFileHealthcheck(*args, **kwargs)`

* DisableByFile healthcheck middleware plugin

* 该插件检查文件的存在以报告该服务是否不可用。

* Example of middleware configuration:

```
[filter:healthcheck]
paste.filter_factory = oslo_middleware:Healthcheck.factory
path = /healthcheck
backends = disable_by_file
disable_by_file_path = /var/run/nova/healthcheck_disable
# set to True to enable detailed output, False is the default
detailed = False
```

### `class oslo_middleware.healthcheck.disable_by_file.DisableByFilesPortsHealthcheck(*args, **kwargs)`

* DisableByFilesPorts healthcheck middleware plugin

* 此插件会检查为某个端口上运行的应用程序提供的文件是否存在，以报告该服务是否不可用。

* Example of middleware configuration:

```
[filter:healthcheck]
paste.filter_factory = oslo_middleware:Healthcheck.factory
path = /healthcheck
backends = disable_by_files_ports
disable_by_file_paths = 5000:/var/run/keystone/healthcheck_disable,             35357:/var/run/keystone/admin_healthcheck_disable
# set to True to enable detailed output, False is the default
detailed = False
```

## CORS Middleware

这个中间件提供了一个全面的，可配置的[CORS](http://www.w3.org/TR/cors/)（Cross Origin Resource Sharing）规范的实现，这个规范是oslo支持的python wsgi中间件。

*注意： 虽然该中间件支持在规范中使用星号通配符，但由于安全原因，不推荐使用此功能。 提供了简化CORS的基本使用，实际上意思是“我不在乎如何使用”。在内部网设置中，这可能会导致数据泄漏超出内部网，因此应该避免。*

### Quickstart

* 首先，在您的应用程序中包含中间件：

```
from oslo_middleware import cors

app = cors.CORS(your_wsgi_application)
```

* 其次，添加您希望的 origin：

```
app.add_origin(allowed_origin='https://website.example.com:443',
               allow_credentials=True,
               max_age=3600,
               allow_methods=['GET','PUT','POST','DELETE'],
               allow_headers=['X-Custom-Header'],
               expose_headers=['X-Custom-Header'])

# ... add more origins here.
```

### Configuration for oslo_config

* 提供了一种工厂方法来简化CORS域的配置，使用oslo_config：

```
from oslo_middleware import cors
from oslo_config import cfg

app = cors.CORS(your_wsgi_application, cfg.CONF)
```

* 在您的应用程序的配置文件中，添加一个配置块：

```
[cors]
allowed_origin=https://website.example.com:443,https://website2.example.com:443
max_age=3600
allow_methods=GET,POST,PUT,DELETE
allow_headers=X-Custom-Header
expose_headers=X-Custom-Header
```

### Configuration for pastedeploy

* 如果您的应用程序正在使用pastedeploy，以下配置块将添加CORS支持：

```
[filter:cors]
use = egg:oslo.middleware#cors
allowed_origin=https://website.example.com:443,https://website2.example.com:443
max_age=3600
allow_methods=GET,POST,PUT,DELETE
allow_headers=X-Custom-Header
expose_headers=X-Custom-Header
```

* 如果您的应用程序正在使用pastedeploy，但也希望使用oslo_config中的现有配置来简化配置点，可以按如下方式完成：

```
[filter:cors]
use = egg:oslo.middleware#cors
oslo_config_project = oslo_project_name

# Optional field, in case the program name is different from the project:
oslo_config_program = oslo_project_name-api
```

### Configuration Options

```
allowed_origin
   Type:	list
    Default:	<None>
```

指示该资源是否可以与请求“origin”头中接收到的域共享。格式：“<protocol>：// <host> [：<port>]”，没有尾随斜线。示例：`https：//horizo​​n.example.com`

```
allow_credentials
    Type:	boolean
    Default:	true
```

表示实际请求可以包括用户凭据

```
expose_headers
    Type:	list
    Default:	
```

指示哪些头可以安全地暴露给API。默认为HTTP简单头文件。

```
max_age
    Type:	integer
    Default:	3600
```

CORS预检要求的最大缓存时间。

```
allow_methods
    Type:	list
    Default:	OPTIONS,GET,HEAD,POST,PUT,DELETE,TRACE,PATCH
```

指示在实际请求期间可以使用哪些方法。

```
allow_headers
Type:	list
Default:	
```

指示在实际请求期间可以使用哪个头字段名称。

#### cors.subdomain

```
allowed_origin
    Type:	list
    Default:	<None>
```

指示该资源是否可以与请求“origin”头中接收到的域共享。格式：“<protocol>：// <host> [：<port>]”，没有尾随斜线。示例：`https：//horizo​​n.example.com`

```
allow_credentials
    Type:	boolean
    Default:	true
```

表示实际请求可以包括用户凭据

```
expose_headers
    Type:	list
    Default:	
```

指示哪些头可以安全地暴露给API。默认为HTTP简单头文件。

```
max_age
    Type:	integer
    Default:	3600
```

CORS预检要求的最大缓存时间。

```
allow_methods
    Type:	list
    Default:	OPTIONS,GET,HEAD,POST,PUT,DELETE,TRACE,PATCH
```

指示在实际请求期间可以使用哪些方法。

```
allow_headers
    Type:	list
    Default:
```

指示在实际请求期间可以使用哪个头字段名称。

### Module Documentation

#### `class oslo_middleware.cors.CORS(application, *args, **kwargs)`

#### `exception oslo_middleware.cors.InvalidOriginError(origin)`

当Origin无效时发出异常。

#### `oslo_middleware.cors.set_defaults(**kwargs)`

* 覆盖配置选项的默认值。

* 此方法允许项目覆盖默认的CORS选项值。例如，它可能希望提供一组合理的默认头，使其在最小的附加配置下也可以工作。

```
Parameters:	
    allow_credentials (bool) – Whether to permit credentials.
    expose_headers (List of Strings) – A list of headers to expose.
    max_age (Int) – Maximum cache duration in seconds.
    allow_methods (List of Strings) – List of HTTP methods to permit.
    allow_headers (List of Strings) – List of HTTP headers to permit from the client.
```

## Middlewares and configuration

根据应用需要，可以多种方式配置中间件。这里有一些用例：

###　Configuration from the application

应用程序代码将如下所示：

```
from oslo_middleware import sizelimit
from oslo_config import cfg

conf = cfg.ConfigOpts()
app = sizelimit.RequestBodySizeLimiter(your_wsgi_application, conf)
```

### Configuration with paste-deploy and the oslo.config

The paste filter (in /etc/my_app/api-paste.ini) will looks like:

```
[filter:sizelimit]
use = egg:oslo.middleware#sizelimit
# In case of the application doesn't use the global oslo.config
# object. The middleware must known the app name to load
# the application configuration, by setting this:
#  oslo_config_project = my_app

# In some cases, you may need to specify the program name for the project
# as well.
#  oslo_config_program = my_app-api
```

The oslo.config file of the application (eg: /etc/my_app/my_app.conf) will looks like:

```
[oslo_middleware]
max_request_body_size=1000
```

### Configuration with pastedeploy only

The paste filter (in /etc/my_app/api-paste.ini) will looks like:

```
[filter:sizelimit]
use = egg:oslo.middleware#sizelimit
max_request_body_size=1000
```

这里面的配置将会覆盖 oslo.config 中的配置

**Note：** healtcheck 中间件不使用 oslo.config, 详情请见： [Healthcheck middleware plugins](https://docs.openstack.org/developer/oslo.middleware/healthcheck_plugins.html)

## 参考文档

[跨域资源共享 CORS 详解](http://www.ruanyifeng.com/blog/2016/04/cors.html)

[浏览器同源政策及其规避方法](http://www.ruanyifeng.com/blog/2016/04/same-origin-policy.html)






