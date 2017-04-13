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

### 通配符 routes

默认情况下，路径变量不匹配斜杠。这确保每个变量将完全匹配一个组件。您可以使用 requirements 来覆盖此：

```
map.connect("/static/{filename:.*?}")
```

这将会匹配 `/static/foo.jpg`，`/static/bar/foo.jpg`等。

请注意，粗心的正则表达式可能会占用URL的其余部分，并导致其右侧的组件不匹配：

```
# OK because the following component is static and the regex has a "?".
map.connect("/static/{filename:.*?}/download")
```

这个教训告诉我们总是要测试通配符模式。

### 格式扩展

`{.format}` 的路径组件将匹配可选的格式扩展名（例如“.html”或“.json”），如果路径中有格式扩展名的话会将 format 变量设置为`.` 后的部分（例如“html”或“json”），否则为 `None`。例如：

```
map.connect('/entries/{id}{.format}')
```

将匹配 `/entries/1` 和 `/entries/1.mp3`。您可以使用要求限制哪些扩展名将匹配，例如：

```
map.connect('/entries/{id:\d+}{.format:json}')
```

将匹配 `/entries/1` 和 `/entries/1.json`，而不是 `/entries/1.mp3`。

与通配符路由一样，了解和测试很重要。没有上述 `id` 变量的 `\d+` 要求，`/entries/1.mp3` 将成功匹配，id变量捕获 `1.mp3`。

*New in Routes 1.12.*

### Submappers

Submappers 允许您添加几个类似的路由，而不必重复相同的关键字参数。有两种语法，一种使用Python的 `with` 块，另一种不使用 with。

```
# Using 'with'
with map.submapper(controller="home") as m:
    m.connect("home", "/", action="splash")
    m.connect("index", "/index", action="index")

# Not using 'with'
m = map.submapper(controller="home")
m.connect("home", "/", action="splash")
m.connect("index", "/index", action="index")

# Both of these syntaxes create the following routes::
# "/"      => {"controller": "home", action="splash"}
# "/index" => {"controller": "home", action="index"}
```

您还可以为 routes 指定公用路径前缀：

```
with map.submapper(path_prefix="/admin", controller="admin") as m:
    m.connect("admin_users", "/users", action="users")
    m.connect("admin_databases", "/databases", action="databases")

# /admin/users     => {"controller": "admin", "action": "users"}
# /admin/databases => {"controller": "admin", "action": "databases"}
```

在 submapper 中使用的所有参数都必须是关键字参数。

submapper 不是一个完整的 mapper。它只是一个带有.connect方法的临时对象，它向从其生成 mapper 的添加路由。

*New in Routes 1.11.*

### Submapper helpers

Submappers包含一些辅助工具，可进一步简化路由配置。例如：

```
with map.submapper(controller="home") as m:
    m.connect("home", "/", action="splash")
    m.connect("index", "/index", action="index")
```

可以写成

```
with map.submapper(controller="home", path_prefix="/") as m:
    m.action("home", action="splash")
    m.link("index")
```

`action`方法在 submapper 的路径（在上面的示例中为'/'）生成一个或多个HTTP方法的route（假定为'GET'）。`link` 在相对路径上生成 route。

有一些针对标准 `index, new, create, show, edit, update, delete` 动作的特定 helper。您可以直接使用这些：

```
with map.submapper(controller="entries", path_prefix="/entries") as entries:
    entries.index()
    with entries.submapper(path_prefix="/{id}") as entry:
        entry.show()
```

或者间接使用：

```
with map.submapper(controller="entries", path_prefix="/entries",
                   actions=["index"]) as entries:
    entries.submapper(path_prefix="/{id}", actions=["show"])
```

以这种方式嵌套的集合/成员子映射器是常见的，这也有helper：

```
map.collection(collection_name="entries", member_name="entry",
               controller="entries",
               collection_actions=["index"], member_actions["show"])
```

这将返回一个可以添加更多路由submapper 实例; 它具有 `member` 属性（嵌套子映射程序），可以向其中添加哪些成员特定 route。 当省略`collection_actions`或`member_actions`时，会生成完整的操作集（请参见下面的“打印”下的示例）。

请参阅下面的“RESTful服务”中的 `map.resource`，这是一个不使用submappers的 `map.collection` 的前身。

### 从嵌套应用程序添加 route

有时在嵌套应用程序中，子应用程序会向父项提供要添加到其映射器的路由列表。这些可以添加`.extend`方法，还可提供路径前缀：

```
from routes.route import Route
routes = [
    Route("index", "/index.html", controller="home", action="index"),
    ]

map.extend(routes)
# /index.html => {"controller": "home", "action": "index"}

map.extend(routes, "/subapp")
# /subapp/index.html => {"controller": "home", "action": "index"}
```

这并不是真正地将 route 对象添加到 mapper。它创建相同的新 route 对象，并将它们添加到mapper。

*New in Routes 1.11.*

## Generation

要生成URL，请使用您的框架提供的 `url` 或 `url_for` 对象。`url` 是 Routes `URLGenerator` 的一个实例，而 `url_for` 是较旧的 `routes.url_for()` 函数。`url_for`正在淘汰，所以新的应用程序应该使用 `url`。

要生成命名路由，请将路由名称指定为位置参数：

```
url("home")   =>  "/"
```

如果路由包含路径变量，则必须使用关键字参数为它们指定值：

```
url("blog", year=2008, month=10, day=2)
```

会自动使用 `str()` 将非字符串值转换为字符串。（若遇到包含非ASCII字符的Unicode值，则可能中断）。

但是，如果路由定义了与路径变量名称相同的额外变量，那么如果未指定该关键字，那么额外的变量将被用作默认值。例：

```
m.connect("archives", "/archives/{id}",
    controller="archives", action="view", id=1)
url("archives", id=123)  =>  "/archives/123"
url("archives")  =>  "/archives/1"
```

*（额外的变量不用于匹配，除非启用最小化。）*

任何不对应于路径变量的关键字参数都将放在**查询字符串**中。如果变量名与Python关键字相冲突，则附加`_`：

```
map.connect("archive", "/archive/{year}")
url("archive", year=2009, font=large)  =>  "/archive/2009?font=large"
url("archive", year=2009, print_=1)  =>  "/archive/2009?print=1"
```

如果应用程序安装在URL空间的子目录中，则所有生成的URL将具有应用程序前缀。应用程序前缀是请求的WSGI环境中的`SCRIPT_NAME`变量。

如果位置参数对应于没有命名的路由，则假定它是一个文字URL。应用程序的安装点是前缀，并将关键字args转换为查询参数：

```
url("/search", q="My question")  =>  "/search?q=My+question"
```

如果没有位置参数，Routes将使用关键字args来选择路由。 将选择具有由关键字args指定的所有路径变量的第一个路由以及未被关键字args覆盖的最小数量的额外变量。 这在较旧版本的路由中是常见的，但是如果选择了意外的路由，则可能会导致应用程序错误，因此使用路由名称是非常优选的，因为只保证命名的路由将被选择。 对于未命名生成的最常见的用法是当你有一个很少使用的控制器，具有很多特殊的方法; 例如，`url（controller =“admin”，action =“session”）`。

如果没有路由对应于参数，则会引发 `routes.util.GenerationException` 的异常。 （在路由1.9之前，返回 None。之后被更改为一个例外，以防止无效的空白URL被封装成模板。）

如果Python产生Unicode URL（如果路由路径或变量值为Unicode），则还会得到此异常。路由只生成`str` URL。

以下关键字参数是特殊的：

* anchor

 * 指定URL锚点（“＃”右侧的部分）。 `url("home", "summary")  =>  "/#summary"`

* host

 * 使URL完全限定，并覆盖 host（domain）。

* protocol

 * 使URL完全限定并覆盖协议（例如，`ftp`）。

* qualified

 * 使URL完全限定（即添加 `protocol://host:port` 前缀）。

* sub_domain

 * 请参考 “Generating URLs with subdomains”。

*本节中的语法对于url和url_for都是相同的。*

*New in Routes 1.10: ``url`` and the ``URLGenerator`` class behind it.*

### 根据当前URL生成路由

`url.current()` 返回当前请求的URL，不带查询字符串。 这被称为 `路由内存`，只有当 `RoutesMiddleware ` 在中间件堆栈中时才可以工作。 关键字参数会覆盖路径变量或放在查询字符串上。

`url_for` 结合了 `url` 和 `url_current` 的行为。这是不推荐的，因为无名路由和路由内存具有相同的语法，这可能导致在某些情况下选择错误的路由。

以下是路由内存的示例：

```
m.connect("/archives/{year}/{month}/{day}", year=2004)

# Current URL is "/archives/2005/10/4".
# Routing variables are {"controller": "archives", "action": "view",
  "year": "2005", "month": "10", "day": "4"}

url.current(day=6)    =>  "/archives/2005/10/6"
url.current(month=4)  =>  "/archives/2005/4/4"
url.current()         =>  "/archives/2005/10/4"
```

可以通过 `map.explicit=True` 全局禁用路由内存。

### Generation-only routes (又名静态路由)

静态路由仅用于生成 - 不用于匹配 - 并且必须命名。要定义静态路由，请使用参数 `_static = True`。

此示例提供了一种方便的链接到搜索的方法：

```
map.connect("google", "http://google.com/", _static=True)
url("google", q="search term")  =>  "http://google.com/?q=search+term")
```

此示例生成Pylons公共目录中静态图像的URL。 Pylons以绕过路由的方式提供公共目录，所以没有理由匹配它下的URL。

```
map.connect("attachment", "/images/attachments/{category}/{id}.jpg",
    _static=True)
url("attachment", category="dogs", id="Mastiff") =>
    "/images/attachments/dogs/Mastiff.jpg"
```

从 routes 1.10开始，静态路由与常规路由完全相同，除了没有添加到 internal match table 中。 在以前版本中，它们不能包含路径变量，而且必须指向外部URL。

### Filter functions

过滤功能修改命名路由的生成方式。不要将其与功能条件混淆，该功能条件用于匹配。滤波器功能是相反的。

一个用例是当您有一个具有年，月和日属性的 `story` 对象时。 你不想在每个`url`调用中对这些属性进行硬编码，因为界面有可能会改变。 相反，您将故事作为伪参数传递，过滤器会生成实际的生成参数。 以下是一个例子：

```
class Story(object):
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @staticmethod
    def expand(kw):
        try:
            story = kw["story"]
        except KeyError:
            pass   # Don't modify dict if ``story`` key not present.
        else:
            # Set the actual generation args from the story.
            kw["year"] = story.year
            kw["month"] = story.month
            kw["day"] = story.day
        return kw

m.connect("archives", "/archives/{year}/{month}/{day}",
    controller="archives", action="view", _filter=Story.expand)

my_story = Story(2009, 1, 2)
url("archives", story=my_story)  =>  "/archives/2009/1/2"
```

`_filter` 参数可以是任何接受dict并返回dict的函数。 在这个例子中，我们使用了Story类的一个静态方法来将所有 story 关联在一起，但是您可能更喜欢使用独立的函数来保持路由相关的代码与模型的隔离。

### Generating URLs with subdomains

如果启用子域支持，并将`sub_domain` 作为参数传递给 `url_for`，则路由可确保生成的路由指向该子域。

```
# Enable subdomain support.
map.sub_domains = True

# Ignore the www subdomain.
map.sub_domains_ignore = "www"

map.connect("/users/{action}")

# Add a subdomain.
url_for(action="update", sub_domain="fred")  =>  "http://fred.example.com/users/update"

# Delete a subdomain.  Assume current URL is fred.example.com.
url_for(action="new", sub_domain=None)  =>  "http://example.com/users/new"
```

## RESTful services

路由可以轻松配置RESTful Web服务。`map.resource` 创建符合Atom发布协议的一组`add/modify/delete`路由。

A resource route addresses *members* in a *collection*, and the collection itself. 通常，一个集合是一个复数词，一个成员是相应的单数词。例如，考虑一个消息集合：

```
map.resource("message", "messages")

# The above command sets up several routes as if you had typed the
# following commands:
map.connect("messages", "/messages",
    controller="messages", action="create",
    conditions=dict(method=["POST"]))
map.connect("messages", "/messages",
    controller="messages", action="index",
    conditions=dict(method=["GET"]))
map.connect("formatted_messages", "/messages.{format}",
    controller="messages", action="index",
    conditions=dict(method=["GET"]))
map.connect("new_message", "/messages/new",
    controller="messages", action="new",
    conditions=dict(method=["GET"]))
map.connect("formatted_new_message", "/messages/new.{format}",
    controller="messages", action="new",
    conditions=dict(method=["GET"]))
map.connect("/messages/{id}",
    controller="messages", action="update",
    conditions=dict(method=["PUT"]))
map.connect("/messages/{id}",
    controller="messages", action="delete",
    conditions=dict(method=["DELETE"]))
map.connect("edit_message", "/messages/{id}/edit",
    controller="messages", action="edit",
    conditions=dict(method=["GET"]))
map.connect("formatted_edit_message", "/messages/{id}.{format}/edit",
    controller="messages", action="edit",
    conditions=dict(method=["GET"]))
map.connect("message", "/messages/{id}",
    controller="messages", action="show",
    conditions=dict(method=["GET"]))
map.connect("formatted_message", "/messages/{id}.{format}",
    controller="messages", action="show",
    conditions=dict(method=["GET"]))
```

这建立了以下惯例：

```
GET    /messages        => messages.index()    => url("messages")
POST   /messages        => messages.create()   => url("messages")
GET    /messages/new    => messages.new()      => url("new_message")
PUT    /messages/1      => messages.update(id) => url("message", id=1)
DELETE /messages/1      => messages.delete(id) => url("message", id=1)
GET    /messages/1      => messages.show(id)   => url("message", id=1)
GET    /messages/1/edit => messages.edit(id)   => url("edit_message", id=1)
```

**注意：**  Due to how Routes matches a list of URL’s, it has no inherent knowledge of a route being a **resource**. 因此，如果路由由于方法要求不满足而无法匹配，则404将像任何其他失败匹配路由一样返回。

因此，您 `GET` 集合以查看到成员的链接索引（`index`方法）。你 `GET` 一个成员看到它（`show`）。 您可以 `GET` `COLLECTION/new` 以获取一个新的邮件表单（`new`），您可以将其`POST` 到集合（`create`）。 您 `GET` `MEMBER/edit` 以获得编辑（`edit`），您将向该成员PUT（`update`） 。你 `DELETE` 该成员来删除它。 请注意，只有四个路由名称，因为多个操作在相同的URL上。

如果您不习惯使用Atom协议，此URL结构可能看起来很奇怪。 REST是一个模糊的术语，有些人认为这意味着适当的URL语法（每个组件包含右边的一个），其他人则认为这不意味着将ID放在查询参数中，而其他人认为这意味着使用除GET和POST之外的HTTP方法。`map.resource` 包含了这三个，但是对于不需要符合 Atom 规范的应用程序，或者更喜欢坚持使用GET和POST，这可能是过度的。`map.resource`的优点是，许多自动化工具和非浏览器代理将能够列出和修改您的资源，而无需您的任何编程。 但是，如果您喜欢使用更简单的 `add/modify/delete` 结构，则不必使用它。

HTML表单只能生成GET和POST请求。作为解决方法，如果POST请求包含 `_method` 参数，则路由中间件会将HTTP方法更改为任何参数指定的内容，就像首先请求的一样。 这种惯例在其他框架中变得越来越普遍。 如果您使用 `WebHelpers`，`WebHelpers`表单函数有一个方法参数，它自动设置`HTTP`方法和`_method`参数。

几条路由与包含 `format` 变量的相同路由配对。目的是允许用户通过文件名后缀获得不同的格式; 例如 `/messages/1.xml`。 这产生一个路由变量`xml`，如果它定义了一个正式的参数，它将在Pylons 中被传递给控制器动作。 在 generation 您可以传递 `format` 参数以生成具有该后缀的URL：


```
url("message", id=1, format="xml")  =>  "/messages/1.xml"
```

route 不识别任何特定的格式，或者知道哪些格式对您的应用有效。It merely passes the `format` attribute through if it appears.

*New in Routes 1.7.3: changed URL suffix from ”;edit” to “/edit”. 不允许在URL的路径部分中使用分号，除了定义路径参数，没人会使用。*

### Resource options

`map.resource`方法识别一些修改其行为的关键字参数：

* controller
 * 使用指定的控制器，而不是从集合名称中推导出来。
* collection
 * Additional URLs to allow for the collection. Example:
```
map.resource("message", "messages", collection={"rss": "GET"})
# "GET /message/rss"  =>  ``Messages.rss()``.
# Defines a named route "rss_messages".
```

* member
 * Additional URLs to allow for a member. Example:
```
map.resource('message', 'messages', member={'mark':'POST'})
# "POST /message/1/mark"  =>  ``Messages.mark(1)``
# also adds named route "mark_message"
```
 * This can be used to display a delete confirmation form:

```
map.resource("message", "messages", member={"ask_delete": "GET"}
# "GET /message/1/ask_delete"   =>   ``Messages.ask_delete(1)``.
# Also adds a named route "ask_delete_message".
```
* new
 * Additional URLs to allow for new-member functionality.
```
map.resource("message", "messages", new={"preview": "POST"})
# "POST /messages/new/preview"
```
* path_prefix
 * 为所有URL模式预先指定前缀。前缀可以包括路径变量。这主要用于在资源中嵌套资源。
* name_prefix
 * 将指定的字符串前缀到所有路由名称。这通常与`path_prefix`相结合来嵌套资源：
```
map.resource("message", "messages", controller="categories",
    path_prefix="/category/{category_id}",
    name_prefix="category_")
# GET /category/7/message/1
# Adds named route "category_message"
```
* parent_resource
 * 包含有关父资源的信息的dict，用于创建嵌套资源。 它应该包含父资源的`member_name`和`collection_name`。 该dict将通过相关的Route对象访问，该对象可以通过`request.environ["routes.route"]`在请求期间访问。
 * 如果提供了`parent_resource`并且`path_prefix`而没有提供，则`path_prefix`将从`parent_resource`生成为`<parent collection name>/:<parent member name>_id`。
 * 如果提供了`parent_resource`并且没有`name_prefix`，则`name_prefix`将从`parent_resource`生成为`<parent member name>_`。
 * 例如：

```
>>> m = Mapper()
>>> m.resource('location', 'locations',
...            parent_resource=dict(member_name='region',
...                                 collection_name='regions'))
>>> # path_prefix is "regions/:region_id"
>>> # name prefix is "region_"
>>> url('region_locations', region_id=13)
'/regions/13/locations'
>>> url('region_new_location', region_id=13)
'/regions/13/locations/new'
>>> url('region_location', region_id=13, id=60)
'/regions/13/locations/60'
>>> url('region_edit_location', region_id=13, id=60)
'/regions/13/locations/60/edit'

Overriding generated path_prefix:

>>> m = Mapper()
>>> m.resource('location', 'locations',
...            parent_resource=dict(member_name='region',
...                                 collection_name='regions'),
...            path_prefix='areas/:area_id')
>>> # name prefix is "region_"
>>> url('region_locations', area_id=51)
'/areas/51/locations'

Overriding generated name_prefix:

>>> m = Mapper()
>>> m.resource('location', 'locations',
...            parent_resource=dict(member_name='region',
...                                 collection_name='regions'),
...            name_prefix='')
>>> # path_prefix is "regions/:region_id"
>>> url('locations', region_id=51)
'/regions/51/locations'
```