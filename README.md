Mirror Control
-----

####  [中文版本](./README_CN.md)
---

#### Usage

* `!!mirror` Help messages and quick manage
* `!!mirror start <server_name>` Start mirror server (Including sync)
* `!!mirror restart <server_name>` Sync mirror server (Including sync)
* `!!mirror stop <server_name>` Stop mirror server
* `!!mirror sync <server_name>` Sync mirror server

`server_name` just like *default*.

#### Configuration file structure

Please modify the configuration file before you use it *After your first loading

\* means you you need to modify

```
config.json
	|- permission (int 1->4)
	|		|- start
	|		|- sync
	|		|- stop
	|		|- restart
	|
    |- this_server (str dir)
    |    	|- work_directory *
    |
    |- server
    		|- default * (just don't 'default', any other name you want is ok)
    		|		|- name * (anything you want, it is this server's nickname)
    		|		|- location * (absolute dir)
    		|		|- target_region_location * (its region file's dir)
    		|		|- command * (command to start.use 'start.bat' or 'sh start.sh')
    		|		|- rcon
    		|			|- enable * (boolean true)
    		|			|- port * 
    		|			|- passwd *
    		|
    		|- ...
```
