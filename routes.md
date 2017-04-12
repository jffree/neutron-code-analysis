# routes

## 简介

*Routes 其实就是 Python 版本的 Rails 的 routes. 它用来将用户的不同 URLs 自动匹配 到不同的应用上, 对于开发 RESTful 的 API 和其他 web 的应用非常方便。*

### 特性

- Sophisticated route lookup and URL generation
- Named routes
- Redirect routes
- Wildcard paths before and after static parts
- Sub-domain support built-in
- Conditional matching based on domain, cookies, HTTP method (RESTful), and more
- Easily extensible utilizing custom condition functions and route generation functions
- Extensive unit tests

## 设定 routes

### 一个典型的配置

```
from routes import Mapper
map = Mapper()
map.connect(None, "/error/{action}/{id}", controller="error")
map.connect("home", "/", controller="main", action="index")
# ADD CUSTOM ROUTES HERE
map.connect(None, "/{controller}/{action}")
map.connect(None, "/{controller}/{action}/{id}")
```

* 第一行和第二行创建一个 mapper

* 第三行匹配任意三组件的并且以 `/error` 开头的 route，并且设定 controller 为常量。*

 * 若一个 URL 为 `/error/images/arrow.jpg`，那么将会产生： `{"controller": "error", "action": "images", "id": "arrow.jpg"}`

* 第四行匹配一个单独的 URL `/`，并且将 `controller` 和 `action` 设为常量。它还有一个路由名称 `home`，可以在 generataion 中使用。 （其他路由都是None而不是一个名字，所以没有名字。建议为所有可能在 generation 中使用的路由命名，但不必命名不会使用的路由。）

* 第6行定义了可以匹配任何2组件的URL，第7行定义了可以匹配任何3组件的URL。如果我们太懒惰地为每个动作定义一个单独的路线，可以使用它们。如果您为每个操作定义了路由，则可以删除这两条路由。

**请注意：** 一个 URL `/error/images/arrow.jpg` 可以匹配第3行和第7行。mapper 通过按照定义的顺序尝试路由来解决此问题，因此该URL将与第3行匹配。

如果没有路由匹配URL，则映射器返回“匹配失败”条件，这在Pylons中被看作是HTTP 404“未找到”。

以下是有效路线的一些例子：

```
m.connect("/feeds/{category}/atom.xml", controller="feeds", action="atom")
m.connect("history", "/archives/by_eon/{century}", controller="archives",
          action="aggregate")
m.connect("article", "/article/{section}/{slug}/{page}.html",
          controller="article", action="view")
```

额外的变量可能是任何Python类型，而不仅仅是字符串。但是，如果在 generation 中使用 route，则将在该值上调用 `str()`，除非给 generation 指定一个重写值。

允许其他参数语法与早期版本的路由兼容。这些在后向兼容性部分中描述。

路线应始终以斜杠（`/`）开头。较早版本的路由允许无斜线的路径，但它们的行为现在是未定义的。

### Requirements

可以将路径变量限制为正则表达式;例如，仅匹配数字分量或限制词的选择。这里有两种语法：inline 写法和requirements参数。inline 写法如下所示：

```
map.connect(R"/blog/{id:\d+}")
map.connect(R"/download/{platform:windows|mac}/{filename}")
```

这匹配 `/blog/123`，而不是 `/blog/12A`。等效的 requirements  语法是：

```
map.connect("/blog/{id}", requirements={"id": R"\d+"}
map.connect("/download/{platform}/{filename}",
    requirements={"platform": R"windows|mac"})
```

请注意使用原始字符串语法（`R""`）来包含带有反斜杠的正则表达式。没有 `R`，你必须加倍每一个反斜杠。

另一个例子：

```
m.connect("/archives/{year}/{month}/{day}", controller="archives",
          action="view", year=2004,
          requirements=dict(year=R"\d{2,4}", month=R"\d{1,2}"))
```

路由中添加了内联语法。以前的版本只有 `requirements` 参数。`requirements` 参数的两个优点是，如果您有几个具有相同要求的变量，则可以将一个变量或整个参数设置为全局：

```
NUMERIC = R"\d+"
map.connect(..., requirements={"id": NUMERIC})

ARTICLE_REQS = {"year": R"\d\d\d\d", "month": R"\d\d", "day": R"\d\d"}
map.connect(..., requirements=ARTICLE_REQS)
```

因为 `requirements` 参数为保留字，所以您不能使用该名称定义路由变量。

### 神奇的 path_info

如果在URL的末尾使用 `path_info` 变量，路由将其前面的所有内容移动到 `SCRIPT_NAME` 环境变量中。当委托给另一个执行自己的路由的WSGI应用程序时，这是非常有用的：子应用程序将仅针对URL的剩余部分路由，而不是整个URL。 您仍然需要 `:.*` requirement 来将余下的URL组件捕获到变量中。

```
map.connect(None, "/cards/{path_info:.*}",
    controller="main", action="cards")
# Incoming URL "/cards/diamonds/4.png"
=> {"controller": "main", action: "cards", "path_info": "/diamonds/4.png"}
# Second WSGI application sees:
# SCRIPT_NAME="/cards"   PATH_INFO="/diamonds/4.png"
```

该路由不符合 `/cards`，因为它还需要一个斜杠。添加另一条路线来解决这个问题：

```
map.connect("cards", "/cards", controller="main", action="cards",
    path_info="/")
```

你也可以将两者组合到一起：

```
map.connect("cards", "/cards{path_info:.*}",
    controller="main", action="cards")
```

但是有两个问题。一个，它也会匹配 `/cardshark`。二， routes 1.10版本中有一个错误：它忘了从 `SCRIPT_NAME` 中取下后缀。

路由的未来版本或许会直接委派给WSGI应用程序，但现在必须在框架中完成。在Pylons中，您可以在 controller action 中执行以下操作：

```
from paste.fileapp import DirectoryApp
def cards(self, environ, start_response):
    app = DirectoryApp("/cards-directory")
    return app(environ, start_response)
```

或者为WSGI应用程序创建一个带有 `__controller__` 变量的假控制器模块：

```
from paste.fileapp import DirectoryApp
__controller__ = DirectoryApp("/cards-directory")
```

### Conditions

Conditions 对可以匹配什么类型的请求做额外的限制。`conditions` 参数是最多三个键的dict：

* method

 * 大写HTTP方法的列表。request必须是列出的方法之一。

* sub_domain

 * 可以是子域列表True，False或None。如果是列表，request必须是指定的子域之一。如果为True，request 必须包含一个子域，但它可以是任何东西。如果为False或None，则如果有子域名，则不匹配。
 * *New in Routes 1.10: ``False`` and ``None`` values.*

* function

 * 评估 request 的函数。 它的格式必须是 `func（environ，match_dict）=> bool`。 如果匹配成功则返回 true，否则返回false。 第一个参数是WSGI环境; 第二个是匹配成功时返回的路由变量。该函数可以修改 `match_dict`，以影响返回哪些变量。 这允许广泛的转换。

实例：

```
# Match only if the HTTP method is "GET" or "HEAD".
m.connect("/user/list", controller="user", action="list",
          conditions=dict(method=["GET", "HEAD"]))

# A sub-domain should be present.
m.connect("/", controller="user", action="home",
          conditions=dict(sub_domain=True))

# Sub-domain should be either "fred" or "george".
m.connect("/", controller="user", action="home",
          conditions=dict(sub_domain=["fred", "george"]))

# Put the referrer into the resulting match dictionary.
# This function always returns true, so it never prevents the match
# from succeeding.
def referals(environ, result):
    result["referer"] = environ.get("HTTP_REFERER")
    return True
m.connect("/{controller}/{action}/{id}",
    conditions=dict(function=referals))
```






