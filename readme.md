# Automation for LakePlacid

## Usage
To use this, clone this repo into your application and from the root dir, run `bash instrument.sh [path to root directory of application code]`.

The following flags are available:
* `-n`: build the application without instrumenting it
* `-p`: print the generated commands, but don't execute them
* `-m`: rebuild the source code using its own build system to generate a new `compilation_info.json` file
* `-o [name of app to build]`: only build a certain app (ie. `-o redis-server`)
* `-t`: build the application with tracing instrumentation
* `-s`: build the application with specialization

As an example, the following would be the steps required to profile and specialize `memcached`:
0. Add `__trace_begin()` and `__trace_end`.
1. `cd memcached`
2. `git clone git@github.com:katm10/LakePlacid-automation.git instrumentation`
3. `cd instrumentation`
4. `bash instrument.sh -m -t ..` This will make the application, using the original build steps, and generate the corresponding `compilation_info.json`. It will then build the application with tracing instrumentation. Generated files will be stored in `memcached/instrumentation/extract_trace`. This may take some time, as it must compile `memcached` twice. 

At this point, the file structure should look like (numerous folders/files omitted for brevity):

```
|-- memcached
|  |-- instrumentation
|  |  |-- extract_trace
|  |  |  |-- ASSEMBLE
|  |  |  |-- COMPILE
|  |  |  |-- INSTRUMENT
|  |  |  |-- LINK
|  |  |  |  |-- memcached
|  |  |  |  |-- memcached-debug
|  |  |  |  |-- sizes
|  |  |  |  |-- testapp
|  |  |  |  |__ timedrun
|  |  |  |-- PREPROCESS
|  |  |  |-- UNSPECIFIED
|__|__|__|__ UNUSED
```

6. Run your application to generate traces for it. In this case, I run
```
cd ..
mkdir traces
./instrumentation/extract_trace/LINK/memcached -U 11211 -l localhost

[In another terminal, send some test GET, SET, UPDATE, etc requests]
```
This will generate a set of `tracexxxxxxxx.txt` within `traces/`.

7. TODO: Generate `manifest.txt`

8. Finally, to generate specialized code, run `bash instrument.sh -s ..`
