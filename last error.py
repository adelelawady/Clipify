python ui/app_gradio.py

* Running on local URL:  http://127.0.0.1:7860
INFO:httpx:HTTP Request: GET http://127.0.0.1:7860/gradio_api/startup-events "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: HEAD http://127.0.0.1:7860/ "HTTP/1.1 200 OK"
* To create a public link, set `share=True` in `launch()`.
INFO:httpx:HTTP Request: GET https://api.gradio.app/pkg-version "HTTP/1.1 200 OK"
Traceback (most recent call last):
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/gradio/queueing.py", line 759, in process_events
    response = await route_utils.call_process_api(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/gradio/route_utils.py", line 354, in call_process_api
    output = await app.get_blocks().process_api(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/gradio/blocks.py", line 2116, in process_api
    result = await self.call_function(
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/gradio/blocks.py", line 1623, in call_function
    prediction = await anyio.to_thread.run_sync(  # type: ignore
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/anyio/to_thread.py", line 56, in run_sync
    return await get_async_backend().run_sync_in_worker_thread(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 2476, in run_sync_in_worker_thread
    return await future
           ^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 967, in run
    result = context.run(func, *args)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/venv/lib/python3.11/site-packages/gradio/utils.py", line 915, in wrapper
    response = f(*args, **kwargs)
               ^^^^^^^^^^^^^^^^^^
  File "/Users/diegomcolucci/Projects/Clipify/ui/app_gradio.py", line 79, in run_pipeline
    _, _, s, e = hit
    ^^^^^^^^^^
ValueError: not enough values to unpack (expected 4, got 2)
^CKeyboard interruption in main thread... closing server.
