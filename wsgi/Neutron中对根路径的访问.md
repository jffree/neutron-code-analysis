# neutron 中对 `/` 的访问

## 实验

```
curl -s -X GET http://172.16.100.106:9696/ -H 'Content-Type: application/json' -H 'X-Auth-Token: faab008a91a6410c92484656c318c5d4' | jq
```

响应：

```
{
  "versions": [
    {
      "status": "CURRENT",
      "id": "v2.0",
      "links": [
        {
          "href": "http://172.16.100.106:9696/v2.0",
          "rel": "self"
        }
      ]
    }
  ]
}
```

## api-paste.ini

```
[composite:neutron]
use = egg:Paste#urlmap
/: neutronversions_composite
/v2.0: neutronapi_v2_0

[composite:neutronversions_composite]
use = call:neutron.auth:pipeline_factory
noauth = cors http_proxy_to_wsgi neutronversions
keystone = cors http_proxy_to_wsgi neutronversions

[app:neutronversions]
paste.app_factory = neutron.api.versions:Versions.factory
```

## `class Versions(object)`

*neutron/api/version.py*

响应对 `/` 访问。

## `class ViewBuilder(object)`

构造对 `/` 相应的 body。