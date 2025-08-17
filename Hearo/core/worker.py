# file: livenote/core/worker.py

import sys
import traceback
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    
    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc())
    
    result
        `object` data returned from processing, anything
    """
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class Worker(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        print(f"✅ [Worker] Bắt đầu chạy tác vụ cho: {self.fn.__name__} với args={self.args}")
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            # In lỗi ra đây để chắc chắn chúng ta thấy nó
            print(f"❌ [Worker] GẶP LỖI NGHIÊM TRỌNG: {e}")
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            print(f"✅ [Worker] Tác vụ hoàn thành. Đang gửi tín hiệu kết quả...")
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            print(f"✅ [Worker] Đã xong. Gửi tín hiệu 'finished'.")
            self.signals.finished.emit()  # Done