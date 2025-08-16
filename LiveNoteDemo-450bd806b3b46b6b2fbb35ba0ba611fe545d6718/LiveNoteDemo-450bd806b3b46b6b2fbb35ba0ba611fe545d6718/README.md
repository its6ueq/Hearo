gõ ``nvidia-smi`` để check xem cuda đang bản mấy 

xong vào đây tải pytorch https://pytorch.org/get-started/locally/ phiên bản phù hợp với gpu (<= phiên bản cuda)

nếu torch đã có r thì xóa mẹ đi ``pip uninstall torch torchvision torchaudio``

xong thì tải lại bằng cái web trên (chắc cũng 2 3GB đó )

xong thì tải mấy cái còn lại ``pip install -r requirements.txt``

setup cho nó có cái mic ảo nữa, window tìm ``change system sounds``, vào ``recording`` chỗ ``stereo mic`` ``enable`` nó lên, xong thì vào ``properties`` của ``stereo mic`` -> ``advanced ``-> bỏ tick 2 cái chỗ`` exclusive mode``

xong thì chạy code ``python -m livenote.main``

lặp từ vãi lồn

