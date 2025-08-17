# file: livenote/core/worker.py

import sys
import traceback
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        print(f"[Worker] Bắt đầu chạy tác vụ cho: {self.fn.__name__} với args={self.args}")
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            print(f"[Worker] GẶP LỖI NGHIÊM TRỌNG: {e}")
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            print(f"[Worker] Tác vụ hoàn thành. Đang gửi tín hiệu kết quả...")
            self.signals.result.emit(result) 
        finally:
            print(f"[Worker] Đã xong. Gửi tín hiệu 'finished'.")
            self.signals.finished.emit() 