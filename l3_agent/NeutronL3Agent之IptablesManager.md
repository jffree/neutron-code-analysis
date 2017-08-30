# Neutron L3 Agent 之 IptablesManager

*neutron/agent/linux/iptables_manager.py*

## `class IptablesManager(object)`

对 iptables 操作的封装

```
    def __init__(self, _execute=None, state_less=False, use_ipv6=False,
                 namespace=None, binary_name=binary_name):
        if _execute:
            self.execute = _execute
        else:
            self.execute = linux_utils.execute

        self.use_ipv6 = use_ipv6
        self.namespace = namespace
        self.iptables_apply_deferred = False
        self.wrap_name = binary_name[:16]

        self.ipv4 = {'filter': IptablesTable(binary_name=self.wrap_name)}
        self.ipv6 = {'filter': IptablesTable(binary_name=self.wrap_name)}

        # Add a neutron-filter-top chain. It's intended to be shared
        # among the various neutron components. It sits at the very top
        # of FORWARD and OUTPUT.
        for tables in [self.ipv4, self.ipv6]:
            tables['filter'].add_chain('neutron-filter-top', wrap=False)
            tables['filter'].add_rule('FORWARD', '-j neutron-filter-top',
                                      wrap=False, top=True)
            tables['filter'].add_rule('OUTPUT', '-j neutron-filter-top',
                                      wrap=False, top=True)

            tables['filter'].add_chain('local')
            tables['filter'].add_rule('neutron-filter-top', '-j $local',
                                      wrap=False)

        # Wrap the built-in chains
        builtin_chains = {4: {'filter': ['INPUT', 'OUTPUT', 'FORWARD']},
                          6: {'filter': ['INPUT', 'OUTPUT', 'FORWARD']}}

        if not state_less:
            self.ipv4.update(
                {'mangle': IptablesTable(binary_name=self.wrap_name)})
            builtin_chains[4].update(
                {'mangle': ['PREROUTING', 'INPUT', 'FORWARD', 'OUTPUT',
                            'POSTROUTING']})
            self.ipv6.update(
                {'mangle': IptablesTable(binary_name=self.wrap_name)})
            builtin_chains[6].update(
                {'mangle': ['PREROUTING', 'INPUT', 'FORWARD', 'OUTPUT',
                            'POSTROUTING']})
            self.ipv4.update(
                {'nat': IptablesTable(binary_name=self.wrap_name)})
            builtin_chains[4].update({'nat': ['PREROUTING',
                                      'OUTPUT', 'POSTROUTING']})

        self.ipv4.update({'raw': IptablesTable(binary_name=self.wrap_name)})
        builtin_chains[4].update({'raw': ['PREROUTING', 'OUTPUT']})
        self.ipv6.update({'raw': IptablesTable(binary_name=self.wrap_name)})
        builtin_chains[6].update({'raw': ['PREROUTING', 'OUTPUT']})

        for ip_version in builtin_chains:
            if ip_version == 4:
                tables = self.ipv4
            elif ip_version == 6:
                tables = self.ipv6

            for table, chains in six.iteritems(builtin_chains[ip_version]):
                for chain in chains:
                    tables[table].add_chain(chain)
                    tables[table].add_rule(chain, '-j $%s' %
                                           (chain), wrap=False)

        if not state_less:
            # Add a neutron-postrouting-bottom chain. It's intended to be
            # shared among the various neutron components. We set it as the
            # last chain of POSTROUTING chain.
            self.ipv4['nat'].add_chain('neutron-postrouting-bottom',
                                       wrap=False)
            self.ipv4['nat'].add_rule('POSTROUTING',
                                      '-j neutron-postrouting-bottom',
                                      wrap=False)

            # We add a snat chain to the shared neutron-postrouting-bottom
            # chain so that it's applied last.
            self.ipv4['nat'].add_chain('snat')
            self.ipv4['nat'].add_rule('neutron-postrouting-bottom',
                                      '-j $snat', wrap=False,
                                      comment=ic.SNAT_OUT)

            # And then we add a float-snat chain and jump to first thing in
            # the snat chain.
            self.ipv4['nat'].add_chain('float-snat')
            self.ipv4['nat'].add_rule('snat', '-j $float-snat')

            # Add a mark chain to mangle PREROUTING chain. It is used to
            # identify ingress packets from a certain interface.
            self.ipv4['mangle'].add_chain('mark')
            self.ipv4['mangle'].add_rule('PREROUTING', '-j $mark')
```

*又是一个巨大无比的 init 方法*

* 参数说明
 1. `_execute` : 执行 iptables 命令的方法，默认为 `linux_utils.execute`
 2. `state_less` : 
 3. `use_ipv6` : 是否使用 ipv6 地址
 4. `namespace` : 执行该命令的命名空间
 5. `binary_name` : 当前运行程序的名称

```
def get_binary_name():
    """Grab the name of the binary we're running in."""
    return os.path.basename(sys.argv[0])[:16].replace(' ', '_')

binary_name = get_binary_name()
```

对于 l3 agent 来说，这里获得的是 `neutron-l3-agent`

1. 分别为 ipv4 和 ipv6 建立 filter 表
2. 分别为 ipv4 和 ipv6 的 filter 表建立做如下操作：
 1. 增加 `neutron-filter-top` chain
 2. 增加 rule，将 `FORWARD` chain 转向 `neutron-filter-top` chain 去处理
 3. 增加 rule，将 `OUTPUT` chain 转向 `neutron-filter-top` chain 去处理
 4. 增加 local chain
 5. 增加 rule，将 `neutron-filter-top` chain 转向 `local` chain 去处理
3. 若 state_less 为 false：
 1. 为 ipv4 和 ipv6 增加 mangle 表
 2. 为 ipv4 增加 nat 表
4. 为 ipv4 和 ipv6 增加 raw 表
5. 为上面增加的这些表，添加上其本身内建的 chain
6. 将所有内建的 chain，都转发的与之对应的包装后的 chain 去处理（例如：`-A PREROUTING -j neutron-l3-agent-PREROUTING`）
7. 若 state_less 为 false：
 1. 为 ipv4 的 nat 表增加 `neutron-postrouting-bottom` chain
 2. 将 nat 表上的 `POSTROUTING` 转发到 `neutron-postrouting-bottom` 上去处理 
 3. 为 ipv4 的 nat 表增加 `snat` chain
 4. 将 nat 表上的 `neutron-postrouting-bottom` 转发到 `$snat` 上去处理 
 5. 为 ipv4 的 nat 表增加 `float-snat` chain
 6. 将 nat 表上的 `snat` 转发到 `$float-snat` 上去处理 
 7. 为 ipv4 的 nat 表增加 `mark` chain
 6. 将 nat 表上的 `PREROUTING` 转发到 `$mark` 上去处理 

### `def get_tables(self, ip_version)`

获取对应 ip 版本的 iptables table 记录

### `def get_chain(self, table, chain, ip_version=4, wrap=True)`

1. 调用 `get_tables` 获取对应 ip 版本的 table
2. 调用 `IptablesTable._get_chain_rules` 获取对应的 chain 上的 rule

### `def is_chain_empty(self, table, chain, ip_version=4, wrap=True)`

判断一个 chain 是否是空的

### `def defer_apply(self)`

延迟执行 iptables 命令

### `def defer_apply_on(self)`

```
    def defer_apply_on(self):
        self.iptables_apply_deferred = True
```

### `def defer_apply_off(self)`

```
    def defer_apply_off(self):
        self.iptables_apply_deferred = False
        self._apply()
```

### `def apply(self)`

若 iptables 命令执行不需要延迟，则调用 `_apply` 执行命令

### `def _apply(self)`

1. 调用 `_apply_synchronized` 执行 iptables 命令
2. 返回执行结果

### `def _apply_synchronized(self)`

*这里只以 Ipv4 来说明*

1. 调用 iptables-save 命令，获取其输出
2. 对于 ipv4 的所有 table：
 1. 调用 `_find_table` 找到 table 的当前所有规则
 2. 调用 `_modify_rules` 找到当前 table 需要设定的 rule 和 Chain
 3. 调用 `_generate_path_between_rules` 生成 iptables 应该执行的规则命令
 4. 执行 iptables-restore 命令保存那些 rule

### `def _find_table(self, lines, table_name)`

lines 是 iptables-save 的返回值。

找到 table 的当前所有 rule

### `def _modify_rules(self, current_lines, table, table_name)`

1. 获取当前不属于 neutron 的 rule 
2. 获得当前 neutron 可操作的 chain
3. 对于 table 中的所有 rule：
 1. 再次过滤掉那些不属于 neutron 的 rule
 2. 获取位于 chain top 位置的 rule 和其余的 rule
4. 调用 `_find_rules_index` 找到在非 Neutron chain 的个数，并在这些非 neutron chain 后插入 neutron chain
5. 定义 `_weed_out_removes` 内方法，检查一个 rule 或 chain 是否已经被设定删除
6. 定义 `_weed_out_duplicates` 内方法，查找到是否有重复的 chain 出现
7. 去除掉重复的 rule 或者 chain，去除掉那些被设定删除的 rule 或 chain
8. 情况 `remove_chains` 和 `remove_rules` 记录
9. 返回现在需要设定的 iptables rule

### `def _find_rules_index(self, lines)`

调用 iptables-save 后，mangle 表的记录如下：

```
*mangle
:PREROUTING ACCEPT [15528745:7936577261]
:INPUT ACCEPT [15297003:7922115195]
:FORWARD ACCEPT [193:19276]
:OUTPUT ACCEPT [15256693:7563536925]
:POSTROUTING ACCEPT [15256827:7563564011]
:nova-api-POSTROUTING - [0:0]
-A POSTROUTING -j nova-api-POSTROUTING
-A POSTROUTING -o virbr0 -p udp -m udp --dport 68 -j CHECKSUM --checksum-fill
COMMIT
```

lines 是非 neutron iptables rule 的记录。
找到这些记录中非 neutron iptables chain 的个数

### `def get_traffic_counters(self, chain, wrap=True, zero=False)`

1. 调用 `_get_traffic_counters_cmd_tables` 构造包含 table 的 iptables 命令
2. 直接执行 iptables 命令，通过其结果获取 `pktes` 和 `bytes`（包个数和字节个数）

```
[root@node1 ~]# iptables -t filter -L INPUT -n -v -x
Chain INPUT (policy ACCEPT 19698 packets, 1971214 bytes)
    pkts      bytes target     prot opt in     out     source               destination         
15371421 7951899279 neutron-openvswi-INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0           
15377604 7953969385 nova-api-INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0           
       0        0 ACCEPT     udp  --  virbr0 *       0.0.0.0/0            0.0.0.0/0            udp dpt:53
       0        0 ACCEPT     tcp  --  virbr0 *       0.0.0.0/0            0.0.0.0/0            tcp dpt:53
       0        0 ACCEPT     udp  --  virbr0 *       0.0.0.0/0            0.0.0.0/0            udp dpt:67
       0        0 ACCEPT     tcp  --  virbr0 *       0.0.0.0/0            0.0.0.0/0            tcp dpt:67
   86858 15477542 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:9696
   31624 35937251 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:9292
      35     3128 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:5000
19994218 10572694002 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
       7      588 ACCEPT     icmp --  *      *       0.0.0.0/0            0.0.0.0/0           
   36556  2189927 ACCEPT     all  --  lo     *       0.0.0.0/0            0.0.0.0/0           
      40     2252 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            state NEW tcp dpt:22
    5348   310680 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:80
      24     1668 ACCEPT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:80
     383    22644 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:5672
```

### `def _get_traffic_counters_cmd_tables(self, chain, wrap=True)`

构造 chain 所在 table 的命令（iptables -t filter）

## `def _generate_path_between_rules(old_rules, new_rules)`

1. 调用 `_get_rules_by_chain` 将 old 和 new rule 按照 chain 进行分类
2. 获取新增的 chain
3. 获取保持不变的 chain，并且调用 `_generate_chain_diff_iptables_commands` 确定这些 chain 上那些 rule 该删除，那些 rule 该插入
4. 获取应该删除的 chain

## `def _get_rules_by_chain(rules)`

将 rules 记录按照所属 chain 进行分类

## `def _generate_chain_diff_iptables_commands(chain, old_chain_rules, new_chain_rules)`

对比 chain 上的新旧 rule，确定那些 rule 该删除，那些 rule 该插入


## `class IptablesTable(object)`

```
    def __init__(self, binary_name=binary_name):
        self.rules = []
        self.remove_rules = []
        self.chains = set()
        self.unwrapped_chains = set()
        self.remove_chains = set()
        self.wrap_name = binary_name[:16]
```

当前 table 中的 rule
当前 table 中原始 Chain 上被删除的 rule
当前 table 中的包装后的 chain
当前 table 中的原始 Chain
当前 table 中被移除的 chain
当前 table chain 的包装名称

### `def add_chain(self, name, wrap=True)`

在当前的 table 中增加一个 chain

`wrap` 为 True 的情况下，会将 binary_name 放在 chain name 的前面（例如：`neutron-openvswi-OUTPUT`）

### `def _select_chain_set(self, wrap)`

返回当前表的 chain

### `def remove_chain(self, name, wrap=True)`

从该 table 中移除该 chain，同时移除该 chain 所包含的 rule

### `def _wrap_target_chain(self, s, wrap)`

若 s 以 `$` 开头，则意味着该选项是一个 target chain，且该 chain 将会以 `wrap_name` 开头（例如：`neutron-openvswi-OUTPUT`）

### `def add_rule(self, chain, rule, wrap=True, top=False, tag=None, comment=None)`

在该 chain 上增加一个 rule，该 rule 用 `IptablesRule` 表示

### `def remove_rule(self, chain, rule, wrap=True, top=False, comment=None)`

在该 chain 上移除一个 rule

### `def _get_chain_rules(self, chain, wrap)`

获取该 chain 上的 rule

### `def empty_chain(self, chain, wrap=True)`

清空一条 chain 上的 rule

### `def clear_rules_by_tag(self, tag)`

清空带有 tag 的 rule

## `class IptablesRule(object)`

```
    def __init__(self, chain, rule, wrap=True, top=False,
                 binary_name=binary_name, tag=None, comment=None):
        self.chain = get_chain_name(chain, wrap)
        self.rule = rule
        self.wrap = wrap
        self.top = top
        self.wrap_name = binary_name[:16]
        self.tag = tag
        self.comment = comment
```

1. 该 rule 所在的 chain
2. 该 rule 所在的 chain 是否被封装过
3. 该 rule 是否未与 chain 的 top
4. 该 rule 所在 chain 的封装名称
5. 该 rule 的 tag
6. 该 rule 的 comment

### `def __eq__(self, other)`

判断当前 rule 是否与另一个 rule 相等

### `def __ne__(self, other)`

判断当前 rule 与另一个 rule 是否是同一个

### `def __str__(self)`

该 rule 的描述