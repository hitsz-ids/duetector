# Open Count

In this section, we will show a user case of counting the number of `open` system call in a process.

## Prepare work dir

First, create a work dir in host machine, then we will mount it to kata container. This is for saving tracking data.

```bash
mkdir ./duetector-kata
```

## Start a container

We use docker to run `duetector` in a container, the details of how to run `duetector` in a container can be found in [run-with-docker](../../how-to/run-with-docker.md).

Alternatively, you can run `duetector` in a kata container, this gives you more isolation and security, see [run-with-kata-containers](../../how-to/run-with-kata-containers.md) for more details.

```bash
docker run -it --rm \
--privileged \
-p 8888:8888 \
-v /lib/modules:/lib/modules \
-e DUETECTOR_DAEMON_WORKDIR=/duetector-kata \
-v $(pwd)/duetector-kata:/duetector-kata \
-v /sys/kernel/debug:/sys/kernel/debug \
dataucon/duetector
```

Note:

- JupyterLab is the default entrypoint of `dataucon/duetector` as user application, see [Dockerfile](../../../docker/Dockerfile) and [start-script](../../../docker/start.sh) for change it by yourself.
- `--privileged` is required for `eBPF` to run properly.
- You can use `--entrypoint bash` to enter the container and run `duetector` manually.
  - In kata container, you need to mount debugfs manually: `mount -t debugfs debugfs /sys/kernel/debug`
- `/lib/modules` contains kernel modules, more details can be found in [run-with-docker](../../how-to/run-with-docker.md).

## Use JupyterLab to write some code

If you use JupyterLab as entrypoint, you can open `http://localhost:8888` in your browser, and use JupyterLab to write some code. In this case, you are user `application` with uid `9999` in the container.

> If you use `--entrypoint bash` to enter the container, you are user `root` in the container.
> Use `duectl-daemon start --loglevel=DEBUG` to start `duetector` daemon.
> Use `su - application` to switch to user `application` for following steps.

### 1. Let's write a file 100 times

```python
for i in range(100):
    with open("somefile", "a+") as f:
        f.write(str(i))
```

### 2. Let's read the file 1 times

```python
with open("somefile", "r") as f:
    print(f.read())
```

### 3. Remove the file

```ipython
!rm somefile
```

## Analyse the tracking data

In host machine, you can find the tracking data in `./duetector-kata` dir. By default, the tracking data is saved in `./duetector-kata/duetector-dbcollector.sqlite3`.

```bash
$sqlite3 ./duetector-kata/duetector-dbcollector.sqlite3
```

`Duector` will create a table for each tracer, and the table name is `tracer_name@tracer_id`. At the time I wrote this document, we have tow tracers: `OpenTracer` and `UnameTracer`, so we have two tables. The default tracer id is `hostname`.

```sql
sqlite> .tables
duetector_tracking:OpenTracer@a707be140e7d
duetector_tracking:UnameTracer@a707be140e7d
```

Now we count the number of `open` system call in the process we just created. Knowing that the `open` system call is traced by `OpenTracer`, we can query the `OpenTracer` table.

And the user id of the process is `9999`, so we can query the `uid` column.

```sql
sqlite> select count(*) from "duetector_tracking:OpenTracer@a707be140e7d" where uid=9999 and comm="python3" or comm="python";

136
```

Let's take a look at the tracking data.

```sql
sqlite> select * from "duetector_tracking:OpenTracer@a707be140e7d" where uid=9999 and comm="python3" or comm="python";

...
319|30458|9999|9999|25675549302584|python3||/home/application/k6p5uj2b|{}
320|30442|9999|9999|25675247583305|python3||/home/application/.ipython/profile_default/startup|{}
321|30458|9999|9999|25675548978328|python3||/tmp/5tt86b7v|{}
322|30463|9999|9999|25675198238774|python3||/home/application/.ipython/profile_default/history.sqlite|{}
323|30442|9999|9999|25675247495558|python3||/usr/local/etc/ipython/startup|{}
324|30442|9999|9999|25675247531323|python3||/usr/etc/ipython/startup|{}
509|30442|9999|9999|25679688669178|python3||somefile|{}
510|30442|9999|9999|25679689243005|python3||somefile|{}
511|30463|9999|9999|25679689332885|python3||/home/application/.ipython/profile_default/history.sqlite-journal|{}
512|30442|9999|9999|25679689641118|python3||somefile|{}
513|30442|9999|9999|25679689549933|python3||somefile|{}
514|30442|9999|9999|25679689706927|python3||somefile|{}
515|30442|9999|9999|25679689383977|python3||somefile|{}
516|30442|9999|9999|25679689962428|python3||somefile|{}
517|30442|9999|9999|25679690089247|python3||somefile|{}
518|30442|9999|9999|25679690151593|python3||somefile|{}
519|30442|9999|9999|25679690276725|python3||somefile|{}
520|30442|9999|9999|25679689169741|python3||somefile|{}
521|30442|9999|9999|25679690339139|python3||somefile|{}
522|30442|9999|9999|25679690403228|python3||somefile|{}
...
```

Because we are using `JupyterLab` as user application, which use ipython as default shell, so we can see the `python3` also access some tmp file and ipython config file.

Now we count the number of `open` system call for file `somefile`

```bash
sqlite> select count(*) from "duetector_tracking:OpenTracer@a707be140e7d" where uid=9999 and comm="python3" and fname="somefile";
101
```

**101** which is the same as the number of `open` system call we called in the python code:

- 100 times for writing
- 1 time for reading

Delete file will not increase the number of `open` system call of the file.

# Notes

- Docker(runc) container shares the same kernel with host machine, be careful with your tracking data, it may leak your privacy.

# More Cases

For more user cases for production, see [usercases](../README.md).
