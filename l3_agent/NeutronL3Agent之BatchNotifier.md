# Neutron L3 Agent 之 BatchNotifier

*neutron/notifiers/batch_notifiers.py*

## `class BatchNotifier(object)`

```
class BatchNotifier(object):
    def __init__(self, batch_interval, callback):
        self.pending_events = []
        self._waiting_to_send = False
        self.callback = callback
        self.batch_interval = batch_interval

    def queue_event(self, event):
        """Called to queue sending an event with the next batch of events.

        Sending events individually, as they occur, has been problematic as it
        can result in a flood of sends.  Previously, there was a loopingcall
        thread that would send batched events on a periodic interval.  However,
        maintaining a persistent thread in the loopingcall was also
        problematic.

        This replaces the loopingcall with a mechanism that creates a
        short-lived thread on demand when the first event is queued.  That
        thread will sleep once for the same batch_duration to allow other
        events to queue up in pending_events and then will send them when it
        wakes.

        If a thread is already alive and waiting, this call will simply queue
        the event and return leaving it up to the thread to send it.

        :param event: the event that occurred.
        """
        if not event:
            return

        self.pending_events.append(event)

        if self._waiting_to_send:
            return

        self._waiting_to_send = True

        def last_out_sends():
            eventlet.sleep(self.batch_interval)
            self._waiting_to_send = False
            self._notify()

        eventlet.spawn_n(last_out_sends)

    def _notify(self):
        if not self.pending_events:
            return

        batched_events = self.pending_events
        self.pending_events = []
        self.callback(batched_events)
```

架构上很简单，向 `pending_events` 然后调用回调函数 callback 去处理这些事件

