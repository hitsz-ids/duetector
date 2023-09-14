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
-p 8120:8120 \
-v /lib/modules:/lib/modules \
-e DUETECTOR_DAEMON_WORKDIR=/duetector-kata \
-e DUETECTOR_SERVER_DAEMON_WORKDIR=/duetector-kata \
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
- `8888` is the port of JupyterLab, `8120` is the port of duetector server. Access `http://localhost:8888` in your browser to use JupyterLab, and access `http://localhost:8120/docs` to see the API docs of duetector server.

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
cd ./duetector-kata/
python
```

We will create a table for each tracer, and the table name is `tracer_name@tracer_id`. At the time I wrote this document, we have tow tracers: `OpenTracer` and `UnameTracer`, so we have two tables. The default tracer id is `hostname`.

```python
>>> from duetector.analyzer.db import DBAnalyzer
>>> analyzer = DBAnalyzer()
>>> analyzer.brief()

Available tracers: {'UnameTracer', 'OpenTracer', 'TcpconnectTracer', 'CloneTracer'}
Available collector ids: {'850732468c3e'}
briefs:
----------------
CloneTracer@850732468c3e with 63 records
from 2023-09-12 08:34:13.101249 to 2023-09-12 08:34:51.662181
available fields: [pid: int, uid: int, gid: int, dt: datetime, comm: str, cwd: str, fname: str, extended: dict]
----------------

----------------
OpenTracer@850732468c3e with 492 records
from 2023-09-12 08:34:17.274420 to 2023-09-12 08:34:52.286982
available fields: [pid: int, uid: int, gid: int, dt: datetime, comm: str, cwd: str, fname: str, extended: dict]
----------------

----------------
TcpconnectTracer@850732468c3e with 97 records
from 2023-09-12 08:34:16.018427 to 2023-09-12 08:34:51.747149
available fields: [pid: int, uid: int, gid: int, dt: datetime, comm: str, cwd: str, fname: str, extended: dict]
----------------

----------------
UnameTracer@850732468c3e with 1 records
from None to None
available fields: [pid: int, uid: int, gid: int, dt: datetime, comm: str, cwd: str, fname: str, extended: dict]
----------------
```

Now we count the number of `open` system call in the process we just created. Knowing that the `open` system call is traced by `OpenTracer`, we can query the `OpenTracer` table.

And the user id of the process is `9999`, so we can query the `uid` column.

```python
>>> query_args = {
  "comm": "python3",
  "uid": 9999
}
>>> len(analyzer.query(tracers=["OpenTracer"], where=query_args))
126
```

Let's take a look at the tracking data.

```python
>>> analyzer.query(tracers=["OpenTracer"], where=query_args, start=15, limit=5)
[Tracking(tracer='OpenTracer', pid=671246, uid=9999, gid=9999, comm='python3', cwd=None, fname='/tmp/5gc4mhvd', dt=datetime.datetime(2023, 9, 12, 8, 34, 41, 189646), extended={}),
 Tracking(tracer='OpenTracer', pid=671250, uid=9999, gid=9999, comm='python3', cwd=None, fname='/home/application/.ipython/profile_default/history.sqlite-journal', dt=datetime.datetime(2023, 9, 12, 8, 34, 41, 190227), extended={}),
 Tracking(tracer='OpenTracer', pid=671228, uid=9999, gid=9999, comm='python3', cwd=None, fname='somefile', dt=datetime.datetime(2023, 9, 12, 8, 34, 41, 191668), extended={}),
 Tracking(tracer='OpenTracer', pid=671228, uid=9999, gid=9999, comm='python3', cwd=None, fname='somefile', dt=datetime.datetime(2023, 9, 12, 8, 34, 41, 195397), extended={}),
 Tracking(tracer='OpenTracer', pid=671228, uid=9999, gid=9999, comm='python3', cwd=None, fname='somefile', dt=datetime.datetime(2023, 9, 12, 8, 34, 41, 195497), extended={})]
```

Because we are using `JupyterLab` as user application, which use ipython as default shell, so we can see the `python3` also access some tmp file and ipython config file.

Now we count the number of `open` system call for file `somefile`

```python
>>> query_args = {
  "comm": "python3",
  "uid": 9999,
  "fname": "somefile"
}
>>> len(analyzer.query(tracers=["OpenTracer"], where=query_args))
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
