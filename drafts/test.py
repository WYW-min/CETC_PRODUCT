from time import sleep
from rich.progress import track

for item in track(range(1000), description="处理数据中..."):
    # 你的业务逻辑
    sleep(0.01)
    print("数据处理完成！")
