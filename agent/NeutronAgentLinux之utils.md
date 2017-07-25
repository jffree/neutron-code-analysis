# Neutron Agent Linux utils

*neutron/agent/linux/utils.py*

## `def addl_env_args(addl_env)`

解析附加的环境变量

## `def create_process(cmd, run_as_root=False, addl_env=None)`

利用 `subprocess.Popen` 创建一个子进程。

若是 run_as_root 为 True，则使用 `sudo` 命令。

返回执行的命令，已经子进程的 `Popen` 对象

## `def execute_rootwrap_daemon(cmd, process_input, addl_env)`

以 `RootwrapDaemonHelper` 包装子进程，调用 `RootwrapDaemonHelper.execute` 来执行子进程


## `def execute(cmd, process_input=None, addl_env=None, check_exit_code=True, return_stderr=False, log_fail_as_error=True, extra_ok_codes=None, run_as_root=False)`

* 参数说明：
 * `cmd` : 需要执行的命令
 * `process_input`：准备输入给子进程的数据（利用 `Popen.communicate` 方法实现）
 * `run_as_root` : 是否以 root 的身份执行
 * `addl_env` : 在执行的命令前附加的环境变量（例如：`{'a':1, 'b':2}`）
 * `extra_ok_codes`：子进程执行正确时的可能返回值（默认为 0）
 * `log_fail_as_error` : 当子进程执行出错时，是否在 log 中记录错误
 * `check_exit_code`：当子进程执行出错时，是否引发异常，并在异常中保存子进程的返回值
 * `return_stderr`：是否返回子进程在标准错误上的输出

`root_helper_daemon`：（在子进程需要长期运行的时候，建议将此开关打开）

1. 在需要 root 权限时：
 1. 若是 `root_helper_daemon` 为 True，则调用 `execute_rootwrap_daemon` 来启动子进程
 2. 若是 `root_helper_daemon` 为 False，则调用 `create_process`  来启动子进程

## `def load_interface_driver(conf)`

根据配置信息加载接口驱动。在 `setup.cfg` 中，我们可以看到接口驱动有一下几种类型：

```
neutron.interface_drivers =
    ivs = neutron.agent.linux.interface:IVSInterfaceDriver
    linuxbridge = neutron.agent.linux.interface:BridgeInterfaceDriver
    null = neutron.agent.linux.interface:NullDriver
    openvswitch = neutron.agent.linux.interface:OVSInterfaceDriver
```







